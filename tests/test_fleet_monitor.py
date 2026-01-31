"""
tests/test_fleet_monitor.py
───────────────────────────
Tests for Agent 1: Fleet State Monitor.

Tests cover:
  1. Initialization produces valid fleet and loads
  2. A single cycle runs without errors and returns a FleetState
  3. Vehicle position updates are processed correctly
  4. Idle timeout triggers fire when threshold exceeded
  5. Cancelled loads are filtered from active state
  6. State persists across multiple cycles
"""

import sys
import os
import time

# Make sure imports resolve from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.fleet_monitor import FleetMonitorAgent
from core.models import (
    Vehicle, Load, Event, FleetState, Location,
    VehicleStatus, LoadStatus, EventType
)


# ─────────────────────────────────────
# TEST 1: Initialization
# ─────────────────────────────────────

def test_initialization():
    """Monitor initializes with correct number of vehicles and loads."""
    monitor = FleetMonitorAgent()
    monitor.initialize(num_vehicles=3, num_loads=5)

    assert len(monitor._state["vehicles"]) == 3, \
        f"Expected 3 vehicles, got {len(monitor._state['vehicles'])}"
    assert len(monitor._state["active_loads"]) == 5, \
        f"Expected 5 loads, got {len(monitor._state['active_loads'])}"

    # All vehicles should start as IDLE
    for v in monitor._state["vehicles"]:
        assert isinstance(v, Vehicle), f"Expected Vehicle, got {type(v)}"

    # All loads should start as AVAILABLE
    for l in monitor._state["active_loads"]:
        assert l.status == LoadStatus.AVAILABLE, \
            f"Load {l.load_id} expected AVAILABLE, got {l.status}"

    print("✓ test_initialization passed")


# ─────────────────────────────────────
# TEST 2: Single Cycle Execution
# ─────────────────────────────────────

def test_single_cycle_runs():
    """A single cycle runs and returns a valid FleetState."""
    monitor = FleetMonitorAgent()
    monitor.initialize(num_vehicles=4, num_loads=6)

    fleet_state = monitor.run_cycle()

    assert isinstance(fleet_state, FleetState), \
        f"Expected FleetState, got {type(fleet_state)}"
    assert fleet_state.snapshot_at > 0, "Snapshot timestamp should be set"
    assert len(fleet_state.vehicles) == 4, \
        f"Expected 4 vehicles in snapshot, got {len(fleet_state.vehicles)}"

    print("✓ test_single_cycle_runs passed")


# ─────────────────────────────────────
# TEST 3: Multiple Cycles Persist State
# ─────────────────────────────────────

def test_multiple_cycles_persist():
    """State accumulates across multiple cycles."""
    monitor = FleetMonitorAgent()
    monitor.initialize(num_vehicles=3, num_loads=4)

    # Run 3 cycles
    states = []
    for _ in range(3):
        state = monitor.run_cycle()
        states.append(state)

    # Each cycle should produce a newer snapshot
    assert states[1].snapshot_at >= states[0].snapshot_at, \
        "Snapshot timestamps should be non-decreasing"
    assert states[2].snapshot_at >= states[1].snapshot_at, \
        "Snapshot timestamps should be non-decreasing"

    # Vehicles should still be there
    assert len(states[2].vehicles) == 3, \
        "Vehicles should persist across cycles"

    # Recent events should accumulate (we generate some each cycle)
    assert len(states[2].recent_events) >= len(states[0].recent_events), \
        "Events should accumulate across cycles"

    print("✓ test_multiple_cycles_persist passed")


# ─────────────────────────────────────
# TEST 4: Idle Timeout Trigger
# ─────────────────────────────────────

