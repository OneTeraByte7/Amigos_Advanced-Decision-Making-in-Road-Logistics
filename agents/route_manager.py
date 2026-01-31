"""
agents/route_manager.py
───────────────────────
AGENT 3: ADAPTIVE ROUTE MANAGEMENT AGENT
─────────────────────────────────────────
Role: Monitor and adapt routes for vehicles ALREADY IN MOTION.

This is the KEY agent for solving the problem statement:
"Little ability to adapt once a truck is already on the road"

What this agent does while truck moves from A→B:
1. Monitors traffic conditions
2. Detects delays and calculates impact
3. Searches for new load opportunities along the route
4. Decides whether to:
   - Continue on current route
   - Take detour for a profitable new load
   - Adjust for traffic/delays
5. Re-optimizes in real-time

Why LLM:
- Weighs trade-offs (time vs profit vs customer satisfaction)
- Considers multiple factors simultaneously
- Explains decisions to driver/dispatcher
- Adapts to unexpected situations
"""

import time
import uuid
import math
from typing import List, Dict, Optional, Tuple
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from core.models import (
    Vehicle, Load, Trip, Event, FleetState,
    VehicleStatus, LoadStatus, TripPhase, EventType,
    Location
)
from utils.llm_client import call_llm
from config.settings import system_settings
import random


# ─────────────────────────────────────
# STATE
# ─────────────────────────────────────

class RouteManagerState(TypedDict):
    trip: Trip
    vehicle: Vehicle
    current_load: Load
    available_loads: List[Load]  # New loads that appeared
    traffic_events: List[Event]  # Traffic alerts on route
    delay_minutes: float
    new_opportunities: List[Dict]
    llm_decision: str
    action_taken: str
    updated_trip: Optional[Trip]


# ─────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Haversine distance in km."""
    R = 6371
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def estimate_location_on_route(vehicle: Vehicle, destination: Location, progress: float) -> Location:
    """
    Estimate where vehicle is based on progress (0.0 to 1.0).
    For simulation - in production, use actual GPS.
    """
    lat = vehicle.current_location.lat + (destination.lat - vehicle.current_location.lat) * progress
    lng = vehicle.current_location.lng + (destination.lng - vehicle.current_location.lng) * progress
    return Location(lat=lat, lng=lng, name=f"En-route (progress: {progress*100:.0f}%)")


# ─────────────────────────────────────
# NODE 1: Detect Route Conditions
# ─────────────────────────────────────

def detect_route_conditions(state: RouteManagerState) -> RouteManagerState:
    """
    Monitor current route for:
    - Traffic delays
    - Vehicle issues (fuel, breakdown)
    - Weather conditions
    """
    trip = state["trip"]
    vehicle = state["vehicle"]
    
    # Simulate traffic detection (in production, call traffic API)
    traffic_events = []
    delay_minutes = 0.0
    
    # Random traffic event (30% chance)
    if random.random() < 0.3:
        delay_amount = random.uniform(15, 60)
        traffic_events.append(Event(
            event_id=str(uuid.uuid4())[:12],
            event_type=EventType.TRAFFIC_ALERT,
            timestamp=time.time(),
            payload={
                "vehicle_id": vehicle.vehicle_id,
                "trip_id": trip.trip_id,
                "delay_minutes": delay_amount,
                "reason": random.choice([
                    "Heavy traffic on highway",
                    "Road construction ahead",
                    "Accident blocking lane",
                    "Weather conditions slow"
                ]),
                "location": vehicle.current_location.name
            }
        ))
        delay_minutes = delay_amount
    
    # Check fuel level
    if vehicle.fuel_level_percent < 20:
        traffic_events.append(Event(
            event_id=str(uuid.uuid4())[:12],
            event_type=EventType.DELIVERY_DELAY,
            timestamp=time.time(),
            payload={
                "vehicle_id": vehicle.vehicle_id,
                "reason": "Low fuel - refueling needed",
                "fuel_level": vehicle.fuel_level_percent,
                "estimated_delay_minutes": 30
            }
        ))
        delay_minutes += 30
    
    state["traffic_events"] = traffic_events
    state["delay_minutes"] = delay_minutes
    return state


# ─────────────────────────────────────
# NODE 2: Search for New Opportunities
# ─────────────────────────────────────

