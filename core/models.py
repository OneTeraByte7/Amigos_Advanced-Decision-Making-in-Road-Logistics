"""
core/models.py
──────────────
All Pydantic models used across the system.
Every agent reads/writes these types — no ad-hoc dicts anywhere.

Design rules:
  - Enums for any field that has a fixed set of values
  - Optional fields only where a value genuinely may not exist yet
  - Timestamps are always UTC floats (epoch) for fast comparison
  - No business logic here — this file is pure data structure
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import time


# ─────────────────────────────────────
# ENUMS — fixed vocabularies
# ─────────────────────────────────────

class VehicleStatus(str, Enum):
    IDLE = "idle"                    # Parked, available, no assignment
    EN_ROUTE_LOADED = "en_route_loaded"      # Moving with cargo
    EN_ROUTE_EMPTY = "en_route_empty"        # Moving without cargo (deadhead)
    AT_PICKUP = "at_pickup"          # Physically at pickup location
    AT_DELIVERY = "at_delivery"      # Physically at delivery location
    MAINTENANCE = "maintenance"      # Out of service
    OFFLINE = "offline"              # GPS lost or driver logged out


class LoadStatus(str, Enum):
    AVAILABLE = "available"          # Posted, not yet matched
    MATCHED = "matched"              # Assigned to a vehicle, not yet picked up
    IN_TRANSIT = "in_transit"        # On the truck, moving
    DELIVERED = "delivered"          # Dropped off successfully
    CANCELLED = "cancelled"          # No longer needs transport
    EXPIRED = "expired"              # Pickup window passed


class TripPhase(str, Enum):
    PLANNING = "planning"            # Route computed, not yet started
    PICKUP_LEG = "pickup_leg"        # Driving to pickup
    LOADED_LEG = "loaded_leg"        # Driving to delivery (carrying cargo)
    COMPLETED = "completed"          # Trip finished
    FAILED = "failed"                # Something went wrong


class EventType(str, Enum):
    VEHICLE_POSITION_UPDATE = "vehicle_position_update"
    LOAD_POSTED = "load_posted"
    LOAD_CANCELLED = "load_cancelled"
    TRAFFIC_ALERT = "traffic_alert"
    FUEL_PRICE_CHANGE = "fuel_price_change"
    DELIVERY_DELAY = "delivery_delay"
    VEHICLE_IDLE_TIMEOUT = "vehicle_idle_timeout"
    TRIP_COMPLETED = "trip_completed"


# ─────────────────────────────────────
# LOCATION — used everywhere
# ─────────────────────────────────────

class Location(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = None       # Human-readable label (city, depot name)

    class Config:
        frozen = True                # Locations are immutable once created


# ─────────────────────────────────────
# VEHICLE — a truck in the fleet
# ─────────────────────────────────────

class Vehicle(BaseModel):
    vehicle_id: str
    driver_id: str
    status: VehicleStatus = VehicleStatus.IDLE
    current_location: Location
    capacity_tons: float             # Max payload in metric tons
    current_load_tons: float = 0.0   # How much is on it right now
    fuel_level_percent: float = 100.0
    last_updated_at: float = Field(default_factory=time.time)  # epoch UTC

    # Accumulated metrics (reset daily or per shift)
    total_km_today: float = 0.0
    loaded_km_today: float = 0.0
    idle_minutes_today: float = 0.0

    # Constraints
    max_driving_hours_remaining: float = 10.0  # Regulatory HoS limit
    home_depot: Optional[Location] = None      # Where it needs to return

    @property
    def utilization_rate(self) -> float:
        """loaded_km / total_km for today. Returns 0 if no km driven yet."""
        if self.total_km_today == 0:
            return 0.0
        return self.loaded_km_today / self.total_km_today

    @property
    def is_available(self) -> bool:
        """Can this vehicle accept a new load right now?"""
        return (
            self.status in (VehicleStatus.IDLE, VehicleStatus.EN_ROUTE_EMPTY)
            and self.current_load_tons == 0.0
            and self.max_driving_hours_remaining > 1.0
            and self.fuel_level_percent > 15.0
        )


# ─────────────────────────────────────
# LOAD — a cargo request to be transported
# ─────────────────────────────────────

class Load(BaseModel):
    load_id: str
    status: LoadStatus = LoadStatus.AVAILABLE
    origin: Location
    destination: Location
    weight_tons: float
    pickup_window_start: float      # epoch UTC — earliest pickup
    pickup_window_end: float        # epoch UTC — latest pickup (after this → expired)
    delivery_deadline: float         # epoch UTC — must arrive by this time
    offered_rate_per_km: float       # How much the shipper is willing to pay per km
    distance_km: float               # Pre-computed origin→destination distance
    assigned_vehicle_id: Optional[str] = None
    created_at: float = Field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        return time.time() > self.pickup_window_end

    @property
    def total_offered_revenue(self) -> float:
        return self.offered_rate_per_km * self.distance_km


# ─────────────────────────────────────
# TRIP — links a vehicle to a load for a journey
# ─────────────────────────────────────

class Trip(BaseModel):
    trip_id: str
    vehicle_id: str
    load_id: str
    phase: TripPhase = TripPhase.PLANNING
    route_pickup_leg_km: float = 0.0       # Empty km to reach pickup
    route_loaded_leg_km: float = 0.0       # Loaded km from pickup to delivery
    estimated_revenue: float = 0.0
    estimated_cost: float = 0.0            # Fuel + time cost
    estimated_profit: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    @property
    def total_route_km(self) -> float:
        return self.route_pickup_leg_km + self.route_loaded_leg_km

    @property
    def profit_margin(self) -> float:
        if self.estimated_revenue == 0:
            return 0.0
        return self.estimated_profit / self.estimated_revenue


# ─────────────────────────────────────
# EVENT — things that happen in the world
# ─────────────────────────────────────

class Event(BaseModel):
    event_id: str
    event_type: EventType
    timestamp: float = Field(default_factory=time.time)
    payload: dict = {}               # Flexible — depends on event_type
    # Example payloads:
    #   VEHICLE_POSITION_UPDATE → {"vehicle_id": "v1", "lat": 28.6, "lng": 77.2}
    #   LOAD_POSTED             → {"load_id": "l42", ...full Load dict...}
    #   TRAFFIC_ALERT           → {"region": "Delhi-NH8", "delay_minutes": 45}


# ─────────────────────────────────────
# FLEET STATE — the full snapshot an agent sees
# ─────────────────────────────────────

class FleetState(BaseModel):
    """
    This is what the Monitor agent publishes and all other agents consume.
    It is the single shared view of reality at a point in time.
    """
    snapshot_at: float = Field(default_factory=time.time)
    vehicles: List[Vehicle] = []
    active_loads: List[Load] = []           # AVAILABLE or MATCHED loads
    active_trips: List[Trip] = []           # Trips currently in progress
    recent_events: List[Event] = []         # Last N events for context

    @property
    def available_vehicles(self) -> List[Vehicle]:
        return [v for v in self.vehicles if v.is_available]

    @property
    def available_loads(self) -> List[Load]:
        return [l for l in self.active_loads if l.status == LoadStatus.AVAILABLE and not l.is_expired]