"""
agents/fleet_monitor.py
───────────────────────
AGENT 1: FLEET STATE MONITOR
─────────────────────────────
Role: Continuously observe the world, build a live FleetState, and publish it.

What it does:
  1. Collects vehicle position updates (from GPS / simulator)
  2. Collects external events (traffic, new loads, fuel prices)
  3. Detects state transitions (e.g., vehicle went idle too long)
  4. Publishes a fresh FleetState snapshot that other agents read

Why LangGraph:
  - This agent has a clear loop: observe → update state → check triggers → publish
  - LangGraph's conditional edges let us branch: "if idle timeout detected, emit alert event"
  - The state dict flows through each node cleanly

LangGraph Graph Structure:
  [collect_events] → [update_fleet_state] → [check_triggers] → [publish_state]
                                                    ↓ (if trigger found)
                                            [emit_alert_event]
                                                    ↓
                                            [publish_state]
"""

import time
import uuid
from typing import TypedDict, List

from langgraph.graph import StateGraph, END
from core.models import (
    Vehicle, Load, Event, FleetState,
    VehicleStatus, LoadStatus, EventType
)
from config.settings import system_settings
from utils.simulator import (
    generate_initial_fleet,
    generate_available_loads,
    simulate_traffic_alert,
    simulate_position_update,
)


# ─────────────────────────────────────
# AGENT STATE — what flows through the graph
# ─────────────────────────────────────

class MonitorState(TypedDict):
    """Typed state that passes between LangGraph nodes."""
    vehicles: List[Vehicle]
    active_loads: List[Load]
    recent_events: List[Event]
    new_events: List[Event]           # Events collected this cycle
    triggered_alerts: List[Event]     # Alerts generated this cycle
    fleet_state: FleetState           # The output snapshot


# ─────────────────────────────────────
# NODE 1: Collect Events
# ─────────────────────────────────────

def collect_events(state: MonitorState) -> MonitorState:
    """
    Pulls in new events from the outside world.
    In production: reads from a message queue (Kafka, RabbitMQ).
    In simulation: generates synthetic events.
    """
    new_events = []

    # Simulate position updates for each vehicle
    for vehicle in state["vehicles"]:
        if vehicle.status in (VehicleStatus.EN_ROUTE_LOADED, VehicleStatus.EN_ROUTE_EMPTY):
            new_events.append(simulate_position_update(vehicle))

    # Occasionally inject a traffic alert (simulated randomness)
    # In production this comes from a traffic data API
    import random
    if random.random() < 0.3:  # 30% chance per cycle
        new_events.append(simulate_traffic_alert())

    state["new_events"] = new_events
    return state


# ─────────────────────────────────────
# NODE 2: Update Fleet State
# ─────────────────────────────────────

def update_fleet_state(state: MonitorState) -> MonitorState:
    """
    Processes new events and mutates the vehicle/load lists accordingly.
    This is where raw events become structured state changes.
    """
    vehicles_by_id = {v.vehicle_id: v for v in state["vehicles"]}
    loads_by_id = {l.load_id: l for l in state["active_loads"]}

    for event in state["new_events"]:

        if event.event_type == EventType.VEHICLE_POSITION_UPDATE:
            vid = event.payload.get("vehicle_id")
            if vid and vid in vehicles_by_id:
                old = vehicles_by_id[vid]
                # Update location
                from core.models import Location
                new_loc = Location(
                    lat=event.payload["lat"],
                    lng=event.payload["lng"],
                    name=old.current_location.name
                )
                # Rebuild vehicle with updated location and timestamp
                vehicles_by_id[vid] = old.model_copy(update={
                    "current_location": new_loc,
                    "last_updated_at": event.timestamp,
                })

        elif event.event_type == EventType.LOAD_POSTED:
            # A new load appeared — add it to active loads
            load_data = event.payload
            if "load_id" in load_data:
                new_load = Load(**load_data)
                loads_by_id[new_load.load_id] = new_load

        elif event.event_type == EventType.LOAD_CANCELLED:
            lid = event.payload.get("load_id")
            if lid and lid in loads_by_id:
                old_load = loads_by_id[lid]
                loads_by_id[lid] = old_load.model_copy(update={
                    "status": LoadStatus.CANCELLED
                })

    # Write back
    state["vehicles"] = list(vehicles_by_id.values())
    state["active_loads"] = list(loads_by_id.values())

    # Append new events to recent history (keep last 50)
    state["recent_events"] = (state["recent_events"] + state["new_events"])[-50:]

    return state


# ─────────────────────────────────────
# NODE 3: Check Triggers
# ─────────────────────────────────────

def check_triggers(state: MonitorState) -> MonitorState:
    """
    Scans for conditions that should generate alert events.
    This is the Monitor's "reasoning" step — it doesn't just relay data,
    it detects situations that need attention.

    Current triggers:
      - Vehicle idle longer than MAX_IDLE_MINUTES → VEHICLE_IDLE_TIMEOUT
      - Load approaching pickup window end → implicit (visible in state)
    """
    alerts = []
    max_idle = system_settings.max_idle_minutes

    for vehicle in state["vehicles"]:
        if (
            vehicle.status == VehicleStatus.IDLE
            and vehicle.idle_minutes_today >= max_idle
            and vehicle.is_available
        ):
            alerts.append(Event(
                event_id=str(uuid.uuid4())[:12],
                event_type=EventType.VEHICLE_IDLE_TIMEOUT,
                timestamp=time.time(),
                payload={
                    "vehicle_id": vehicle.vehicle_id,
                    "idle_minutes": vehicle.idle_minutes_today,
                    "location": {
                        "lat": vehicle.current_location.lat,
                        "lng": vehicle.current_location.lng,
                        "name": vehicle.current_location.name,
                    }
                }
            ))

    state["triggered_alerts"] = alerts
    return state


