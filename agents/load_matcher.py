"""
agents/load_matcher.py
──────────────────────
AGENT 2: INTELLIGENT LOAD MATCHING AGENT
─────────────────────────────────────────
Role: Match available vehicles with available loads using AI reasoning.

This agent uses LLM to make intelligent matching decisions based on:
- Vehicle location and current position
- Load pickup/delivery locations
- Profitability (revenue vs. cost)
- Delivery deadlines
- Vehicle capacity and constraints
- Empty return minimization

Why LLM:
- Weighs multiple competing factors (profit, utilization, time)
- Reasons about future consequences
- Explains decisions (transparency)
- Adapts to changing conditions
"""

import time
import uuid
from typing import List, Dict, Optional, Tuple
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from core.models import (
    Vehicle, Load, Trip, FleetState, Event,
    VehicleStatus, LoadStatus, TripPhase, EventType
)
from utils.llm_client import call_llm
from config.settings import metric_targets
import math


# ─────────────────────────────────────
# STATE
# ─────────────────────────────────────

class MatcherState(TypedDict):
    fleet_state: FleetState
    proposed_matches: List[Dict]
    llm_reasoning: str
    matches_approved: List[Tuple[str, str]]  # (vehicle_id, load_id)


# ─────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Haversine distance in km."""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def calculate_trip_metrics(vehicle: Vehicle, load: Load) -> Dict:
    """Calculate financial and operational metrics for a potential trip."""
    # Distance from vehicle to pickup
    pickup_distance = calculate_distance(
        vehicle.current_location.lat,
        vehicle.current_location.lng,
        load.origin.lat,
        load.origin.lng
    )
    
    # Distance from pickup to delivery (already in load)
    delivery_distance = load.distance_km
    
    total_distance = pickup_distance + delivery_distance
    
    # Revenue
    revenue = load.offered_rate_per_km * delivery_distance
    
    # Costs
    fuel_cost = total_distance * 2.5  # rupees 2.5 per km
    time_hours = total_distance / 60  # Assuming 60 km/h average
    driver_cost = time_hours * 15.0  # rupees 15 per hour
    total_cost = fuel_cost + driver_cost
    
    # Profit
    profit = revenue - total_cost
    profit_margin = profit / revenue if revenue > 0 else 0
    
    # Utilization impact
    utilization = delivery_distance / total_distance if total_distance > 0 else 0
    
    return {
        "pickup_distance_km": round(pickup_distance, 2),
        "delivery_distance_km": round(delivery_distance, 2),
        "total_distance_km": round(total_distance, 2),
        "revenue": round(revenue, 2),
        "cost": round(total_cost, 2),
        "profit": round(profit, 2),
        "profit_margin": round(profit_margin, 4),
        "utilization": round(utilization, 4),
        "time_hours": round(time_hours, 2)
    }


# ─────────────────────────────────────
# NODE 1: Analyze Matching Opportunities
# ─────────────────────────────────────

def analyze_opportunities(state: MatcherState) -> MatcherState:
    """
    Find all possible vehicle-load pairs and calculate metrics for each.
    This prepares the data for LLM reasoning.
    """
    fleet_state = state["fleet_state"]
    available_vehicles = fleet_state.available_vehicles
    available_loads = fleet_state.available_loads
    
    opportunities = []
    
    for vehicle in available_vehicles:
        for load in available_loads:
            # Check basic constraints
            if load.weight_tons > vehicle.capacity_tons:
                continue  # Vehicle can't carry this load
            
            if load.is_expired:
                continue  # Load pickup window has passed
            
            # Calculate metrics
            metrics = calculate_trip_metrics(vehicle, load)
            
            opportunities.append({
                "vehicle_id": vehicle.vehicle_id,
                "vehicle_location": vehicle.current_location.name,
                "vehicle_fuel": vehicle.fuel_level_percent,
                "vehicle_hours_remaining": vehicle.max_driving_hours_remaining,
                "load_id": load.load_id,
                "load_origin": load.origin.name,
                "load_destination": load.destination.name,
                "load_weight": load.weight_tons,
                "metrics": metrics
            })
    
    state["proposed_matches"] = opportunities
    return state


# ─────────────────────────────────────
# NODE 2: LLM Reasoning
# ─────────────────────────────────────

