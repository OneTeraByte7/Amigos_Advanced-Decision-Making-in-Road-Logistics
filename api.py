"""
api.py
──────
FastAPI REST API for the Fleet Monitoring System.

Endpoints:
  POST /api/initialize - Initialize the fleet monitoring system
  GET  /api/state - Get current fleet state
  POST /api/cycle - Run one monitoring cycle
  GET  /api/vehicles - Get all vehicles
  GET  /api/vehicles/{vehicle_id} - Get specific vehicle
  GET  /api/loads - Get all loads
  GET  /api/loads/{load_id} - Get specific load
  GET  /api/events - Get recent events
  GET  /api/metrics - Get fleet metrics
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
import time

from agents.fleet_monitor import FleetMonitorAgent
from agents.load_matcher import LoadMatcherAgent
from agents.route_manager import RouteManagerAgent
from core.models import (
    FleetState, Vehicle, Load, Event, 
    VehicleStatus, LoadStatus, EventType, TripPhase
)
from utils.osrm_client import osrm_client

# Initialize FastAPI app
app = FastAPI(
    title="Fleet Monitoring API",
    description="REST API for fleet monitoring and logistics management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instances
monitor_agent: Optional[FleetMonitorAgent] = None
matcher_agent: Optional[LoadMatcherAgent] = None
route_manager_agent: Optional[RouteManagerAgent] = None


# ─────────────────────────────────────
# REQUEST/RESPONSE MODELS
# ─────────────────────────────────────

class InitializeRequest(BaseModel):
    num_vehicles: int = 5
    num_loads: int = 8

class InitializeResponse(BaseModel):
    message: str
    num_vehicles: int
    num_loads: int

class CycleResponse(BaseModel):
    message: str
    snapshot_at: float
    vehicles_count: int
    available_loads_count: int
    events_count: int

class MetricsResponse(BaseModel):
    total_vehicles: int
    available_vehicles: int
    idle_vehicles: int
    en_route_vehicles: int
    total_loads: int
    available_loads: int
    matched_loads: int
    in_transit_loads: int
    average_utilization: float
    total_km_today: float


# ─────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Fleet Monitoring API",
        "version": "1.0.0",
        "status": "running",
        "initialized": monitor_agent is not None
    }


@app.post("/api/initialize", response_model=InitializeResponse)
async def initialize_fleet(request: InitializeRequest):
    """
    Initialize the fleet monitoring system with vehicles and loads.
    
    Request body:
    {
        "num_vehicles": 5,
        "num_loads": 8
    }
    """
    global monitor_agent, matcher_agent, route_manager_agent
    
    try:
        monitor_agent = FleetMonitorAgent()
        monitor_agent.initialize(
            num_vehicles=request.num_vehicles,
            num_loads=request.num_loads
        )
        
        # Initialize matcher agent
        matcher_agent = LoadMatcherAgent()
        
        # Initialize route manager agent
        route_manager_agent = RouteManagerAgent()
        
        return InitializeResponse(
            message="Fleet monitoring system initialized successfully",
            num_vehicles=request.num_vehicles,
            num_loads=request.num_loads
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")


@app.get("/api/state")
async def get_fleet_state() -> FleetState:
    """
    Get the current fleet state snapshot.
    
    Returns complete fleet state including vehicles, loads, trips, and events.
    """
    if monitor_agent is None:
        raise HTTPException(
            status_code=400, 
            detail="Fleet monitoring system not initialized. Call /api/initialize first."
        )
    
    return monitor_agent.current_state


@app.post("/api/cycle", response_model=CycleResponse)
async def run_monitoring_cycle():
    """
    Run one monitoring cycle to update fleet state.
    
    This processes events, updates vehicle positions, checks triggers,
    and publishes a new fleet state.
    """
    if monitor_agent is None:
        raise HTTPException(
            status_code=400,
            detail="Fleet monitoring system not initialized. Call /api/initialize first."
        )
    
    try:
        fleet_state = monitor_agent.run_cycle()
        
        return CycleResponse(
            message="Monitoring cycle completed",
            snapshot_at=fleet_state.snapshot_at,
            vehicles_count=len(fleet_state.vehicles),
            available_loads_count=len(fleet_state.available_loads),
            events_count=len(fleet_state.recent_events)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cycle execution failed: {str(e)}")


@app.get("/api/vehicles")
async def get_vehicles(
    status: Optional[VehicleStatus] = Query(None, description="Filter by vehicle status")
) -> List[Vehicle]:
    """
    Get all vehicles, optionally filtered by status.
    
    Query parameters:
    - status: Filter by vehicle status (idle, en_route_loaded, en_route_empty, etc.)
    """
    if monitor_agent is None:
        raise HTTPException(
            status_code=400,
            detail="Fleet monitoring system not initialized. Call /api/initialize first."
        )
    
    vehicles = monitor_agent.current_state.vehicles
    
    if status:
        vehicles = [v for v in vehicles if v.status == status]
    
    return vehicles


@app.get("/api/vehicles/{vehicle_id}")
async def get_vehicle(vehicle_id: str) -> Vehicle:
    """
    Get a specific vehicle by ID.
    """
    if monitor_agent is None:
        raise HTTPException(
            status_code=400,
            detail="Fleet monitoring system not initialized. Call /api/initialize first."
        )
    
    for vehicle in monitor_agent.current_state.vehicles:
        if vehicle.vehicle_id == vehicle_id:
            return vehicle
    
    raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")


@app.get("/api/loads")
async def get_loads(
    status: Optional[LoadStatus] = Query(None, description="Filter by load status")
) -> List[Load]:
    """
    Get all loads, optionally filtered by status.
    
    Query parameters:
    - status: Filter by load status (available, matched, in_transit, etc.)
    """
    if monitor_agent is None:
        raise HTTPException(
            status_code=400,
            detail="Fleet monitoring system not initialized. Call /api/initialize first."
        )
    
    loads = monitor_agent.current_state.active_loads
    
    if status:
        loads = [l for l in loads if l.status == status]
    
    return loads


@app.get("/api/loads/{load_id}")
async def get_load(load_id: str) -> Load:
    """
    Get a specific load by ID.
    """
    if monitor_agent is None:
        raise HTTPException(
            status_code=400,
            detail="Fleet monitoring system not initialized. Call /api/initialize first."
        )
    
    for load in monitor_agent.current_state.active_loads:
        if load.load_id == load_id:
            return load
    
    raise HTTPException(status_code=404, detail=f"Load {load_id} not found")


@app.get("/api/events")
async def get_events(
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of events to return")
) -> List[Event]:
    """
    Get recent events, optionally filtered by type.
    
    Query parameters:
    - event_type: Filter by event type (vehicle_position_update, load_posted, etc.)
    - limit: Maximum number of events to return (default: 50, max: 500)
    """
    if monitor_agent is None:
        raise HTTPException(
            status_code=400,
            detail="Fleet monitoring system not initialized. Call /api/initialize first."
        )
    
    events = monitor_agent.current_state.recent_events
    
    if event_type:
        events = [e for e in events if e.event_type == event_type]
    
    return events[:limit]


@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Get aggregated fleet metrics and statistics.
    
    Returns summary metrics including vehicle counts, load counts,
    utilization rates, and total kilometers driven.
    """
    if monitor_agent is None:
        raise HTTPException(
            status_code=400,
            detail="Fleet monitoring system not initialized. Call /api/initialize first."
        )
    
    state = monitor_agent.current_state
    
    # Calculate metrics
    vehicles = state.vehicles
    loads = state.active_loads
    
    idle_vehicles = len([v for v in vehicles if v.status == VehicleStatus.IDLE])
    en_route_vehicles = len([v for v in vehicles if v.status in (VehicleStatus.EN_ROUTE_LOADED, VehicleStatus.EN_ROUTE_EMPTY)])
    available_loads = len([l for l in loads if l.status == LoadStatus.AVAILABLE])
    matched_loads = len([l for l in loads if l.status == LoadStatus.MATCHED])
    in_transit_loads = len([l for l in loads if l.status == LoadStatus.IN_TRANSIT])
    
    # Calculate average utilization
    total_utilization = sum(v.utilization_rate for v in vehicles)
    avg_utilization = total_utilization / len(vehicles) if vehicles else 0.0
    
    # Calculate total km
    total_km = sum(v.total_km_today for v in vehicles)
    
    return MetricsResponse(
        total_vehicles=len(vehicles),
        available_vehicles=len(state.available_vehicles),
        idle_vehicles=idle_vehicles,
        en_route_vehicles=en_route_vehicles,
        total_loads=len(loads),
        available_loads=available_loads,
        matched_loads=matched_loads,
        in_transit_loads=in_transit_loads,
        average_utilization=avg_utilization,
        total_km_today=total_km
    )


