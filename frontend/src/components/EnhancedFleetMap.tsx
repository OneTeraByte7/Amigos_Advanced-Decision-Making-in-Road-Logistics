import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Polyline } from 'react-leaflet'
import { LatLng } from 'leaflet'
import { FleetState, Load } from '../types'
import LiveTruckMarker from './LiveTruckMarker'
import LoadMarker from './LoadMarker'
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
      style={{ background: '#1a1a2e' }}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
      />
      
      {/* Render active trip routes */}
      {fleetState?.trips?.map(trip => {
        const vehicle = fleetState?.vehicles?.find(v => v.vehicle_id === trip.vehicle_id)
        const load = fleetState?.loads?.find(l => l.load_id === trip.load_id)
        if (!vehicle || !load || !load.origin?.lat || !load.destination?.lat) return null

        // Draw route from current vehicle position to destination
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
              weight: 3,
              opacity: 0.7,
              dashArray: '10, 10',
            }}
          />
        )
      })}

      {/* Render available loads */}
      {fleetState?.loads?.filter(l => l.status === 'available').map(load => (
        <LoadMarker key={load.load_id} load={load} />
      ))}

      {/* Render live trucks with animation */}
      {fleetState?.vehicles?.map(vehicle => {
        if (!vehicle.current_location?.lat || !vehicle.current_location?.lng) return null
        
        const previousPosition = vehiclePositions.get(vehicle.vehicle_id)
        
        return (
          <LiveTruckMarker
            key={vehicle.vehicle_id}
            vehicle={vehicle}
            previousPosition={previousPosition}
          />
        )
      })}
    </MapContainer>
  )
}
