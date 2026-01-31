import { Marker, Popup } from 'react-leaflet'
import { Icon } from 'leaflet'
import { Load } from '../types'

const createLoadIcon = (isUrgent: boolean) => {
  return new Icon({
    iconUrl: 'data:image/svg+xml;base64,' + btoa(`
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
        <defs>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
          <linearGradient id="boxGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#F59E0B;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#EF4444;stop-opacity:1" />
          </linearGradient>
        </defs>
        
        ${isUrgent ? `
          <circle cx="20" cy="20" r="18" fill="#EF4444" opacity="0.2">
            <animate attributeName="r" values="15;20;15" dur="2s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0.5;0.1;0.5" dur="2s" repeatCount="indefinite"/>
          </circle>
        ` : ''}
        
        <g filter="url(#glow)">
          <!-- Box Base -->
          <path d="M 20 8 L 30 13 L 30 23 L 20 28 L 10 23 L 10 13 Z" 
                fill="url(#boxGrad)" 
                stroke="white" 
                stroke-width="2"
                stroke-linejoin="round"/>
          
          <!-- Box Top -->
          <path d="M 10 13 L 20 8 L 30 13 L 20 18 Z" 
                fill="#FCD34D" 
                stroke="white" 
                stroke-width="2"
                stroke-linejoin="round"/>
          
          <!-- Box Side -->
          <path d="M 20 18 L 20 28 L 30 23 L 30 13 Z" 
                fill="#F59E0B" 
                opacity="0.8"
                stroke="white" 
                stroke-width="2"
                stroke-linejoin="round"/>
          
          <!-- Straps -->
          <line x1="12" y1="16" x2="28" y2="16" stroke="white" stroke-width="1.5" opacity="0.6"/>
          <line x1="12" y1="20" x2="28" y2="20" stroke="white" stroke-width="1.5" opacity="0.6"/>
          
          <!-- Dollar Sign -->
          <text x="20" y="22" font-size="10" font-weight="bold" fill="white" text-anchor="middle">$</text>
          
          ${isUrgent ? `
            <circle cx="32" cy="10" r="5" fill="#EF4444" stroke="white" stroke-width="2">
              <animate attributeName="opacity" values="1;0.3;1" dur="1s" repeatCount="indefinite"/>
            </circle>
            <text x="32" y="13" font-size="8" font-weight="bold" fill="white" text-anchor="middle">!</text>
          ` : ''}
        </g>
      </svg>
    `),
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20],
  })
}

interface Props {
  load: Load
}

export default function ProfessionalLoadMarker({ load }: Props) {
  if (!load.origin?.lat || !load.origin?.lng) return null

  const revenue = (load.offered_rate_per_km * load.distance_km).toFixed(0)
  const isUrgent = load.delivery_deadline < Date.now() / 1000 + 86400

  const timeToDeadline = load.delivery_deadline - Date.now() / 1000
  const hoursToDeadline = Math.floor(timeToDeadline / 3600)

  return (
    <Marker 
      position={[load.origin.lat, load.origin.lng]} 
      icon={createLoadIcon(isUrgent)}
    >
      <Popup minWidth={340} maxWidth={400}>
        <div className="font-sans">
          {/* Header */}
          <div className="bg-gradient-to-r from-orange-500 to-red-500 -m-3 mb-3 p-4 text-white rounded-t-lg">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-lg font-bold flex items-center gap-2">
                  📦 {load.load_id}
                </div>
                <div className="text-xs opacity-90 mt-1">Available Load</div>
              </div>
              {isUrgent && (
                <div className="px-3 py-1.5 rounded-full text-xs font-bold bg-red-600 text-white shadow-lg animate-pulse">
                  ⚠️ URGENT
                </div>
              )}
            </div>
          </div>

          {/* Route Information */}
          <div className="space-y-2 mb-3">
            <div className="p-3 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border-l-4 border-blue-500">
              <div className="flex items-start gap-2">
                <span className="text-blue-600 text-xl">🚩</span>
                <div className="flex-1">
                  <div className="text-xs text-gray-600 font-semibold">Origin</div>
                  <div className="font-bold text-gray-800">{load.origin.name || 'Unknown'}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    📍 {load.origin.lat.toFixed(4)}, {load.origin.lng.toFixed(4)}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-center">
              <div className="bg-gray-200 rounded-full p-2">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="text-gray-600">
                  <path d="M12 5v14m0 0l-4-4m4 4l4-4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>

            <div className="p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border-l-4 border-green-500">
              <div className="flex items-start gap-2">
                <span className="text-green-600 text-xl">🎯</span>
                <div className="flex-1">
                  <div className="text-xs text-gray-600 font-semibold">Destination</div>
                  <div className="font-bold text-gray-800">{load.destination.name || 'Unknown'}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    📍 {load.destination.lat.toFixed(4)}, {load.destination.lng.toFixed(4)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-2 mb-3">
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-3 rounded-lg border border-purple-100 text-center">
              <div className="text-2xl mb-1">⚖️</div>
              <div className="text-lg font-bold text-purple-600">{load.weight_tons}t</div>
              <div className="text-xs text-gray-600">Weight</div>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-3 rounded-lg border border-blue-100 text-center">
              <div className="text-2xl mb-1">📏</div>
              <div className="text-lg font-bold text-blue-600">{load.distance_km.toFixed(0)}km</div>
              <div className="text-xs text-gray-600">Distance</div>
            </div>

            <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-3 rounded-lg border border-orange-100 text-center">
              <div className="text-2xl mb-1">⏱️</div>
              <div className="text-lg font-bold text-orange-600">{hoursToDeadline}h</div>
              <div className="text-xs text-gray-600">Deadline</div>
            </div>
          </div>

          {/* Revenue Card */}
          <div className="bg-gradient-to-r from-green-500 to-emerald-600 p-4 rounded-xl text-white mb-3 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs opacity-90 mb-1">Total Revenue</div>
                <div className="text-3xl font-bold">${revenue}</div>
              </div>
              <div className="text-right">
                <div className="text-xs opacity-90 mb-1">Rate</div>
                <div className="text-xl font-semibold">${load.offered_rate_per_km.toFixed(2)}/km</div>
              </div>
            </div>
          </div>

          {/* Urgency Warning */}
          {isUrgent && (
            <div className="bg-red-50 border-2 border-red-200 rounded-lg p-3 flex items-center gap-3">
              <div className="bg-red-500 text-white rounded-full w-10 h-10 flex items-center justify-center text-xl animate-pulse">
                ⚠️
              </div>
              <div className="flex-1">
                <div className="font-bold text-red-700">Urgent Delivery Required!</div>
                <div className="text-xs text-red-600 mt-1">
                  Deadline in less than 24 hours
                </div>
              </div>
            </div>
          )}

          {/* Pickup Time Window */}
          <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600">
            <div className="flex justify-between">
              <span>Pickup Window:</span>
              <span className="font-semibold">
                {new Date(load.pickup_window_start * 1000).toLocaleString('en-US', { 
                  month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
                })}
              </span>
            </div>
          </div>
        </div>
      </Popup>
    </Marker>
  )
}
