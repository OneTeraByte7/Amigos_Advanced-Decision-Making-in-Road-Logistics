// Service for fetching real road routes using OSRM (Open Source Routing Machine)
// FREE - No API key required

interface RoutePoint {
  lat: number
  lng: number
}

interface RouteResponse {
  coordinates: [number, number][] // [lng, lat] format
  distance: number // meters
  duration: number // seconds
}

class RoutingService {
  private baseUrl = 'https://router.project-osrm.org/route/v1/driving'

  /**
   * Get real road route between two points
   * @param start Starting point {lat, lng}
   * @param end Destination point {lat, lng}
   * @returns Route with coordinates following actual roads
   */
  async getRoute(start: RoutePoint, end: RoutePoint): Promise<RouteResponse | null> {
    try {
      // OSRM uses lng,lat format (opposite of typical lat,lng)
      const url = `${this.baseUrl}/${start.lng},${start.lat};${end.lng},${end.lat}?overview=full&geometries=geojson`
      
      const response = await fetch(url)
      if (!response.ok) {
        console.error('OSRM routing failed:', response.statusText)
        return null
      }

      const data = await response.json()
      
      if (!data.routes || data.routes.length === 0) {
        console.error('No routes found')
        return null
      }

      const route = data.routes[0]
      
      return {
        coordinates: route.geometry.coordinates, // Array of [lng, lat]
        distance: route.distance, // meters
        duration: route.duration // seconds
      }
    } catch (error) {
      console.error('Error fetching route:', error)
      return null
    }
  }

  /**
   * Get route with multiple waypoints
   * @param points Array of points to route through
   */
  async getMultiPointRoute(points: RoutePoint[]): Promise<RouteResponse | null> {
    try {
      const coordinates = points.map(p => `${p.lng},${p.lat}`).join(';')
      const url = `${this.baseUrl}/${coordinates}?overview=full&geometries=geojson`
      
      const response = await fetch(url)
      if (!response.ok) return null

      const data = await response.json()
      const route = data.routes[0]
      
      return {
        coordinates: route.geometry.coordinates,
        distance: route.distance,
        duration: route.duration
      }
    } catch (error) {
      console.error('Error fetching multi-point route:', error)
      return null
    }
  }

  /**
   * Get point at specific progress along route
   * @param routeCoordinates Full route coordinates
   * @param progressPercent Progress from 0 to 100
   */
  getPointAtProgress(routeCoordinates: [number, number][], progressPercent: number): RoutePoint | null {
    if (!routeCoordinates || routeCoordinates.length === 0) return null
    
    const targetIndex = Math.floor((progressPercent / 100) * (routeCoordinates.length - 1))
    const clampedIndex = Math.max(0, Math.min(targetIndex, routeCoordinates.length - 1))
    
    const [lng, lat] = routeCoordinates[clampedIndex]
    return { lat, lng }
  }

  /**
   * Calculate bearing/direction between two points
   * @param start Starting point
   * @param end Ending point
   * @returns Bearing in degrees (0-360)
   */
  calculateBearing(start: RoutePoint, end: RoutePoint): number {
    const startLat = start.lat * Math.PI / 180
    const startLng = start.lng * Math.PI / 180
    const endLat = end.lat * Math.PI / 180
    const endLng = end.lng * Math.PI / 180

    const y = Math.sin(endLng - startLng) * Math.cos(endLat)
    const x = Math.cos(startLat) * Math.sin(endLat) -
              Math.sin(startLat) * Math.cos(endLat) * Math.cos(endLng - startLng)
    
    let bearing = Math.atan2(y, x) * 180 / Math.PI
    bearing = (bearing + 360) % 360
    
    return bearing
  }
}

export const routingService = new RoutingService()
export type { RoutePoint, RouteResponse }
