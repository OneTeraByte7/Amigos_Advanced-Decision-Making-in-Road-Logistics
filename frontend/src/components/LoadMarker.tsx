import { Marker, Popup } from 'react-leaflet'
import { Icon } from 'leaflet'
import { Load } from '../types'

const loadIcon = new Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24">
      <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#F59E0B;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#EF4444;stop-opacity:1" />
        </linearGradient>
      </defs>
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" 
            fill="url(#grad1)" stroke="white" stroke-width="2"/>
      <circle cx="12" cy="12" r="3" fill="white"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -16],
})

const pulseIcon = new Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
      <circle cx="20" cy="20" r="18" fill="#F59E0B" opacity="0.3">
        <animate attributeName="r" from="8" to="20" dur="2s" repeatCount="indefinite"/>
        <animate attributeName="opacity" from="0.8" to="0" dur="2s" repeatCount="indefinite"/>
      </circle>
      <circle cx="20" cy="20" r="16" fill="#F59E0B" opacity="0.5">
        <animate attributeName="r" from="8" to="18" dur="2s" begin="0.5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" from="0.8" to="0" dur="2s" begin="0.5s" repeatCount="indefinite"/>
      </circle>
      <path d="M28 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 10 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 28 16z" 
            fill="#F59E0B" stroke="white" stroke-width="1.5" transform="translate(1, 5)"/>
    </svg>
  `),
  iconSize: [40, 40],
  iconAnchor: [20, 20],
  popupAnchor: [0, -20],
})

interface Props {
  load: Load
}

export default function LoadMarker({ load }: Props) {
  if (!load.origin?.lat || !load.origin?.lng) return null

  const revenue = (load.offered_rate_per_km * load.distance_km).toFixed(0)
  const isUrgent = load.delivery_deadline < Date.now() / 1000 + 86400 // Less than 24 hours

  return (
    <Marker 
      position={[load.origin.lat, load.origin.lng]} 
      icon={isUrgent ? pulseIcon : loadIcon}
    >
      <Popup>
        <div className="font-sans min-w-[280px]">
          <div className="flex items-center justify-between mb-3 pb-2 border-b">
            <h3 className="font-bold text-lg text-gray-800">{load.load_id}</h3>
            <span className="px-2 py-1 rounded-full text-xs bg-orange-100 text-orange-800 font-semibold">
              Available
            </span>
          </div>
          
          <div className="space-y-3 text-sm">
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-blue-600">📍</span>
                <span className="text-gray-600 font-medium">Origin:</span>
              </div>
              <div className="font-semibold text-gray-800 ml-6">{load.origin.name || 'Unknown'}</div>
            </div>
            
            <div className="bg-green-50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-green-600">🎯</span>
                <span className="text-gray-600 font-medium">Destination:</span>
              </div>
              <div className="font-semibold text-gray-800 ml-6">{load.destination.name || 'Unknown'}</div>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-gray-50 rounded-lg p-2">
                <div className="text-gray-600 text-xs">Weight</div>
                <div className="font-bold text-gray-800">{load.weight_tons} tons</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-2">
                <div className="text-gray-600 text-xs">Distance</div>
                <div className="font-bold text-gray-800">{load.distance_km.toFixed(0)} km</div>
              </div>
            </div>
            
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-3 border-2 border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-gray-600 text-xs">Total Revenue</div>
                  <div className="font-bold text-2xl text-green-600">${revenue}</div>
                </div>
                <div className="text-right">
                  <div className="text-gray-600 text-xs">Rate/km</div>
                  <div className="font-semibold text-green-600">${load.offered_rate_per_km.toFixed(1)}</div>
                </div>
              </div>
            </div>

            {isUrgent && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-2 flex items-center gap-2">
                <span className="text-red-600">⚠️</span>
                <span className="text-red-700 text-xs font-semibold">Urgent - Deadline soon!</span>
              </div>
            )}
          </div>
        </div>
      </Popup>
    </Marker>
  )
}