# ─────────────────────────────────────
# CONDITIONAL EDGE: Did we find alerts?
# ─────────────────────────────────────

def should_emit_alerts(state: MonitorState) -> str:
    """
    LangGraph conditional edge.
    If there are triggered alerts, route to emit_alert_event node.
    Otherwise, go straight to publish.
    """
    if state.get("triggered_alerts"):
        return "emit_alerts"
    return "publish"


# ─────────────────────────────────────
# NODE 4a: Emit Alert Events (conditional)
# ─────────────────────────────────────

def emit_alert_events(state: MonitorState) -> MonitorState:
    """
    Adds triggered alerts into the recent_events history
    so downstream agents can see them in the FleetState.
    """
    state["recent_events"] = (state["recent_events"] + state["triggered_alerts"])[-50:]
    return state


# ─────────────────────────────────────
# NODE 4b: Publish State
# ─────────────────────────────────────

def publish_state(state: MonitorState) -> MonitorState:
    """
    Assembles the final FleetState snapshot.
    This is what all other agents will read.
    """
    # Filter out cancelled/delivered loads from active list
    active_loads = [
        l for l in state["active_loads"]
        if l.status in (LoadStatus.AVAILABLE, LoadStatus.MATCHED, LoadStatus.IN_TRANSIT)
    ]

    fleet_state = FleetState(
        snapshot_at=time.time(),
        vehicles=state["vehicles"],
        active_loads=active_loads,
        active_trips=[],              # Will be populated by Orchestrator
        recent_events=state["recent_events"],
    )

    state["fleet_state"] = fleet_state
    return state


# ─────────────────────────────────────
# BUILD THE LANGGRAPH
# ─────────────────────────────────────

def build_monitor_graph() -> StateGraph:
    """
    Assembles the LangGraph for the Fleet Monitor agent.

    Graph topology:
        collect_events
            ↓
        update_fleet_state
            ↓
        check_triggers
            ↓ (conditional)
        ├── emit_alert_events → publish_state → END
        └── publish_state → END
    """
    graph = StateGraph(MonitorState)

    # Add nodes
    graph.add_node("collect_events", collect_events)
    graph.add_node("update_fleet_state", update_fleet_state)
    graph.add_node("check_triggers", check_triggers)
    graph.add_node("emit_alert_events", emit_alert_events)
    graph.add_node("publish_state", publish_state)

    # Add edges (flow)
    graph.add_edge("collect_events", "update_fleet_state")
    graph.add_edge("update_fleet_state", "check_triggers")

    # Conditional edge after trigger check
    graph.add_conditional_edges(
        "check_triggers",
        should_emit_alerts,
        {
            "emit_alerts": "emit_alert_events",
            "publish": "publish_state",
        }
    )

    # After emitting alerts, still publish
    graph.add_edge("emit_alert_events", "publish_state")
    graph.add_edge("publish_state", END)

    # Entry point
    graph.set_entry_point("collect_events")

    return graph


# ─────────────────────────────────────
# PUBLIC INTERFACE
# ─────────────────────────────────────

class FleetMonitorAgent:
    """
    The runnable agent. Holds the compiled graph and manages state persistence
    across cycles.

    Usage:
        monitor = FleetMonitorAgent()
        monitor.initialize()                # Load initial fleet + loads
        fleet_state = monitor.run_cycle()   # One observe→publish cycle
    """

    def __init__(self):
        self.graph = build_monitor_graph().compile()
        self._state: MonitorState = {
            "vehicles": [],
            "active_loads": [],
            "recent_events": [],
            "new_events": [],
            "triggered_alerts": [],
            "fleet_state": FleetState(),
        }

    def initialize(self, num_vehicles: int = 5, num_loads: int = 8):
        """Seed the monitor with initial simulated data."""
        self._state["vehicles"] = generate_initial_fleet(num_vehicles)
        self._state["active_loads"] = generate_available_loads(num_loads)
        # Create initial fleet state so data is immediately available
        self._state["fleet_state"] = FleetState(
            snapshot_at=time.time(),
            vehicles=self._state["vehicles"],
            active_loads=self._state["active_loads"],
            active_trips=[],
            recent_events=[]
        )
        print(f"[FleetMonitor] Initialized with {num_vehicles} vehicles, {num_loads} loads")

    def run_cycle(self) -> FleetState:
        """
        Runs one full observe→process→publish cycle through the graph.
        Returns the published FleetState.
        """
        # Run the graph with current state
        result = self.graph.invoke(self._state)

        # Persist state for next cycle (events accumulate, vehicles update)
        self._state["vehicles"] = result["vehicles"]
        self._state["active_loads"] = result["active_loads"]
        self._state["recent_events"] = result["recent_events"]

        fleet_state = result["fleet_state"]
        print(f"[FleetMonitor] Published state: {len(fleet_state.vehicles)} vehicles, "
              f"{len(fleet_state.available_loads)} available loads, "
              f"{len(fleet_state.recent_events)} recent events")

        return fleet_state

    @property
    def current_state(self) -> FleetState:
        """Returns the last published FleetState without running a new cycle."""
        return self._state["fleet_state"]