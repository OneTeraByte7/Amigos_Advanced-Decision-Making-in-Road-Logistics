"""
cache_manager.py
────────────────
Intelligent caching system for API responses, route calculations,
and frequently accessed data to improve performance.
"""

import time
import hashlib
import json
from typing import Any, Optional, Dict, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pickle


@dataclass
class CacheEntry:
    """Single cache entry"""
    key: str
    value: Any
    created_at: float
    expires_at: float
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    size_bytes: int = 0


class CacheManager:
    """
    Intelligent caching system with TTL, LRU eviction, and statistics
    """
    
    def __init__(
        self,
        max_size_mb: float = 100.0,
        default_ttl_seconds: int = 3600
    ):
        """
        Initialize cache manager
        
        Args:
            max_size_mb: Maximum cache size in megabytes
            default_ttl_seconds: Default time-to-live for cache entries
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.default_ttl = default_ttl_seconds
        self.current_size_bytes = 0
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        
        # Check expiration
        if time.time() > entry.expires_at:
            self._remove_entry(key)
            self.expirations += 1
            self.misses += 1
            return None
        
        # Update access statistics
        entry.access_count += 1
        entry.last_accessed = time.time()
        self.hits += 1
        
        return entry.value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live (uses default if None)
        
        Returns:
            True if successfully cached
        """
        ttl = ttl_seconds or self.default_ttl
        
        # Calculate size
        try:
            size = len(pickle.dumps(value))
        except Exception:
            size = 1024  # Default size estimate
        
        # Check if we need to evict entries
        while self.current_size_bytes + size > self.max_size_bytes:
            if not self._evict_lru():
                return False  # Cache full, cannot evict
        
        # Remove old entry if exists
        if key in self.cache:
            self._remove_entry(key)
        
        # Create new entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            expires_at=time.time() + ttl,
            size_bytes=size
        )
        
        self.cache[key] = entry
        self.current_size_bytes += size
        
        return True
    
    def delete(self, key: str) -> bool:
        """
        Delete entry from cache
        
        Args:
            key: Cache key
        
        Returns:
            True if entry existed and was deleted
        """
        if key in self.cache:
            self._remove_entry(key)
            return True
        return False
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.current_size_bytes = 0
    
    def _remove_entry(self, key: str):
        """Remove entry and update size"""
        if key in self.cache:
            entry = self.cache[key]
            self.current_size_bytes -= entry.size_bytes
            del self.cache[key]
    
    def _evict_lru(self) -> bool:
        """
        Evict least recently used entry
        
        Returns:
            True if an entry was evicted
        """
        if not self.cache:
            return False
        
        # Find LRU entry
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed
        )
        
        self._remove_entry(lru_key)
        self.evictions += 1
        return True
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry.expires_at
        ]
        
        for key in expired_keys:
            self._remove_entry(key)
            self.expirations += 1
        
        return len(expired_keys)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary of cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'entries': len(self.cache),
            'size_mb': self.current_size_bytes / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'utilization_percent': (self.current_size_bytes / self.max_size_bytes * 100),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate_percent': hit_rate,
            'evictions': self.evictions,
            'expirations': self.expirations,
            'total_requests': total_requests
        }
    
    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a cache entry
        
        Args:
            key: Cache key
        
        Returns:
            Entry information or None
        """
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        age_seconds = time.time() - entry.created_at
        ttl_remaining = entry.expires_at - time.time()
        
        return {
            'key': key,
            'size_bytes': entry.size_bytes,
            'age_seconds': age_seconds,
            'ttl_remaining_seconds': max(0, ttl_remaining),
            'access_count': entry.access_count,
            'last_accessed': datetime.fromtimestamp(entry.last_accessed).isoformat()
        }


class RouteCacheManager:
    """Specialized cache for route calculations"""
    
    def __init__(self):
        self.cache = CacheManager(max_size_mb=50.0, default_ttl_seconds=3600)
    
    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached route
        
        Returns:
            Cached route data or None
        """
        key = self._make_route_key(origin_lat, origin_lng, dest_lat, dest_lng)
        return self.cache.get(key)
    
    def cache_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        route_data: Dict[str, Any],
        ttl_seconds: int = 7200  # 2 hours
    ):
        """Cache route data"""
        key = self._make_route_key(origin_lat, origin_lng, dest_lat, dest_lng)
        self.cache.set(key, route_data, ttl_seconds)
    
    @staticmethod
    def _make_route_key(
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> str:
        """Generate cache key for route"""
        # Round to 4 decimal places (~11m precision)
        coords = f"{origin_lat:.4f},{origin_lng:.4f}-{dest_lat:.4f},{dest_lng:.4f}"
        return f"route:{coords}"


class APIResponseCache:
    """Cache for API responses"""
    
    def __init__(self):
        self.cache = CacheManager(max_size_mb=30.0, default_ttl_seconds=300)
    
    def get_response(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Get cached API response
        
        Args:
            endpoint: API endpoint
            params: Request parameters
        
        Returns:
            Cached response or None
        """
        key = self._make_api_key(endpoint, params)
        return self.cache.get(key)
    
    def cache_response(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]],
        response: Any,
        ttl_seconds: int = 300
    ):
        """Cache API response"""
        key = self._make_api_key(endpoint, params)
        self.cache.set(key, response, ttl_seconds)
    
    @staticmethod
    def _make_api_key(
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate cache key for API call"""
        if params:
            # Sort params for consistent key
            param_str = json.dumps(params, sort_keys=True)
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            return f"api:{endpoint}:{param_hash}"
        return f"api:{endpoint}"


def cache_result(
    ttl_seconds: int = 3600,
    cache_manager: Optional[CacheManager] = None
):
    """
    Decorator to cache function results
    
    Args:
        ttl_seconds: Cache TTL
        cache_manager: Optional cache manager instance
    
    Usage:
        @cache_result(ttl_seconds=600)
        def expensive_function(arg1, arg2):
            # ... expensive computation
            return result
    """
    if cache_manager is None:
        cache_manager = CacheManager()
    
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache_manager.get(key)
            if cached_result is not None:
                return cached_result
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Cache result
            cache_manager.set(key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


class DataCache:
    """
    General-purpose data cache with namespaces
    """
    
    def __init__(self):
        self.caches: Dict[str, CacheManager] = {}
        self.default_cache = CacheManager()
    
    def get_cache(self, namespace: str = "default") -> CacheManager:
        """
        Get or create cache for namespace
        
        Args:
            namespace: Cache namespace
        
        Returns:
            CacheManager instance
        """
        if namespace == "default":
            return self.default_cache
        
        if namespace not in self.caches:
            self.caches[namespace] = CacheManager()
        
        return self.caches[namespace]
    
    def clear_namespace(self, namespace: str):
        """Clear all entries in a namespace"""
        if namespace in self.caches:
            self.caches[namespace].clear()
    
    def clear_all(self):
        """Clear all caches"""
        self.default_cache.clear()
        for cache in self.caches.values():
            cache.clear()
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches"""
        stats = {
            'default': self.default_cache.get_statistics()
        }
        
        for namespace, cache in self.caches.items():
            stats[namespace] = cache.get_statistics()
        
        return stats


# Global cache instances
route_cache = RouteCacheManager()
api_cache = APIResponseCache()
data_cache = DataCache()


__all__ = [
    'CacheManager',
    'RouteCacheManager',
    'APIResponseCache',
    'DataCache',
    'cache_result',
    'route_cache',
    'api_cache',
    'data_cache'
]
