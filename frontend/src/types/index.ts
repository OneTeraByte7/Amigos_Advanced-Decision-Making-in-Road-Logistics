export interface Location {
  lat: number
  lng: number
  name?: string
}

export interface Vehicle {
  vehicle_id: string
  driver_id: string
  current_location: Location
  capacity_tons: number
  current_load_tons: number
  status: 'idle' | 'en_route_loaded' | 'en_route_empty' | 'at_pickup' | 'at_delivery' | 'maintenance' | 'offline'
  fuel_level_percent: number
  total_km_today: number
  loaded_km_today: number
  idle_minutes_today: number
  max_driving_hours_remaining: number
  home_depot?: Location
}

export interface Load {
  load_id: string
  origin: Location
  destination: Location
  weight_tons: number
  distance_km: number
  offered_rate_per_km: number
  status: 'available' | 'matched' | 'in_transit' | 'delivered' | 'cancelled' | 'expired'
  assigned_vehicle_id?: string
  pickup_window_start: number
  pickup_window_end: number
  delivery_deadline: number
  created_at: number
}

export interface Trip {
  trip_id: string
  vehicle_id: string
  load_id: string
  origin: Location
  destination: Location
  distance_km: number
  phase: string
  progress_percent: number
  estimated_revenue: number
  fuel_cost: number
  net_profit: number
  started_at: number
  route_coordinates?: number[][]  // Changed to number[][] to match JSON: [[lat, lng], ...]
  route_distance_km?: number
}

export interface Event {
  event_id?: string
  timestamp: string | number
  vehicle_id?: string
  event_type: string
  details?: Record<string, any>
  payload?: Record<string, any>
}

export interface FleetState {
  vehicles: Vehicle[]
  loads: Load[]
  trips: Trip[]
  events: Event[]
  metrics: {
    idle_vehicles: number
    enroute_vehicles: number
    available_loads: number
    matched_loads: number
  }
}

export interface FleetMetrics {
  total_vehicles: number
  available_vehicles: number
  idle_vehicles?: number
  en_route_vehicles?: number
  total_loads: number
  available_loads: number
  matched_loads: number
  in_transit_loads?: number
  avg_utilization: number
  total_km_today: number
}

export interface MatchingResult {
  message: string
  opportunities_analyzed: number
  matches_created: number
  llm_reasoning: string
  approved_matches: Array<{
    vehicle_id: string
    load_id: string
    score: number
    reasoning: string
  }>
}

export interface RouteDecision {
  vehicle_id: string
  decision: string
  reasoning: string
  estimated_benefit: number
}