def search_new_opportunities(state: RouteManagerState) -> RouteManagerState:
    """
    While truck is moving, check if new loads appeared nearby
    that could be picked up with minimal detour.
    
    This is KEY to reducing empty return legs!
    """
    vehicle = state["vehicle"]
    current_load = state["current_load"]
    available_loads = state["available_loads"]
    
    opportunities = []
    
    # Check loads near delivery destination
    for load in available_loads:
        if load.status != LoadStatus.AVAILABLE:
            continue
        
        # Distance from current delivery destination to new load pickup
        detour_distance = calculate_distance(
            current_load.destination.lat,
            current_load.destination.lng,
            load.origin.lat,
            load.origin.lng
        )
        
        # Only consider if detour is reasonable (< 100km)
        if detour_distance > 100:
            continue
        
        # Calculate profitability
        revenue = load.offered_rate_per_km * load.distance_km
        extra_cost = detour_distance * 2.5  # Fuel cost for detour
        delivery_cost = load.distance_km * 2.5
        total_cost = extra_cost + delivery_cost
        profit = revenue - total_cost
        
        if profit > 0:
            opportunities.append({
                "load_id": load.load_id,
                "load_origin": load.origin.name,
                "load_destination": load.destination.name,
                "detour_km": round(detour_distance, 2),
                "new_delivery_km": round(load.distance_km, 2),
                "revenue": round(revenue, 2),
                "cost": round(total_cost, 2),
                "profit": round(profit, 2),
                "profit_margin": round(profit / revenue, 4) if revenue > 0 else 0,
                "weight_tons": load.weight_tons,
                "pickup_deadline": load.pickup_window_end
            })
    
    state["new_opportunities"] = opportunities
    return state


# ─────────────────────────────────────
# NODE 3: LLM Decision Making
# ─────────────────────────────────────

def llm_route_decision(state: RouteManagerState) -> RouteManagerState:
    """
    Use LLM to decide how to handle the situation.
    
    The LLM considers:
    - Current delivery commitment
    - Traffic delays
    - New load opportunities
    - Customer expectations
    - Profitability
    - Driver hours remaining
    """
    trip = state["trip"]
    vehicle = state["vehicle"]
    current_load = state["current_load"]
    delay_minutes = state["delay_minutes"]
    opportunities = state["new_opportunities"]
    traffic_events = state["traffic_events"]
    
    # Build context for LLM
    system_prompt = """You are an expert logistics operations manager making real-time decisions for trucks already on the road.

Your goal is to:
1. Ensure current delivery commitments are met
2. Minimize delays and customer impact
3. Maximize fleet utilization
4. Seize profitable new opportunities when feasible
5. Consider driver constraints (hours, fuel)

You must balance customer satisfaction with profitability.
Explain your reasoning clearly."""

    # Current situation
    current_situation = f"""
TRUCK IN MOTION - REAL-TIME DECISION NEEDED

Current Trip:
  Vehicle: {vehicle.vehicle_id}
  Status: {vehicle.status}
  Current Load: {current_load.load_id}
  Route: {current_load.origin.name} → {current_load.destination.name}
  
  Trip Progress:
    - Phase: {trip.phase}
    - Distance remaining: ~{trip.route_loaded_leg_km * 0.6:.0f} km (estimated)
    - Original ETA impact: {delay_minutes:.0f} minutes delay
    
  Vehicle State:
    - Fuel level: {vehicle.fuel_level_percent}%
    - Hours remaining: {vehicle.max_driving_hours_remaining}
    - Current location: {vehicle.current_location.name}
"""
    
    # Add traffic/delays
    if traffic_events:
        current_situation += "\n  ALERTS:\n"
        for event in traffic_events:
            current_situation += f"    ⚠️  {event.payload.get('reason', 'Delay detected')}\n"
            if 'delay_minutes' in event.payload:
                current_situation += f"        Estimated delay: {event.payload['delay_minutes']:.0f} minutes\n"
    
    # Add new opportunities
    if opportunities:
        current_situation += f"\n  NEW LOAD OPPORTUNITIES DETECTED ({len(opportunities)}):\n"
        for i, opp in enumerate(opportunities, 1):
            current_situation += f"""
    Opportunity {i}:
      Load: {opp['load_id']}
      Route: {opp['load_origin']} → {opp['load_destination']}
      Detour from delivery: {opp['detour_km']} km
      New delivery distance: {opp['new_delivery_km']} km
      Revenue: ${opp['revenue']}
      Profit: ${opp['profit']} (margin: {opp['profit_margin']*100:.1f}%)
      Weight: {opp['weight_tons']} tons
"""
    else:
        current_situation += "\n  No new load opportunities nearby.\n"
    
    user_prompt = f"""{current_situation}

DECISION REQUIRED:

Analyze this situation and decide:
1. Should we continue on current route?
2. Should we take a detour for a new load?
3. How should we handle the delays?
4. What should we communicate to customer?

Respond in this format:

DECISION: [CONTINUE / DETOUR_FOR_LOAD / ADJUST_ROUTE]

IF DETOUR:
  Selected Load: [load_id]
  Justification: [why this makes sense]

DELAY MANAGEMENT:
  [How to handle current delays]

CUSTOMER COMMUNICATION:
  [What to tell the customer]

REASONING:
  [Your detailed analysis considering all factors]

If no good options exist, say:
DECISION: CONTINUE
REASONING: [explain why staying on course is best]
"""
    
    # Call LLM
    try:
        llm_response = call_llm(system_prompt, user_prompt)
        state["llm_decision"] = llm_response
    except Exception as e:
        state["llm_decision"] = f"LLM Error: {str(e)}"
        state["action_taken"] = "CONTINUE (fallback due to error)"
        return state
    
    return state


