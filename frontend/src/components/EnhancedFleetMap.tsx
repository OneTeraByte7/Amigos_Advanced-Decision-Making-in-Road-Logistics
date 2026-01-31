import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Polyline } from 'react-leaflet'
import { LatLng } from 'leaflet'
import { FleetState } from '../types'
import ProfessionalTruckMarker from './ProfessionalTruckMarker'
import ProfessionalLoadMarker from './ProfessionalLoadMarker'
import 'leaflet/dist/leaflet.css'

interface Props {
  fleetState: FleetState | null
}

export default function EnhancedFleetMap({ fleetState }: Props) {
  const center: [number, number] = [20.5937, 78.9629]
  const [vehiclePositions, setVehiclePositions] = useState<Map<string, LatLng>>(new Map())

  useEffect(() => {
    if (fleetState?.vehicles) {
      const newPositions = new Map<string, LatLng>()
      fleetState.vehicles.forEach(v => {
        if (v.current_location?.lat && v.current_location?.lng) {
          newPositions.set(v.vehicle_id, new LatLng(v.current_location.lat, v.current_location.lng))
        }
      })
      setVehiclePositions(newPositions)
    }
  }, [fleetState?.vehicles])

  return (
    <MapContainer 
      center={center} 
      zoom={5} 
      className="h-full w-full rounded-xl shadow-2xl"
      style={{ background: '#f8fafc' }}
      zoomControl={true}
    >
      {/* Light Map Style */}
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      
      {/* Render active trip routes - now follows real roads! */}
      {fleetState?.trips?.map(trip => {
        const vehicle = fleetState?.vehicles?.find(v => v.vehicle_id === trip.vehicle_id)
        const load = fleetState?.loads?.find(l => l.load_id === trip.load_id)
        if (!vehicle || !load || !load.origin?.lat || !load.destination?.lat) return null

        // DEBUG: Log route data
        if (trip.route_coordinates) {
          console.log(`✅ Trip ${trip.trip_id} has ${trip.route_coordinates.length} route points`)
        } else {
          console.log(`⚠️ Trip ${trip.trip_id} has NO route_coordinates`)
        }

        // If trip has real route coordinates, use them!
        if (trip.route_coordinates && trip.route_coordinates.length > 0) {
          const routePositions: [number, number][] = trip.route_coordinates.map(coord => [coord[0], coord[1]])
          
          console.log(`🗺️ Rendering real route for ${trip.trip_id}:`, routePositions.slice(0, 3))
          
          return (
            <Polyline
              key={trip.trip_id}
              positions={routePositions}
              pathOptions={{
                color: '#0066ff',
                weight: 4,
                opacity: 0.7,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />
          )
        }

        // Fallback to straight line if no route available
        console.log(`⚠️ Using straight line fallback for ${trip.trip_id}`)
        const currentPos: [number, number] = [
          vehicle.current_location.lat, 
          vehicle.current_location.lng
        ]
        const destPos: [number, number] = [
          load.destination.lat, 
          load.destination.lng
        ]

        return (
          <Polyline
            key={trip.trip_id}
            positions={[currentPos, destPos]}
            pathOptions={{
              color: '#10B981',
              weight: 4,
              opacity: 0.8,
              dashArray: '10, 10',
              lineCap: 'round',
            }}
          />
        )
      })}

      {/* Render available loads with professional markers */}
      {fleetState?.loads?.filter(l => l.status === 'available').map(load => (
        <ProfessionalLoadMarker key={load.load_id} load={load} />
      ))}

      {/* Render live trucks with professional animated markers */}
      {fleetState?.vehicles?.map(vehicle => {
        if (!vehicle.current_location?.lat || !vehicle.current_location?.lng) return null
        
        const previousPosition = vehiclePositions.get(vehicle.vehicle_id)
        
        return (
          <ProfessionalTruckMarker
            key={vehicle.vehicle_id}
            vehicle={vehicle}
            previousPosition={previousPosition}
          />
        )
      })}
    </MapContainer>
  )
}
