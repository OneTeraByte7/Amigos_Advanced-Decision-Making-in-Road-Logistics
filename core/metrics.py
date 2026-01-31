"""
core/metrics.py
───────────────
All KPI computations live here. Agents do NOT compute metrics themselves —
they call these functions and get back clean numbers.

Metrics tracked (from problem statement requirements):
  1. Utilization Rate        → loaded_km / total_km          (target ≥ 0.85)
  2. Empty Return Rate       → empty_trips / total_trips     (target ≤ 0.15)
  3. Revenue per KM          → total_revenue / total_km
  4. Idle Time               → minutes a vehicle sat unused
  5. Load Acceptance Rate    → loads matched / loads available
  6. Route Deviation Cost    → extra cost from re-routing vs original plan
  7. Decision Latency        → seconds from event to agent action
  8. Profit Margin           → (revenue - cost) / revenue    (target ≥ 0.12)
"""

from typing import List, Optional
from .models import Vehicle, Load, Trip, FleetState, Event, EventType
import time


# ─────────────────────────────────────
# 1. UTILIZATION RATE
# ─────────────────────────────────────

def compute_utilization_rate(vehicle: Vehicle) -> float:
    """
    How efficiently is this vehicle being used?
    Only counts km where it was carrying cargo vs total km driven today.
    """
    if vehicle.total_km_today == 0.0:
        return 0.0
    return round(vehicle.loaded_km_today / vehicle.total_km_today, 4)


def fleet_utilization_rate(vehicles: List[Vehicle]) -> float:
    """Average utilization across all vehicles that have moved today."""
    active = [v for v in vehicles if v.total_km_today > 0]
    if not active:
        return 0.0
    return round(sum(compute_utilization_rate(v) for v in active) / len(active), 4)


# ─────────────────────────────────────
# 2. EMPTY RETURN RATE
# ─────────────────────────────────────

def compute_empty_return_rate(trips: List[Trip]) -> float:
    """
    What fraction of trips have a significant empty (pickup) leg?
    A trip is "empty return" if pickup_leg > 20% of total route.
    """
    if not trips:
        return 0.0
    empty_trips = sum(
        1 for t in trips
        if t.total_route_km > 0 and (t.route_pickup_leg_km / t.total_route_km) > 0.20
    )
    return round(empty_trips / len(trips), 4)


# ─────────────────────────────────────
# 3. REVENUE PER KM
# ─────────────────────────────────────

def compute_revenue_per_km(trips: List[Trip]) -> float:
    """Average revenue earned per kilometer across all completed/active trips."""
    total_km = sum(t.total_route_km for t in trips)
    if total_km == 0:
        return 0.0
    total_revenue = sum(t.estimated_revenue for t in trips)
    return round(total_revenue / total_km, 4)


# ─────────────────────────────────────
# 4. IDLE TIME
# ─────────────────────────────────────

def compute_idle_time(vehicle: Vehicle) -> float:
    """Returns idle minutes for this vehicle today."""
    return vehicle.idle_minutes_today


def fleet_total_idle_minutes(vehicles: List[Vehicle]) -> float:
    """Sum of all idle time across the fleet today."""
    return round(sum(v.idle_minutes_today for v in vehicles), 2)


# ─────────────────────────────────────
# 5. LOAD ACCEPTANCE RATE
# ─────────────────────────────────────

def compute_load_acceptance_rate(
    total_loads_seen: int,
    total_loads_matched: int
) -> float:
    """
    Of all loads that appeared as AVAILABLE, how many did we match?
    Higher is better — means we're not letting profitable loads escape.
    """
    if total_loads_seen == 0:
        return 0.0
    return round(total_loads_matched / total_loads_seen, 4)


# ─────────────────────────────────────
# 6. ROUTE DEVIATION COST
# ─────────────────────────────────────

def compute_route_deviation_cost(
    original_route_km: float,
    actual_route_km: float,
    cost_per_km: float
) -> float:
    """
    How much extra did a re-route cost vs the original plan?
    This is called by the Route agent when it re-plans a trip mid-journey.
    """
    deviation_km = max(0.0, actual_route_km - original_route_km)
    return round(deviation_km * cost_per_km, 2)


# ─────────────────────────────────────
# 7. DECISION LATENCY
# ─────────────────────────────────────

def compute_decision_latency(event_timestamp: float, decision_timestamp: float) -> float:
    """
    Seconds between when an event fired and when an agent acted on it.
    Lower is better. Target: < 5 seconds.
    """
    return round(decision_timestamp - event_timestamp, 3)


# ─────────────────────────────────────
# 8. PROFIT MARGIN
# ─────────────────────────────────────

def compute_profit_margin(trip: Trip) -> float:
    """
    (revenue - cost) / revenue for a single trip.
    Negative means we lose money on this trip.
    """
    if trip.estimated_revenue == 0:
        return 0.0
    return round(trip.estimated_profit / trip.estimated_revenue, 4)


def fleet_average_profit_margin(trips: List[Trip]) -> float:
    """Average profit margin across all trips."""
    if not trips:
        return 0.0
    margins = [compute_profit_margin(t) for t in trips]
    return round(sum(margins) / len(margins), 4)


# ─────────────────────────────────────
# DASHBOARD SNAPSHOT — all metrics at once
# ─────────────────────────────────────

def get_fleet_dashboard(state: FleetState) -> dict:
    """
    Returns a full metrics snapshot. Used by the Orchestrator
    to understand system health at a glance.
    """
    return {
        "snapshot_at": state.snapshot_at,
        "total_vehicles": len(state.vehicles),
        "available_vehicles": len(state.available_vehicles),
        "available_loads": len(state.available_loads),
        "active_trips": len(state.active_trips),
        "fleet_utilization_rate": fleet_utilization_rate(state.vehicles),
        "empty_return_rate": compute_empty_return_rate(state.active_trips),
        "revenue_per_km": compute_revenue_per_km(state.active_trips),
        "total_idle_minutes": fleet_total_idle_minutes(state.vehicles),
        "avg_profit_margin": fleet_average_profit_margin(state.active_trips),
    }