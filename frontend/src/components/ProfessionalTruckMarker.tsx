import { useEffect, useState } from 'react'
import { Marker, Popup, Tooltip } from 'react-leaflet'
import { Icon, LatLng } from 'leaflet'
import { Vehicle } from '../types'

const createTruckIcon = (status: string, rotation: number = 0) => {
  // Uber/Swiggy style 2D flat colors
  const color = status === 'idle' ? '#6B7280' : 
                status.includes('en_route_loaded') ? '#10B981' : 
                status.includes('en_route_empty') ? '#3B82F6' : '#F59E0B'
  
  return new Icon({
    iconUrl: 'data:image/svg+xml;base64,' + btoa(`
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
        <defs>
          <filter id="shadow">
            <feDropShadow dx="0" dy="1" stdDeviation="2" flood-color="#000000" flood-opacity="0.25"/>
          </filter>
        </defs>
        
        <!-- Outer circle background (white) -->
        <circle cx="20" cy="20" r="18" fill="white" filter="url(#shadow)"/>
        
        <!-- Main truck body (rotated to show direction) -->
        <g transform="rotate(${rotation} 20 20)">
          <!-- Truck cab (front) -->
          <rect x="14" y="8" width="12" height="8" rx="2" fill="${color}"/>
          
          <!-- Windshield -->
          <rect x="16" y="10" width="8" height="3" rx="1" fill="rgba(255,255,255,0.4)"/>
          
          <!-- Cargo container (back) -->
          <rect x="14" y="16" width="12" height="14" rx="1.5" fill="${color}"/>
          
          <!-- Side stripe detail -->
          <rect x="15" y="20" width="10" height="1" rx="0.5" fill="rgba(255,255,255,0.3)"/>
          
          <!-- Direction indicator (front bumper) -->
          <rect x="17" y="7" width="6" height="1.5" rx="0.5" fill="rgba(255,255,255,0.9)"/>
        </g>
        
        <!-- Status dot indicator -->
        ${status !== 'idle' ? `
          <circle cx="30" cy="10" r="4" fill="${color}">
            <animate attributeName="opacity" values="1;0.4;1" dur="1.5s" repeatCount="indefinite"/>
          </circle>
        ` : ''}
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

export default function ProfessionalTruckMarker({ vehicle, previousPosition }: Props) {
  const [position, setPosition] = useState<LatLng>(
    new LatLng(vehicle.current_location?.lat ?? 0, vehicle.current_location?.lng ?? 0)
  )
  const [rotation, setRotation] = useState(0)

  useEffect(() => {
    const newPos = new LatLng(vehicle.current_location?.lat ?? 0, vehicle.current_location?.lng ?? 0)
    
    if (previousPosition && !previousPosition.equals(newPos)) {
      const angle = Math.atan2(
        newPos.lng - previousPosition.lng,
        newPos.lat - previousPosition.lat
      ) * (180 / Math.PI)
      setRotation(angle)
    }

    // Smooth transition to new position
    const timer = setTimeout(() => {
      setPosition(newPos)
    }, 100)
    
    return () => clearTimeout(timer)
  }, [vehicle.current_location, previousPosition])

  const getStatusInfo = () => {
    switch (vehicle.status) {
      case 'idle':
        return { color: 'bg-gray-500', label: 'Idle', icon: '⏸️' }
      case 'en_route_loaded':
        return { color: 'bg-green-500', label: 'En Route (Loaded)', icon: '🚛' }
      case 'en_route_empty':
        return { color: 'bg-blue-500', label: 'En Route (Empty)', icon: '🚚' }
      case 'at_pickup':
        return { color: 'bg-yellow-500', label: 'At Pickup', icon: '📦' }
      case 'at_delivery':
        return { color: 'bg-purple-500', label: 'At Delivery', icon: '✅' }
      default:
        return { color: 'bg-gray-500', label: 'Unknown', icon: '❓' }
    }
  }

  const statusInfo = getStatusInfo()
  const utilizationPercent = ((vehicle.current_load_tons ?? 0) / (vehicle.capacity_tons || 1)) * 100

  return (
    <Marker 
      position={position} 
      icon={createTruckIcon(vehicle.status, rotation)}
    >
      <Tooltip direction="top" offset={[0, -20]} opacity={0.95} permanent={false}>
        <div className="text-xs font-bold text-center">
          {statusInfo.icon} {vehicle.vehicle_id}
        </div>
      </Tooltip>
      <Popup minWidth={320} maxWidth={400}>
        <div className="font-sans">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 -m-3 mb-3 p-4 text-white rounded-t-lg">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-lg font-bold">{vehicle.vehicle_id}</div>
                <div className="text-xs opacity-90">Driver: {vehicle.driver_id}</div>
              </div>
              <div className={`px-3 py-1.5 rounded-full text-xs font-semibold ${statusInfo.color} text-white shadow-lg`}>
                {statusInfo.icon} {statusInfo.label}
              </div>
            </div>
          </div>

          {/* Location */}
          <div className="mb-3 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-l-4 border-blue-500">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-blue-600 text-lg">📍</span>
              <div>
                <div className="font-semibold text-gray-700">Current Location</div>
                <div className="text-xs text-gray-600">{vehicle.current_location?.name ?? 'Unknown'}</div>
              </div>
            </div>
          </div>

          {/* Cargo Information */}
          <div className="mb-3 p-3 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-semibold text-gray-700">Cargo Load</span>
                <span className="text-sm font-bold text-blue-600">
                {(vehicle.current_load_tons ?? 0).toFixed(1)} / {(vehicle.capacity_tons ?? 0).toFixed(1)} tons
              </span>
            </div>
            <div className="relative w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div 
                className="absolute inset-0 bg-gradient-to-r from-blue-500 to-green-500 rounded-full transition-all duration-500"
                style={{ width: `${utilizationPercent}%` }}
              >
                <div className="absolute inset-0 bg-white opacity-20 animate-pulse"></div>
              </div>
            </div>
            <div className="text-xs text-gray-500 mt-1 text-center">
              {utilizationPercent.toFixed(0)}% Utilized
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-2 mb-3">
            <div className="bg-gradient-to-br from-orange-50 to-red-50 p-3 rounded-lg border border-orange-100">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">⛽</span>
                <span className="text-xs text-gray-600">Fuel Level</span>
              </div>
                <div className={`text-xl font-bold ${((vehicle.fuel_level_percent ?? 0) < 20) ? 'text-red-600' : 'text-orange-600'}`}>
                {(vehicle.fuel_level_percent ?? 0).toFixed(0)}%
              </div>
              {vehicle.fuel_level_percent < 20 && (
                <div className="text-xs text-red-600 font-semibold mt-1">⚠️ Low Fuel</div>
              )}
            </div>

            <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-3 rounded-lg border border-green-100">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">📊</span>
                <span className="text-xs text-gray-600">Distance Today</span>
              </div>
              <div className="text-xl font-bold text-green-600">
                {(vehicle.total_km_today ?? 0).toFixed(0)} km
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {(vehicle.loaded_km_today ?? 0).toFixed(0)} km loaded
              </div>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-3 rounded-lg border border-purple-100">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">⏰</span>
                <span className="text-xs text-gray-600">Hours Left</span>
              </div>
                <div className={`text-xl font-bold ${((vehicle.max_driving_hours_remaining ?? 0) < 2) ? 'text-red-600' : 'text-purple-600'}`}>
                {(vehicle.max_driving_hours_remaining ?? 0).toFixed(1)}h
              </div>
              {vehicle.max_driving_hours_remaining < 2 && (
                <div className="text-xs text-red-600 font-semibold mt-1">⚠️ Rest Soon</div>
              )}
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-3 rounded-lg border border-blue-100">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">📈</span>
                <span className="text-xs text-gray-600">Efficiency</span>
              </div>
                <div className="text-xl font-bold text-blue-600">
                {(vehicle.total_km_today ?? 0) > 0 ? (((vehicle.loaded_km_today ?? 0) / (vehicle.total_km_today ?? 1)) * 100).toFixed(0) : '0'}%
              </div>
              <div className="text-xs text-gray-500 mt-1">Utilization</div>
            </div>
          </div>

          {/* Home Depot Info */}
          {vehicle.home_depot && (
            <div className="p-2 bg-gray-100 rounded text-xs text-gray-600 text-center">
              🏠 Home: {vehicle.home_depot?.name ?? 'Depot'}
            </div>
          )}
        </div>
      </Popup>
    </Marker>
  )
}
