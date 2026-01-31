import { Package, Truck, TrendingUp, MapPin, DollarSign, Weight, Navigation, Clock, Zap } from 'lucide-react'
import { FleetState } from '../types'

interface Props {
  fleetState: FleetState | null
}

export default function ProfessionalLoadMatchingPanel({ fleetState }: Props) {
  const availableVehicles = fleetState?.vehicles?.filter(v => v.status === 'idle') || []
  const availableLoads = fleetState?.loads?.filter(l => l.status === 'available') || []
  const matchedLoads = fleetState?.loads?.filter(l => l.status === 'matched' || l.status === 'in_transit') || []
  const inTransitLoads = fleetState?.loads?.filter(l => l.status === 'in_transit') || []

  const totalRevenue = availableLoads.reduce((sum, load) => 
    sum + (load.offered_rate_per_km * load.distance_km), 0
  )

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-4 text-white shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <Truck className="w-5 h-5" />
            <span className="text-xs opacity-90">Available Vehicles</span>
          </div>
          <div className="text-4xl font-bold">{availableVehicles.length}</div>
          <div className="text-xs opacity-75 mt-1">Ready for assignment</div>
        </div>
        
        <div className="bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl p-4 text-white shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <Package className="w-5 h-5" />
            <span className="text-xs opacity-90">Available Loads</span>
          </div>
          <div className="text-4xl font-bold">{availableLoads.length}</div>
          <div className="text-xs opacity-75 mt-1">Waiting for trucks</div>
        </div>
        
        <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-4 text-white shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5" />
            <span className="text-xs opacity-90">Matched</span>
          </div>
          <div className="text-4xl font-bold">{matchedLoads.length}</div>
          <div className="text-xs opacity-75 mt-1">{inTransitLoads.length} in transit</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl p-4 text-white shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="w-5 h-5" />
            <span className="text-xs opacity-90">Revenue Pool</span>
          </div>
          <div className="text-4xl font-bold">${(totalRevenue / 1000).toFixed(0)}K</div>
          <div className="text-xs opacity-75 mt-1">Available earnings</div>
        </div>
      </div>

      {/* Available Loads Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <Package className="w-6 h-6 text-orange-500" />
            Available Loads
          </h3>
          <span className="text-sm text-gray-500">{availableLoads.length} total</span>
        </div>
        
        {availableLoads.length === 0 ? (
          <div className="bg-white rounded-xl p-8 text-center">
            <Package className="w-16 h-16 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No available loads</p>
            <p className="text-sm text-gray-400 mt-1">All loads are currently matched or delivered</p>
          </div>
        ) : (
          <div className="space-y-3">
            {availableLoads.slice(0, 6).map(load => {
              const revenue = (load.offered_rate_per_km * load.distance_km).toFixed(0)
              const isUrgent = load.delivery_deadline < Date.now() / 1000 + 86400
              
              return (
                <div 
                  key={load.load_id} 
                  className={`bg-white rounded-xl p-4 shadow-md hover:shadow-xl transition-all duration-300 border-l-4 ${
                    isUrgent ? 'border-red-500' : 'border-orange-500'
                  }`}
                >
                  {isUrgent && (
                    <div className="flex items-center gap-2 mb-2 text-red-600 text-xs font-semibold">
                      <Zap className="w-3 h-3" />
                      URGENT - Deadline in {Math.floor((load.delivery_deadline - Date.now() / 1000) / 3600)}h
                    </div>
                  )}
                  
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-bold text-lg text-gray-800 mb-3">{load.load_id}</div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                          <div className="flex items-center gap-1 text-blue-600">
                            <MapPin className="w-4 h-4" />
                            <span className="font-semibold">{load.origin.name}</span>
                          </div>
                          <span className="text-gray-400">→</span>
                          <div className="flex items-center gap-1 text-green-600">
                            <MapPin className="w-4 h-4" />
                            <span className="font-semibold">{load.destination.name}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-4 text-xs text-gray-600">
                          <div className="flex items-center gap-1">
                            <Weight className="w-3 h-3" />
                            <span>{load.weight_tons}t</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Navigation className="w-3 h-3" />
                            <span>{load.distance_km.toFixed(0)}km</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            <span>
                              {new Date(load.delivery_deadline * 1000).toLocaleDateString('en-US', { 
                                month: 'short', day: 'numeric' 
                              })}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right ml-4">
                      <div className="bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-lg p-3 shadow-md">
                        <div className="text-xs opacity-90">Revenue</div>
                        <div className="text-2xl font-bold">${revenue}</div>
                        <div className="text-xs opacity-75">${load.offered_rate_per_km.toFixed(2)}/km</div>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
            
            {availableLoads.length > 6 && (
              <div className="text-center text-sm text-gray-500 pt-2">
                + {availableLoads.length - 6} more loads available
              </div>
            )}
          </div>
        )}
      </div>

      {/* Matched/In-Transit Loads Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-green-500" />
            Active Shipments
          </h3>
          <span className="text-sm text-gray-500">{matchedLoads.length} active</span>
        </div>
        
        {matchedLoads.length === 0 ? (
          <div className="bg-white rounded-xl p-8 text-center">
            <TrendingUp className="w-16 h-16 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No active shipments</p>
            <p className="text-sm text-gray-400 mt-1">Run Load Matcher to create matches</p>
          </div>
        ) : (
          <div className="space-y-3">
            {matchedLoads.slice(0, 5).map(load => {
              const trip = fleetState?.trips?.find(t => t.load_id === load.load_id)
              const progress = trip?.progress_percent || 0
              
              return (
                <div 
                  key={load.load_id} 
                  className="bg-white rounded-xl p-4 shadow-md border-l-4 border-green-500"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <div className="font-bold text-gray-800">{load.load_id}</div>
                      <div className="text-xs text-gray-500">Vehicle: {load.assigned_vehicle_id}</div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      load.status === 'in_transit' 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-blue-100 text-blue-700'
                    }`}>
                      {load.status === 'in_transit' ? '🚛 In Transit' : '📋 Matched'}
                    </span>
                  </div>

                  <div className="mb-3">
                    <div className="flex items-center gap-2 text-sm mb-2">
                      <span className="text-gray-600">{load.origin.name}</span>
                      <span className="text-gray-400">→</span>
                      <span className="text-gray-600">{load.destination.name}</span>
                      <span className="ml-auto text-xs font-semibold text-blue-600">
                        {progress.toFixed(0)}%
                      </span>
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${progress}%` }}
                      >
                        <div className="w-full h-full bg-white opacity-20 animate-pulse"></div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-600">
                    <span>{load.distance_km.toFixed(0)}km</span>
                    <span>{load.weight_tons}t</span>
                    <span className="font-semibold text-green-600">
                      ${(load.offered_rate_per_km * load.distance_km).toFixed(0)}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Idle Vehicles Section */}
      {availableVehicles.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <Truck className="w-6 h-6 text-blue-500" />
              Idle Vehicles
            </h3>
            <span className="text-sm text-gray-500">{availableVehicles.length} waiting</span>
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            {availableVehicles.slice(0, 6).map(vehicle => (
              <div 
                key={vehicle.vehicle_id}
                className="bg-white rounded-lg p-3 shadow-md hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-gray-800">{vehicle.vehicle_id}</span>
                  <span className="px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">
                    ⏸️ Idle
                  </span>
                </div>
                <div className="text-xs text-gray-600 space-y-1">
                  <div>📍 {vehicle.current_location.name}</div>
                  <div>📦 {vehicle.capacity_tons}t capacity</div>
                  <div>⛽ {vehicle.fuel_level_percent.toFixed(0)}% fuel</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
