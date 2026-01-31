import requests
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class RouteInfo:
    coordinates: List[Tuple[float, float]]  # [(lat, lng), ...]
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
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('routes') or len(data['routes']) == 0:
                print("No routes found")
                return None
            
            route = data['routes'][0]
            
            # Convert [lng, lat] to (lat, lng) tuples
            coordinates = [
                (coord[1], coord[0])  # Swap lng,lat to lat,lng
                for coord in route['geometry']['coordinates']
            ]
            
            return RouteInfo(
                coordinates=coordinates,
                distance_km=route['distance'] / 1000,  # meters to km
                duration_seconds=route['duration']
            )
            
        except Exception as e:
            print(f"OSRM routing error: {e}")
            return None
    
    def get_point_at_progress(self, coordinates: List[Tuple[float, float]], 
                             progress_percent: float) -> Tuple[float, float]:
        """
        Get lat/lng at specific progress along route
        
        Args:
            coordinates: Full route coordinates
            progress_percent: 0-100
            
        Returns:
            (lat, lng) at that progress point
        """
        if not coordinates:
            return (0.0, 0.0)
        
        target_index = int((progress_percent / 100.0) * (len(coordinates) - 1))
        target_index = max(0, min(target_index, len(coordinates) - 1))
        
        return coordinates[target_index]

# Global instance
osrm_client = OSRMClient()