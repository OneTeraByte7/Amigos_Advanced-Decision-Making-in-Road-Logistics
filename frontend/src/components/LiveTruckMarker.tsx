import { useEffect, useState } from 'react'
import { Marker, Popup, Tooltip } from 'react-leaflet'
import { Icon, LatLng } from 'leaflet'
import { Vehicle } from '../types'

const createTruckIcon = (status: string, rotation: number = 0) => {
  const color = status === 'idle' ? '#6B7280' : 
                status.includes('en_route_loaded') ? '#10B981' : 
                status.includes('en_route_empty') ? '#3B82F6' : '#F59E0B'
  
  return new Icon({
    iconUrl: 'data:image/svg+xml;base64,' + btoa(`
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="${color}" stroke="white" stroke-width="1.5" transform="rotate(${rotation})">
        <rect x="1" y="3" width="15" height="13" rx="2"></rect>
        <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
        <circle cx="5.5" cy="18.5" r="2.5" fill="white" stroke="${color}"></circle>
        <circle cx="18.5" cy="18.5" r="2.5" fill="white" stroke="${color}"></circle>
        <path d="M8 3 L8 1 M12 3 L12 1" stroke="${color}" stroke-width="2" stroke-linecap="round"/>
      </svg>
    `),
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20],
  })
}

interface Props {
  vehicle: Vehicle
  previousPosition?: LatLng
}

export default function LiveTruckMarker({ vehicle, previousPosition }: Props) {
  const [position, setPosition] = useState<LatLng>(
    new LatLng(vehicle.current_location.lat, vehicle.current_location.lng)
  )
  const [rotation, setRotation] = useState(0)

  useEffect(() => {
    const newPos = new LatLng(vehicle.current_location.lat, vehicle.current_location.lng)
    
    // Calculate rotation angle if moving
    if (previousPosition && !previousPosition.equals(newPos)) {
      const angle = Math.atan2(
        newPos.lng - previousPosition.lng,
        newPos.lat - previousPosition.lat
      ) * (180 / Math.PI)
      setRotation(angle)
    }

    // Smooth animation
    setPosition(newPos)
  }, [vehicle.current_location, previousPosition])

  const getStatusColor = () => {
    switch (vehicle.status) {
      case 'idle': return 'bg-gray-500'
      case 'en_route_loaded': return 'bg-green-500'
      case 'en_route_empty': return 'bg-blue-500'
      default: return 'bg-yellow-500'
    }
  }

  const getStatusLabel = () => {
    return vehicle.status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  return (
    <Marker 
      position={position} 
      icon={createTruckIcon(vehicle.status, rotation)}
    >
      <Tooltip direction="top" offset={[0, -15]} opacity={0.9} permanent={false}>
        <div className="text-xs font-semibold">{vehicle.vehicle_id}</div>
      </Tooltip>
      <Popup>
        <div className="font-sans min-w-[250px]">
          <div className="flex items-center justify-between mb-3 pb-2 border-b">
            <h3 className="font-bold text-lg text-gray-800">{vehicle.vehicle_id}</h3>
            <span className={`px-2 py-1 rounded-full text-xs text-white ${getStatusColor()}`}>
              {getStatusLabel()}
            </span>
          </div>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">📍 Location:</span>
              <span className="font-semibold">{vehicle.current_location.name || 'Unknown'}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">👤 Driver:</span>
              <span className="font-semibold">{vehicle.driver_id}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">📦 Load:</span>
              <span className="font-semibold">{vehicle.current_load_tons.toFixed(1)} / {vehicle.capacity_tons.toFixed(1)} t</span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                style={{ width: `${(vehicle.current_load_tons / vehicle.capacity_tons) * 100}%` }}
              />
            </div>
            
            <div className="flex justify-between mt-3 pt-2 border-t">
              <span className="text-gray-600">⛽ Fuel:</span>
              <span className={`font-semibold ${vehicle.fuel_level_percent < 20 ? 'text-red-600' : 'text-green-600'}`}>
                {vehicle.fuel_level_percent.toFixed(0)}%
              </span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">📊 Today:</span>
              <span className="font-semibold">{vehicle.total_km_today.toFixed(0)} km</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">⏰ Hours Left:</span>
              <span className="font-semibold">{vehicle.max_driving_hours_remaining.toFixed(1)} hrs</span>
            </div>
          </div>
        </div>
      </Popup>
    </Marker>
  )
}
