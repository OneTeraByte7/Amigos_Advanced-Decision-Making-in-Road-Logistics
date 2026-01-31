"""
Quick test to verify OSRM routing is working
Run this to see if routes are being fetched correctly
"""

import sys
sys.path.append('.')

from utils.osrm_client import osrm_client

print("=" * 60)
print("Testing OSRM Route Fetching")
print("=" * 60)

# Test route: Delhi to Mumbai
start_lat, start_lng = 28.6139, 77.2090  # Delhi
end_lat, end_lng = 19.0760, 72.8777      # Mumbai

print(f"\nFetching route from Delhi to Mumbai...")
print(f"Start: ({start_lat}, {start_lng})")
print(f"End: ({end_lat}, {end_lng})")

route_info = osrm_client.get_route(start_lat, start_lng, end_lat, end_lng)

if route_info:
    print("\n✅ SUCCESS! Route fetched from OSRM")
    print(f"   - Total points: {len(route_info.coordinates)}")
    print(f"   - Distance: {route_info.distance_km:.1f} km")
    print(f"   - Duration: {route_info.duration_seconds / 3600:.1f} hours")
    print(f"   - First 3 points: {route_info.coordinates[:3]}")
    print(f"   - Last 3 points: {route_info.coordinates[-3:]}")
    
    # Test progress calculation
    print("\n Testing position at different progress levels:")
    for progress in [0, 25, 50, 75, 100]:
        lat, lng = osrm_client.get_point_at_progress(route_info.coordinates, progress)
        print(f"   {progress}% → ({lat:.4f}, {lng:.4f})")
    
    print("\n✅ OSRM is working correctly!")
    print("   Trucks should move along real roads.")
    
else:
    print("\n❌ FAILED! Could not fetch route from OSRM")
    print("   Possible reasons:")
    print("   1. No internet connection")
    print("   2. OSRM server is down")
    print("   3. Firewall blocking requests")
    print("   4. 'requests' library not installed")
    print("\nTry manually:")
    print(f"   curl 'https://router.project-osrm.org/route/v1/driving/{start_lng},{start_lat};{end_lng},{end_lat}?overview=full'")

print("\n" + "=" * 60)