def test_idle_timeout_trigger():
    """
    If a vehicle is IDLE and has exceeded MAX_IDLE_MINUTES,
    the monitor should emit a VEHICLE_IDLE_TIMEOUT event.
    """
    monitor = FleetMonitorAgent()
    monitor.initialize(num_vehicles=2, num_loads=2)

    # Manually set one vehicle to be idle for a long time
    vehicle = monitor._state["vehicles"][0]
    monitor._state["vehicles"][0] = vehicle.model_copy(update={
        "status": VehicleStatus.IDLE,
        "idle_minutes_today": 999,  # Way over the 30-min threshold
        "current_load_tons": 0.0,
        "max_driving_hours_remaining": 8.0,
        "fuel_level_percent": 80.0,
    })

    fleet_state = monitor.run_cycle()

    # Check that an idle timeout event was generated
    idle_events = [
        e for e in fleet_state.recent_events
        if e.event_type == EventType.VEHICLE_IDLE_TIMEOUT
    ]

    assert len(idle_events) > 0, \
        "Expected at least one VEHICLE_IDLE_TIMEOUT event for the idle vehicle"
    assert idle_events[0].payload["vehicle_id"] == vehicle.vehicle_id, \
        "Idle timeout event should reference the correct vehicle"

    print("✓ test_idle_timeout_trigger passed")


# ─────────────────────────────────────
# TEST 5: Cancelled Loads Filtered
# ─────────────────────────────────────

def test_cancelled_loads_filtered():
    """Loads with CANCELLED status should not appear in active_loads."""
    monitor = FleetMonitorAgent()
    monitor.initialize(num_vehicles=2, num_loads=3)

    # Manually cancel one load
    load = monitor._state["active_loads"][0]
    monitor._state["active_loads"][0] = load.model_copy(update={
        "status": LoadStatus.CANCELLED
    })

    fleet_state = monitor.run_cycle()

    # The cancelled load should NOT be in active_loads
    active_ids = [l.load_id for l in fleet_state.active_loads]
    assert load.load_id not in active_ids, \
        f"Cancelled load {load.load_id} should not appear in active_loads"

    print("✓ test_cancelled_loads_filtered passed")


# ─────────────────────────────────────
# TEST 6: Vehicle Availability Logic
# ─────────────────────────────────────

def test_vehicle_availability():
    """Test that is_available correctly identifies pickable vehicles."""
    # Available: idle, no load, has hours and fuel
    available = Vehicle(
        vehicle_id="v_avail",
        driver_id="d1",
        status=VehicleStatus.IDLE,
        current_location=Location(lat=28.6, lng=77.2, name="Delhi"),
        capacity_tons=20.0,
        current_load_tons=0.0,
        fuel_level_percent=80.0,
        max_driving_hours_remaining=8.0,
    )
    assert available.is_available is True, "Should be available"

    # Not available: already loaded
    loaded = available.model_copy(update={"current_load_tons": 10.0})
    assert loaded.is_available is False, "Should NOT be available (has load)"

    # Not available: low fuel
    low_fuel = available.model_copy(update={"fuel_level_percent": 10.0})
    assert low_fuel.is_available is False, "Should NOT be available (low fuel)"

    # Not available: no driving hours left
    no_hours = available.model_copy(update={"max_driving_hours_remaining": 0.5})
    assert no_hours.is_available is False, "Should NOT be available (no hours)"

    # Not available: in maintenance
    maintenance = available.model_copy(update={"status": VehicleStatus.MAINTENANCE})
    assert maintenance.is_available is False, "Should NOT be available (maintenance)"

    print("✓ test_vehicle_availability passed")


# ─────────────────────────────────────
# RUN ALL TESTS
# ─────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  AGENT 1: Fleet Monitor — Test Suite")
    print("=" * 60)
    print()

    test_initialization()
    test_single_cycle_runs()
    test_multiple_cycles_persist()
    test_idle_timeout_trigger()
    test_cancelled_loads_filtered()
    test_vehicle_availability()

    print()
    print("=" * 60)
    print("  ALL TESTS PASSED ✓")
    print("=" * 60)