def llm_match_reasoning(state: MatcherState) -> MatcherState:
    """
    Use LLM to reason about which matches are best.
    The LLM considers profitability, utilization, deadlines, and strategic positioning.
    """
    opportunities = state["proposed_matches"]
    fleet_state = state["fleet_state"]
    
    if not opportunities:
        state["llm_reasoning"] = "No matching opportunities available."
        state["matches_approved"] = []
        return state
    
    # Build prompt for LLM
    system_prompt = f"""You are an expert logistics dispatcher managing a fleet of trucks.

Your goal is to maximize:
1. Profitability (profit margin > {metric_targets.min_profit_margin})
2. Fleet utilization (loaded km / total km > {metric_targets.target_utilization_rate})
3. Minimize empty returns (pickup distance should be reasonable)
4. Meet delivery deadlines

Analyze the vehicle-load matching opportunities and recommend the BEST matches.
Consider not just immediate profit, but strategic positioning for future loads.

CRITICAL RULES:
- Each vehicle can only be matched to ONE load
- Each load can only be matched to ONE vehicle
- Prioritize profitability but balance with utilization
- Avoid matches where pickup distance > 50% of delivery distance (poor utilization)
- Consider driver constraints (hours remaining, fuel)
"""
    
    # Format opportunities as a readable list (limit to top 10 to avoid timeout)
    # Sort by profit margin first
    sorted_opps = sorted(opportunities, key=lambda x: x["metrics"]["profit_margin"], reverse=True)
    top_opportunities = sorted_opps[:10]  # Only send top 10 to LLM
    
    opportunities_text = f"MATCHING OPPORTUNITIES (Top 10 of {len(opportunities)}):\n\n"
    for i, opp in enumerate(top_opportunities, 1):
        m = opp["metrics"]
        opportunities_text += f"Opportunity {i}:\n"
        opportunities_text += f"  Vehicle: {opp['vehicle_id']} at {opp['vehicle_location']}\n"
        opportunities_text += f"  Load: {opp['load_id']} ({opp['load_origin']} → {opp['load_destination']})\n"
        opportunities_text += f"  Metrics: Profit rupees {m['profit']} ({m['profit_margin']:.0%}), Util {m['utilization']:.0%}, Distance {m['total_distance_km']}km\n"
        opportunities_text += "---\n"
    
    user_prompt = f"""{opportunities_text}

Fleet: {len(fleet_state.vehicles)} vehicles, {len(fleet_state.available_vehicles)} available
Loads: {len(fleet_state.available_loads)} available

TASK: Select the BEST 3-5 matches from the opportunities above.

Rules:
- Each vehicle can only match ONE load
- Each load can only match ONE vehicle  
- Prioritize profit margin > 12% and utilization > 85%

Respond EXACTLY like this:

APPROVED MATCHES:
- Vehicle v1 → Load l3: [one sentence why]
- Vehicle v2 → Load l5: [one sentence why]

REASONING:
[2-3 sentences on strategy]

If no good matches: say "APPROVED MATCHES: None" and explain why.
"""
    
    # Call LLM
    try:
        llm_response = call_llm(system_prompt, user_prompt)
        state["llm_reasoning"] = llm_response
    except Exception as e:
        state["llm_reasoning"] = f"LLM Error: {str(e)}"
        state["matches_approved"] = []
        return state
    
    return state


# ─────────────────────────────────────
# NODE 3: Parse LLM Response
# ─────────────────────────────────────

def parse_llm_matches(state: MatcherState) -> MatcherState:
    """
    Parse the LLM's text response and extract approved matches.
    """
    llm_response = state["llm_reasoning"]
    approved = []
    
    # Simple parsing: look for "Vehicle [id] → Load [id]" patterns
    lines = llm_response.split('\n')
    for line in lines:
        if '→' in line or '->' in line:
            # Extract vehicle and load IDs
            try:
                if '→' in line:
                    parts = line.split('→')
                else:
                    parts = line.split('->')
                
                vehicle_part = parts[0]
                load_part = parts[1].split(':')[0]  # Remove reason
                
                # Extract IDs - support both formats: truck_001, v1, vehicle_1, etc.
                import re
                # Try different ID patterns
                vehicle_match = (
                    re.search(r'truck_\d+', vehicle_part, re.IGNORECASE) or
                    re.search(r'vehicle_\d+', vehicle_part, re.IGNORECASE) or
                    re.search(r'v\d+', vehicle_part, re.IGNORECASE)
                )
                load_match = (
                    re.search(r'load_\d+', load_part, re.IGNORECASE) or
                    re.search(r'l\d+', load_part, re.IGNORECASE)
                )
                
                if vehicle_match and load_match:
                    vehicle_id = vehicle_match.group()
                    load_id = load_match.group()
                    approved.append((vehicle_id, load_id))
            except:
                continue
    
    state["matches_approved"] = approved
    return state


# ─────────────────────────────────────
# NODE 4: Create Trips
# ─────────────────────────────────────

