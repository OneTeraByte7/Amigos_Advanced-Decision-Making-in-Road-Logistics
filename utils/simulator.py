"""
utils/simulator.py
──────────────────
Generates simulated fleet data so we can test agents without real GPS/IoT.
In production, this entire module would be replaced by a live data stream.

What it simulates:
  - Vehicle position updates (trucks moving along known routes)
  - New loads appearing (shipper posts a pickup request)
  - Traffic alerts (random delays on known corridors)
  - Fuel price changes
  - Delivery delays
"""

import random
import time
import uuid
from typing import List

from core.models import (
    Vehicle, Load, Event, Location,
    VehicleStatus, LoadStatus, EventType
)


# ─── Fixed city locations for simulation (Indian cities) ───
CITIES = {
    "delhi":      Location(lat=28.6139, lng=77.2090, name="Delhi"),
    "mumbai":     Location(lat=19.0760, lng=72.8777, name="Mumbai"),
    "bangalore":  Location(lat=12.9716, lng=77.5946, name="Bangalore"),
    "chennai":    Location(lat=13.0827, lng=80.2707, name="Chennai"),
    "hyderabad":  Location(lat=17.3850, lng=78.4867, name="Hyderabad"),
    "kolkata":    Location(lat=22.5726, lng=88.3639, name="Kolkata"),
    "pune":       Location(lat=18.5204, lng=73.8567, name="Pune"),
    "jaipur":     Location(lat=26.9124, lng=75.7873, name="Jaipur"),
    "lucknow":    Location(lat=26.8467, lng=80.9462, name="Lucknow"),
    "ahmedabad":  Location(lat=22.5726, lng=72.8311, name="Ahmedabad"),
}

# Pre-computed approximate distances between city pairs (km)
DISTANCES = {
    ("delhi", "mumbai"): 1412,
    ("delhi", "bangalore"): 2150,
    ("delhi", "chennai"): 2180,
    ("delhi", "hyderabad"): 1750,
    ("delhi", "kolkata"): 1470,
    ("delhi", "pune"): 1380,
    ("delhi", "jaipur"): 270,
    ("delhi", "lucknow"): 470,
    ("delhi", "ahmedabad"): 960,
    ("mumbai", "bangalore"): 840,
    ("mumbai", "chennai"): 1340,
    ("mumbai", "hyderabad"): 730,
    ("mumbai", "pune"): 155,
    ("mumbai", "ahmedabad"): 440,
    ("bangalore", "chennai"): 340,
    ("bangalore", "hyderabad"): 570,
    ("chennai", "hyderabad"): 630,
    ("kolkata", "lucknow"): 1030,
    ("pune", "hyderabad"): 580,
    ("jaipur", "ahmedabad"): 540,
    ("lucknow", "kolkata"): 1030,
}


def get_distance(city_a: str, city_b: str) -> float:
    """Look up distance. Symmetric, so check both orderings."""
    key = (city_a, city_b)
    if key in DISTANCES:
        return float(DISTANCES[key])
    key_rev = (city_b, city_a)
    if key_rev in DISTANCES:
        return float(DISTANCES[key_rev])
    # Fallback: rough estimate based on lat/lng difference
    loc_a = CITIES[city_a]
    loc_b = CITIES[city_b]
    return round(((loc_a.lat - loc_b.lat)**2 + (loc_a.lng - loc_b.lng)**2)**0.5 * 111, 1)


def generate_initial_fleet(num_vehicles: int = 5) -> List[Vehicle]:
    """
    Creates an initial fleet of trucks at various Indian cities.
    Each truck gets realistic specs.
    """
    city_names = list(CITIES.keys())
    vehicles = []

    for i in range(num_vehicles):
        city = city_names[i % len(city_names)]
        vehicles.append(Vehicle(
            vehicle_id=f"truck_{i+1:03d}",
            driver_id=f"driver_{i+1:03d}",
            status=VehicleStatus.IDLE,
            current_location=CITIES[city],
            capacity_tons=random.uniform(10.0, 25.0),
            current_load_tons=0.0,
            fuel_level_percent=random.uniform(60.0, 100.0),
            total_km_today=random.uniform(0, 300),
            loaded_km_today=random.uniform(0, 200),
            idle_minutes_today=random.uniform(0, 90),
            max_driving_hours_remaining=random.uniform(4.0, 10.0),
            home_depot=CITIES["delhi"],
        ))

    return vehicles


def generate_available_loads(num_loads: int = 8) -> List[Load]:
    """
    Creates a batch of available loads with realistic pickup windows.
    """
    city_names = list(CITIES.keys())
    loads = []
    now = time.time()

    for i in range(num_loads):
        origin_city = random.choice(city_names)
        dest_city = random.choice([c for c in city_names if c != origin_city])

        distance = get_distance(origin_city, dest_city)
        weight = round(random.uniform(2.0, 20.0), 1)

        # Pickup window: starts now, ends in 2-6 hours
        window_hours = random.uniform(2, 6)
        # Delivery deadline: pickup_end + travel time estimate + buffer
        travel_hours = distance / 60.0  # assume avg 60 km/h
        deadline_buffer = random.uniform(1, 4)  # extra hours

        loads.append(Load(
            load_id=f"load_{i+1:03d}",
            status=LoadStatus.AVAILABLE,
            origin=CITIES[origin_city],
            destination=CITIES[dest_city],
            weight_tons=weight,
            pickup_window_start=now,
            pickup_window_end=now + (window_hours * 3600),
            delivery_deadline=now + ((window_hours + travel_hours + deadline_buffer) * 3600),
            offered_rate_per_km=round(random.uniform(35.0, 80.0), 2),  # INR per km
            distance_km=distance,
        ))

    return loads


def generate_event(event_type: EventType, payload: dict) -> Event:
    """Creates a single event with a unique ID and current timestamp."""
    return Event(
        event_id=str(uuid.uuid4())[:12],
        event_type=event_type,
        timestamp=time.time(),
        payload=payload,
    )


def simulate_traffic_alert() -> Event:
    """Generates a random traffic alert on an Indian highway corridor."""
    corridors = [
        "Delhi-NH8-Gurgaon", "Mumbai-NH4-Pune", "Bangalore-NH44-Hyderabad",
        "Chennai-NH16-Vijayawada", "Delhi-NH58-Meerut", "Kolkata-NH12-Ranchi"
    ]
    return generate_event(EventType.TRAFFIC_ALERT, {
        "corridor": random.choice(corridors),
        "delay_minutes": random.randint(15, 90),
        "reason": random.choice(["accident", "roadwork", "flooding", "protest"]),
    })


def simulate_position_update(vehicle: Vehicle) -> Event:
    """Simulates a slight position drift for a vehicle (GPS ping)."""
    new_lat = vehicle.current_location.lat + random.uniform(-0.05, 0.05)
    new_lng = vehicle.current_location.lng + random.uniform(-0.05, 0.05)
    return generate_event(EventType.VEHICLE_POSITION_UPDATE, {
        "vehicle_id": vehicle.vehicle_id,
        "lat": round(new_lat, 4),
        "lng": round(new_lng, 4),
    })