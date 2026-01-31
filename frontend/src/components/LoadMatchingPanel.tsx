import { Package, Truck, TrendingUp, MapPin } from 'lucide-react'
import { FleetState } from '../types'

interface Props {
  fleetState: FleetState | null
}

export default function LoadMatchingPanel({ fleetState }: Props) {
  const availableVehicles = fleetState?.vehicles?.filter(v => v.status === 'idle') || []
  const availableLoads = fleetState?.loads?.filter(l => l.status === 'available') || []
  const matchedLoads = fleetState?.loads?.filter(l => l.status === 'matched' || l.assigned_vehicle_id) || []

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Truck className="w-5 h-5 text-blue-600" />
            <span className="text-sm text-gray-600">Available Vehicles</span>
          </div>
          <div className="text-3xl font-bold text-blue-600">{availableVehicles.length}</div>
        </div>
        
        <div className="bg-yellow-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Package className="w-5 h-5 text-yellow-600" />
            <span className="text-sm text-gray-600">Available Loads</span>
          </div>
          <div className="text-3xl font-bold text-yellow-600">{availableLoads.length}</div>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <span className="text-sm text-gray-600">Matched</span>
          </div>
          <div className="text-3xl font-bold text-green-600">{matchedLoads.length}</div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-bold text-gray-800 mb-3">Available Loads</h3>
        <div className="space-y-3">
          {availableLoads.slice(0, 5).map(load => (
            <div key={load.id} className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="font-semibold text-gray-800 mb-2">{load.id}</div>
                  <div className="space-y-1 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span>{load.origin} â†’ {load.destination}</span>
                    </div>
                    <div className="flex gap-4">
                      <span>Weight: {load.weight}t</span>
                      <span>Distance: {load.distance.toFixed(0)}km</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-green-600">
                    ${load.total_revenue.toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-500">
                    ${load.rate_per_km.toFixed(1)}/km
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-bold text-gray-800 mb-3">Recent Matches</h3>
        <div className="space-y-3">
          {matchedLoads.slice(0, 5).map(load => (
            <div key={load.id} className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-gray-800">{load.id}</span>
                <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded-full">
                  Matched
                </span>
              </div>
              <div className="text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <Truck className="w-4 h-4" />
                  <span>{load.assigned_vehicle}</span>
                </div>
                <div className="mt-1">
                  {load.origin} â†’ {load.destination}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}