def create_trips(state: MatcherState) -> MatcherState:
    """
    Create Trip objects for approved matches and update vehicle/load status.
    """
    fleet_state = state["fleet_state"]
    approved_matches = state["matches_approved"]
    
    # Index vehicles and loads by ID
    vehicles_by_id = {v.vehicle_id: v for v in fleet_state.vehicles}
    loads_by_id = {l.load_id: l for l in fleet_state.active_loads}
    
    new_trips = []
    new_events = []
    
    for vehicle_id, load_id in approved_matches:
        if vehicle_id not in vehicles_by_id or load_id not in loads_by_id:
            continue
        
        vehicle = vehicles_by_id[vehicle_id]
        load = loads_by_id[load_id]
        
        # Check if already matched
        if vehicle.status != VehicleStatus.IDLE or load.status != LoadStatus.AVAILABLE:
            continue
        
        # Calculate trip metrics
        metrics = calculate_trip_metrics(vehicle, load)
        
        # Create trip
        trip = Trip(
            trip_id=f"trip_{uuid.uuid4().hex[:8]}",
            vehicle_id=vehicle_id,
            load_id=load_id,
            phase=TripPhase.PLANNING,
            route_pickup_leg_km=metrics['pickup_distance_km'],
            route_loaded_leg_km=metrics['delivery_distance_km'],
            estimated_revenue=metrics['revenue'],
            estimated_cost=metrics['cost'],
            estimated_profit=metrics['profit'],
            started_at=time.time()
        )
        
        new_trips.append(trip)
        
        # Create TRIP STARTED event
        trip_event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=EventType.TRIP_STARTED,
            timestamp=time.time(),
            payload={
                "vehicle_id": vehicle_id,
                "load_id": load_id,
                "trip_id": trip.trip_id,
                "phase": TripPhase.PLANNING.value,
                "pickup_location": load.origin.name,
                "delivery_location": load.destination.name
            }
        )
        new_events.append(trip_event)
        
        # Create LOAD MATCHED event
        match_event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=EventType.LOAD_MATCHED,
            timestamp=time.time(),
            payload={
                "vehicle_id": vehicle_id,
                "load_id": load_id,
                "origin": load.origin.name,
                "destination": load.destination.name,
                "revenue": metrics['revenue'],
                "profit": metrics['profit'],
                "distance_km": metrics['delivery_distance_km']
            }
        )
        new_events.append(match_event)
        
        # Update vehicle status
        vehicles_by_id[vehicle_id] = vehicle.model_copy(update={
            "status": VehicleStatus.EN_ROUTE_EMPTY,
            "current_load_tons": load.weight_tons
        })
        
        # Update load status
        loads_by_id[load_id] = load.model_copy(update={
            "status": LoadStatus.MATCHED,
            "assigned_vehicle_id": vehicle_id
        })
    
    # Update fleet state
    fleet_state.active_trips.extend(new_trips)
    fleet_state.vehicles = list(vehicles_by_id.values())
    fleet_state.active_loads = list(loads_by_id.values())
    
    # Add events to fleet state
    fleet_state.recent_events = (new_events + fleet_state.recent_events)[:100]
    
    return state


# ─────────────────────────────────────
# BUILD GRAPH
# ─────────────────────────────────────

def build_matcher_graph() -> StateGraph:
    """Build the LangGraph for the load matching agent."""
    graph = StateGraph(MatcherState)
    
    graph.add_node("analyze_opportunities", analyze_opportunities)
    graph.add_node("llm_reasoning", llm_match_reasoning)
    graph.add_node("parse_matches", parse_llm_matches)
    graph.add_node("create_trips", create_trips)
    
    graph.add_edge("analyze_opportunities", "llm_reasoning")
    graph.add_edge("llm_reasoning", "parse_matches")
    graph.add_edge("parse_matches", "create_trips")
    graph.add_edge("create_trips", END)
    
    graph.set_entry_point("analyze_opportunities")
    
    return graph


# ─────────────────────────────────────
# PUBLIC INTERFACE
# ─────────────────────────────────────

class LoadMatcherAgent:
    """
    Intelligent load matching agent that uses LLM reasoning to match
    available vehicles with available loads.
    """
    
    def __init__(self):
        self.graph = build_matcher_graph().compile()
    
    def match_loads(self, fleet_state: FleetState) -> Dict:
        """
        Run the matching process on the current fleet state.
        Returns the reasoning and approved matches.
        """
        initial_state: MatcherState = {
            "fleet_state": fleet_state,
            "proposed_matches": [],
            "llm_reasoning": "",
            "matches_approved": []
        }
        
        result = self.graph.invoke(initial_state)
        
        return {
            "opportunities_found": len(result["proposed_matches"]),
            "matches_approved": len(result["matches_approved"]),
            "llm_reasoning": result["llm_reasoning"],
            "approved_pairs": result["matches_approved"],
            "updated_fleet_state": result["fleet_state"]
        }
