import requests
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class RouteInfo:
    coordinates: List[List[float]]  # Changed from Tuple to List: [[lat, lng], ...]
    distance_km: float
    duration_seconds: float

class OSRMClient:
    """Client for OSRM routing API - FREE, no API key needed"""
    
    def __init__(self):
        self.base_url = "https://router.project-osrm.org/route/v1/driving"
    
    def get_route(self, start_lat: float, start_lng: float, 
                  end_lat: float, end_lng: float) -> Optional[RouteInfo]:
        """
        Get real road route between two points
        
        Args:
            start_lat, start_lng: Starting coordinates
            end_lat, end_lng: Destination coordinates
            
        Returns:
            RouteInfo with coordinates along actual roads, or None if failed
        """
        try:
            # OSRM uses lng,lat format (not lat,lng)
            url = f"{self.base_url}/{start_lng},{start_lat};{end_lng},{end_lat}"
            params = {
                'overview': 'full',
                'geometries': 'geojson'
            }
            
            print(f"   📡 OSRM URL: {url}")
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('routes') or len(data['routes']) == 0:
                print(f"   ⚠️ No routes found in OSRM response")
                return None
            
            route = data['routes'][0]
            
            # Convert [lng, lat] to [lat, lng] lists (not tuples)
            coordinates = [
                [coord[1], coord[0]]  # Swap lng,lat to lat,lng, return as list
                for coord in route['geometry']['coordinates']
            ]
            
            print(f"   ✅ Route parsed: {len(coordinates)} coordinates")
            
            return RouteInfo(
                coordinates=coordinates,
                distance_km=route['distance'] / 1000,  # meters to km
                duration_seconds=route['duration']
            )
            
        except Exception as e:
            print(f"   ❌ OSRM routing error: {type(e).__name__}: {e}")
            return None
    
    def get_point_at_progress(self, coordinates: List[List[float]], 
                             progress_percent: float) -> List[float]:
        """
        Get [lat, lng] at specific progress along route with interpolation
        
        Args:
            coordinates: Full route coordinates [[lat, lng], ...]
            progress_percent: 0-100
            
        Returns:
            [lat, lng] at that progress point (interpolated between points)
        """
        if not coordinates:
            return [0.0, 0.0]
        
        if len(coordinates) == 1:
            return coordinates[0]
        
        # Calculate exact position as float
        exact_index = (progress_percent / 100.0) * (len(coordinates) - 1)
        
        # Get surrounding indices
        lower_index = int(exact_index)
        upper_index = min(lower_index + 1, len(coordinates) - 1)
        
        # If at the end, return last point
        if lower_index >= len(coordinates) - 1:
            return coordinates[-1]
        
        # Interpolate between the two points
        fraction = exact_index - lower_index
        
        point1 = coordinates[lower_index]
        point2 = coordinates[upper_index]
        
        interpolated_lat = point1[0] + (point2[0] - point1[0]) * fraction
        interpolated_lng = point1[1] + (point2[1] - point1[1]) * fraction
        
        return [interpolated_lat, interpolated_lng]

# Global instance
osrm_client = OSRMClient()