# ─────────────────────────────────────
# NODE 4: Execute Decision
# ─────────────────────────────────────

def execute_decision(state: RouteManagerState) -> RouteManagerState:
    """
    Parse LLM decision and execute the action.
    """
    llm_decision = state["llm_decision"]
    trip = state["trip"]
    
    # Parse decision
    if "DETOUR_FOR_LOAD" in llm_decision or "DETOUR" in llm_decision:
        # Extract load ID from decision
        import re
        load_match = re.search(r'load_\d+', llm_decision)
        if load_match:
            selected_load_id = load_match.group()
            state["action_taken"] = f"DETOUR to pickup {selected_load_id}"
            
            # Update trip (in production, this would trigger new routing)
            trip.phase = TripPhase.PLANNING  # Re-plan with new load
        else:
            state["action_taken"] = "CONTINUE (could not parse load ID)"
    
    elif "ADJUST" in llm_decision:
        state["action_taken"] = "ROUTE_ADJUSTED for traffic"
        # Update trip with delay
    
    else:
        state["action_taken"] = "CONTINUE on current route"
    
    state["updated_trip"] = trip
    return state


# ─────────────────────────────────────
# BUILD GRAPH
# ─────────────────────────────────────

def build_route_manager_graph() -> StateGraph:
    """Build the LangGraph for route management."""
    graph = StateGraph(RouteManagerState)
    
    graph.add_node("detect_conditions", detect_route_conditions)
    graph.add_node("search_opportunities", search_new_opportunities)
    graph.add_node("llm_decision", llm_route_decision)
    graph.add_node("execute", execute_decision)
    
    graph.add_edge("detect_conditions", "search_opportunities")
    graph.add_edge("search_opportunities", "llm_decision")
    graph.add_edge("llm_decision", "execute")
    graph.add_edge("execute", END)
    
    graph.set_entry_point("detect_conditions")
    
    return graph


# ─────────────────────────────────────
# PUBLIC INTERFACE
# ─────────────────────────────────────

class RouteManagerAgent:
    """
    Manages routes for vehicles already in motion.
    This is the key to adaptive logistics!
    """
    
    def __init__(self):
        self.graph = build_route_manager_graph().compile()
    
    def manage_route(
        self, 
        trip: Trip, 
        vehicle: Vehicle, 
        current_load: Load,
        available_loads: List[Load]
    ) -> Dict:
        """
        Monitor and potentially adapt a route while vehicle is moving.
        
        Returns decision and reasoning.
        """
        initial_state: RouteManagerState = {
            "trip": trip,
            "vehicle": vehicle,
            "current_load": current_load,
            "available_loads": available_loads,
            "traffic_events": [],
            "delay_minutes": 0.0,
            "new_opportunities": [],
            "llm_decision": "",
            "action_taken": "",
            "updated_trip": None
        }
        
        result = self.graph.invoke(initial_state)
        
        return {
            "trip_id": trip.trip_id,
            "vehicle_id": vehicle.vehicle_id,
            "traffic_delays": len(result["traffic_events"]),
            "delay_minutes": result["delay_minutes"],
            "new_opportunities_found": len(result["new_opportunities"]),
            "opportunities": result["new_opportunities"],
            "llm_decision": result["llm_decision"],
            "action_taken": result["action_taken"],
            "updated_trip": result["updated_trip"]
        }