@app.post("/api/match-loads")
async def match_loads_intelligently():
    """
    Run the intelligent load matching agent.
    
    Uses LLM (Groq) to analyze available vehicles and loads,
    then makes smart matching decisions based on:
    - Profitability
    - Utilization
    - Strategic positioning
    - Delivery deadlines
    
    Returns the LLM's reasoning and approved matches.
    """
    if monitor_agent is None or matcher_agent is None:
        raise HTTPException(
            status_code=400,
            detail="System not initialized. Call /api/initialize first."
        )
    
    try:
        # Get current fleet state
        fleet_state = monitor_agent.current_state
        
        # Run intelligent matching
        result = matcher_agent.match_loads(fleet_state)
        
        # Update the monitor agent with the modified fleet state
        monitor_agent._state["fleet_state"] = result["updated_fleet_state"]
        monitor_agent._state["vehicles"] = result["updated_fleet_state"].vehicles
        monitor_agent._state["active_loads"] = result["updated_fleet_state"].active_loads
        
        return {
            "message": "Intelligent load matching completed",
            "opportunities_analyzed": result["opportunities_found"],
            "matches_created": result["matches_approved"],
            "llm_reasoning": result["llm_reasoning"],
            "approved_matches": [
                {"vehicle_id": v, "load_id": l}
                for v, l in result["approved_pairs"]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")


@app.post("/api/manage-routes")
async def manage_active_routes():
    """
    Manage routes for vehicles already in motion (A→B).
    
    This is the ADAPTIVE LOGISTICS agent that:
    - Monitors traffic and delays
    - Searches for new load opportunities
    - Uses LLM to decide adaptations
    - Can reroute for better opportunities
    
    This addresses: "Little ability to adapt once truck is on road"
    """
    if monitor_agent is None or route_manager_agent is None:
        raise HTTPException(
            status_code=400,
            detail="System not initialized. Call /api/initialize first."
        )
    
    try:
        fleet_state = monitor_agent.current_state
        
        # Find vehicles that are en-route (moving)
        en_route_vehicles = [
            v for v in fleet_state.vehicles 
            if v.status in (VehicleStatus.EN_ROUTE_LOADED, VehicleStatus.EN_ROUTE_EMPTY)
        ]
        
        if not en_route_vehicles:
            return {
                "message": "No vehicles currently en-route",
                "routes_managed": 0,
                "decisions": []
            }
        
        decisions = []
        
        # For each moving vehicle, run route management
        for vehicle in en_route_vehicles:
            # Find the trip for this vehicle
            trips = [t for t in fleet_state.active_trips if t.vehicle_id == vehicle.vehicle_id]
            if not trips:
                continue
            
            trip = trips[0]
            
            # Find the load
            loads = [l for l in fleet_state.active_loads if l.load_id == trip.load_id]
            if not loads:
                continue
            
            current_load = loads[0]
            
            # Get available loads (for opportunity search)
            available_loads = fleet_state.available_loads
            
            # Run route management
            result = route_manager_agent.manage_route(
                trip=trip,
                vehicle=vehicle,
                current_load=current_load,
                available_loads=available_loads
            )
            
            decisions.append(result)
        
        return {
            "message": "Route management completed",
            "routes_managed": len(decisions),
            "decisions": decisions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route management failed: {str(e)}")


@app.post("/api/simulate-movement")
async def simulate_truck_movement():
    """
    Simulate realistic truck movement along active routes.
    Updates vehicle positions incrementally toward destinations.
    """
    if monitor_agent is None:
        raise HTTPException(
            status_code=400,
            detail="System not initialized. Call /api/initialize first."
        )
    
    try:
        fleet_state = monitor_agent.current_state
        updated_vehicles = []
        predictions = []
        
        # Check if there are any active trips
        if not fleet_state.active_trips:
            return {
                "message": "No active trips to simulate",
                "vehicles_updated": 0,
                "vehicle_ids": [],
                "predictions": [],
                "timestamp": time.time()
            }
        
        # Find vehicles that are en-route
        for vehicle in fleet_state.vehicles:
            if vehicle.status not in (VehicleStatus.EN_ROUTE_LOADED, VehicleStatus.EN_ROUTE_EMPTY):
                continue
                
            # Find associated trip
            active_trip = None
            for trip in fleet_state.active_trips:
                if trip.vehicle_id == vehicle.vehicle_id:
                    active_trip = trip
                    break
            
            if not active_trip:
                continue
            
            # Find the load to get destination
            load = None
            for l in fleet_state.active_loads:
                if l.load_id == active_trip.load_id:
                    load = l
                    break
            
            if not load:
                continue
            
            # Fetch real road route if not already cached
            if active_trip.route_coordinates is None:
                print(f"🗺️ Fetching real road route for {vehicle.vehicle_id}...")
                route_info = osrm_client.get_route(
                    load.origin.lat, load.origin.lng,
                    load.destination.lat, load.destination.lng
                )
                
                if route_info:
                    active_trip.route_coordinates = route_info.coordinates
                    active_trip.route_distance_km = route_info.distance_km
                    print(f"✅ Fetched real route: {len(route_info.coordinates)} points, {route_info.distance_km:.1f}km")
                else:
                    print(f"⚠️ Route fetch failed for {vehicle.vehicle_id}, using straight line")
            
            # Calculate movement (5% progress per update)
            progress_increment = 5.0
            new_progress = min(active_trip.progress_percent + progress_increment, 100.0)
            
            # Get new position using real route if available
            if active_trip.route_coordinates:
                # Use real road route
                new_lat, new_lng = osrm_client.get_point_at_progress(
                    active_trip.route_coordinates,
                    new_progress
                )
                print(f"🚛 {vehicle.vehicle_id} moving along real roads: {new_progress:.0f}% complete")
            else:
                # Fallback to linear interpolation
                current_lat = vehicle.current_location.lat
                current_lng = vehicle.current_location.lng
                dest_lat = load.destination.lat
                dest_lng = load.destination.lng
                new_lat = current_lat + (dest_lat - current_lat) * (progress_increment / 100.0)
                new_lng = current_lng + (dest_lng - current_lng) * (progress_increment / 100.0)
                print(f"⚠️ {vehicle.vehicle_id} using straight-line fallback")
            
            # Update vehicle position
            from core.models import Location
            vehicle.current_location = Location(
                lat=new_lat,
                lng=new_lng,
                name=f"En-route ({new_progress:.0f}%)"
            )
            
            # Update trip progress
            active_trip.progress_percent = new_progress
            
            # Calculate ETA and predictions
            remaining_distance = load.distance_km * (100 - new_progress) / 100
            avg_speed_kmh = 60.0  # Average speed
            eta_hours = remaining_distance / avg_speed_kmh if remaining_distance > 0 else 0
            eta_timestamp = time.time() + (eta_hours * 3600)
            
            # Update vehicle metrics
            distance_covered = load.distance_km * (progress_increment / 100.0)
            vehicle.total_km_today += distance_covered
            if vehicle.status == VehicleStatus.EN_ROUTE_LOADED:
                vehicle.loaded_km_today += distance_covered
            
            # Fuel consumption (rough estimate: 0.3L per km)
            fuel_consumed = (distance_covered * 0.3 / 400) * 100  # 400L tank
            vehicle.fuel_level_percent = max(0, vehicle.fuel_level_percent - fuel_consumed)
            
            # Driving hours
            time_hours = distance_covered / avg_speed_kmh if avg_speed_kmh > 0 else 0
            vehicle.max_driving_hours_remaining -= time_hours
            
            updated_vehicles.append(vehicle.vehicle_id)
            
            # Generate prediction
            prediction = {
                "vehicle_id": vehicle.vehicle_id,
                "load_id": load.load_id,
                "current_progress": new_progress,
                "remaining_distance_km": remaining_distance,
                "eta_hours": round(eta_hours, 2),
                "eta_timestamp": eta_timestamp,
                "current_speed_kmh": avg_speed_kmh,
                "fuel_remaining": round(vehicle.fuel_level_percent, 1),
                "estimated_fuel_cost": round(remaining_distance * 0.3 * 1.5, 2),  # $1.5 per liter
                "on_time_status": "on-time",  # Simplified for now
                "recommendations": []
            }
            
            # Add recommendations
            if vehicle.fuel_level_percent < 20:
                prediction["recommendations"].append({
                    "type": "fuel",
                    "priority": "high",
                    "message": "Low fuel! Plan refueling stop."
                })
            
            if vehicle.max_driving_hours_remaining < 2:
                prediction["recommendations"].append({
                    "type": "rest",
                    "priority": "high",
                    "message": "Driver needs rest break soon."
                })
            
            if new_progress >= 100:
                prediction["recommendations"].append({
                    "type": "delivery",
                    "priority": "normal",
                    "message": "Arriving at destination!"
                })
                # Mark as delivered
                vehicle.status = VehicleStatus.AT_DELIVERY
                load.status = LoadStatus.DELIVERED
                active_trip.phase = TripPhase.COMPLETED
            
            predictions.append(prediction)
        
        # Update the monitor agent state
        monitor_agent._state["fleet_state"] = fleet_state
        
        return {
            "message": "Movement simulation completed",
            "vehicles_updated": len(updated_vehicles),
            "vehicle_ids": updated_vehicles,
            "predictions": predictions,
            "timestamp": time.time()
        }
        
    except Exception as e:
        import traceback
        error_detail = f"Simulation failed: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)  # Log to console
        raise HTTPException(status_code=500, detail=error_detail)


# ─────────────────────────────────────
# MAIN
# ─────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
