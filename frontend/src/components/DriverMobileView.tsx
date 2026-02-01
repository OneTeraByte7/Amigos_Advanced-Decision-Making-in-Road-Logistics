import { useState, useEffect } from 'react'
import { Truck, MapPin, Package, Clock, CheckCircle, XCircle, AlertTriangle, Navigation, DollarSign, Fuel, TrendingUp } from 'lucide-react'
import { FleetState, Load, Vehicle } from '../types'

interface Props {
  fleetState: FleetState | null
  driverId?: string
  onBack?: () => void
}

export default function DriverMobileView({ fleetState, driverId = 'driver_001', onBack }: Props) {
  const [selectedLoad, setSelectedLoad] = useState<Load | null>(null)
  const [showLoadDetails, setShowLoadDetails] = useState(false)

  // Find driver's vehicle
  const myVehicle = fleetState?.vehicles?.find(v => v.driver_id === driverId)
  const myTrip = myVehicle ? fleetState?.trips?.find(t => t.vehicle_id === myVehicle.vehicle_id) : null
  const myLoad = myTrip ? fleetState?.loads?.find(l => l.load_id === myTrip.load_id) : null

  // Get available loads for driver
  const availableLoads = fleetState?.loads?.filter(l => l.status === 'available') || []

  const getAIRecommendation = (load: Load): { score: number, reason: string, color: string } => {
    if (!myVehicle) return { score: 0, reason: 'No vehicle assigned', color: 'text-gray-500' }

    // Simple AI scoring logic
    const distanceScore = load.distance_km > 500 ? 0.6 : 0.8
    const revenueScore = load.offered_rate_per_km > 10 ? 0.9 : 0.7
    const capacityMatch = load.weight_tons <= myVehicle.capacity_tons ? 1.0 : 0.3
    
    const finalScore = (distanceScore + revenueScore + capacityMatch) / 3

    if (finalScore > 0.8) {
      return { score: finalScore, reason: '🎯 Highly Recommended - Great revenue & route', color: 'text-green-600' }
    } else if (finalScore > 0.6) {
      return { score: finalScore, reason: '✅ Good Match - Acceptable terms', color: 'text-blue-600' }
    } else {
      return { score: finalScore, reason: '⚠️ Low Priority - Consider alternatives', color: 'text-orange-600' }
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Top Header - Fixed */}
      <div className="sticky top-0 z-50 bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg">
        <div className="px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {onBack && (
                <button
                  onClick={onBack}
                  className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm hover:bg-white/30 transition-colors"
                  aria-label="Back to Fleet View"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
              )}
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                <Truck className="w-6 h-6" />
              </div>
              <div>
                <h1 className="font-bold text-lg">Driver Portal</h1>
                <p className="text-xs text-blue-100">{driverId}</p>
              </div>
            </div>
            <div className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-xs font-medium">Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Vehicle Status Card */}
      {myVehicle && (
        <div className="px-4 pt-4">
          <div className="bg-white rounded-2xl shadow-lg p-4 border-l-4 border-blue-600">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-bold text-gray-800 flex items-center gap-2">
                <Truck className="w-5 h-5 text-blue-600" />
                My Vehicle: {myVehicle.vehicle_id}
              </h2>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                myVehicle.status === 'idle' ? 'bg-gray-100 text-gray-700' :
                myVehicle.status.includes('en_route') ? 'bg-green-100 text-green-700' :
                'bg-blue-100 text-blue-700'
              }`}>
                {myVehicle.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-3 rounded-xl">
                <div className="flex items-center gap-1 mb-1">
                  <Fuel className="w-4 h-4 text-orange-600" />
                  <span className="text-xs text-gray-600">Fuel</span>
                </div>
                <div className="text-lg font-bold text-orange-700">
                  {myVehicle.fuel_level_percent.toFixed(0)}%
                </div>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-green-100 p-3 rounded-xl">
                <div className="flex items-center gap-1 mb-1">
                  <Navigation className="w-4 h-4 text-green-600" />
                  <span className="text-xs text-gray-600">Today</span>
                </div>
                <div className="text-lg font-bold text-green-700">
                  {myVehicle.total_km_today.toFixed(0)} km
                </div>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-3 rounded-xl">
                <div className="flex items-center gap-1 mb-1">
                  <Clock className="w-4 h-4 text-blue-600" />
                  <span className="text-xs text-gray-600">Hours</span>
                </div>
                <div className="text-lg font-bold text-blue-700">
                  {myVehicle.max_driving_hours_remaining.toFixed(1)}h
                </div>
              </div>
            </div>

            {/* Current Location */}
            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
              <div className="flex items-start gap-2">
                <MapPin className="w-4 h-4 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <div className="text-xs text-gray-500">Current Location</div>
                  <div className="font-semibold text-gray-800 text-sm">
                    {myVehicle.current_location.name || 'Unknown'}
                  </div>
                  <div className="text-xs text-gray-400 mt-0.5">
                    {myVehicle.current_location.lat.toFixed(4)}, {myVehicle.current_location.lng.toFixed(4)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Active Trip Card */}
      {myLoad && myTrip && (
        <div className="px-4 pt-4">
          <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl shadow-lg p-5 text-white">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-lg flex items-center gap-2">
                <Package className="w-5 h-5" />
                Active Delivery
              </h2>
              <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-semibold">
                {myTrip.progress_percent.toFixed(0)}% Complete
              </span>
            </div>

            {/* Progress Bar */}
            <div className="relative w-full bg-white/20 rounded-full h-3 mb-4 overflow-hidden">
              <div 
                className="absolute inset-0 bg-white rounded-full transition-all duration-500"
                style={{ width: `${myTrip.progress_percent}%` }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
              </div>
            </div>

            {/* Route Info */}
            <div className="space-y-2 mb-4">
              <div className="flex items-start gap-2 bg-white/10 rounded-lg p-3">
                <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
                <div className="flex-1">
                  <div className="text-xs opacity-80">Origin</div>
                  <div className="font-semibold">{myLoad.origin.name}</div>
                </div>
              </div>

              <div className="flex items-center justify-center">
                <div className="w-0.5 h-6 bg-white/30"></div>
              </div>

              <div className="flex items-start gap-2 bg-white/10 rounded-lg p-3">
                <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center flex-shrink-0">
                  <MapPin className="w-3 h-3 text-green-600" />
                </div>
                <div className="flex-1">
                  <div className="text-xs opacity-80">Destination</div>
                  <div className="font-semibold">{myLoad.destination.name}</div>
                </div>
              </div>
            </div>

            {/* Load Details */}
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-white/10 rounded-lg p-2">
                <div className="text-xs opacity-80">Distance</div>
                <div className="font-bold">{myLoad.distance_km.toFixed(0)} km</div>
              </div>
              <div className="bg-white/10 rounded-lg p-2">
                <div className="text-xs opacity-80">Weight</div>
                <div className="font-bold">{myLoad.weight_tons.toFixed(1)} tons</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Available Loads Section */}
      {!myLoad && (
        <div className="px-4 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-bold text-gray-800 flex items-center gap-2">
              <Package className="w-5 h-5 text-blue-600" />
              Available Loads
              <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full text-xs font-semibold">
                {availableLoads.length}
              </span>
            </h2>
          </div>

          {availableLoads.length === 0 ? (
            <div className="bg-white rounded-2xl shadow-sm p-8 text-center">
              <Package className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 font-medium">No loads available</p>
              <p className="text-xs text-gray-400 mt-1">Check back later for new opportunities</p>
            </div>
          ) : (
            <div className="space-y-3">
              {availableLoads.map(load => {
                const recommendation = getAIRecommendation(load)
                return (
                  <div 
                    key={load.load_id}
                    className="bg-white rounded-2xl shadow-sm border-2 border-gray-100 hover:border-blue-300 transition-all cursor-pointer"
                    onClick={() => {
                      setSelectedLoad(load)
                      setShowLoadDetails(true)
                    }}
                  >
                    <div className="p-4">
                      {/* Header */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-bold text-gray-800">{load.load_id}</span>
                            <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-xs font-semibold">
                              rupees {((load.offered_rate_per_km || 0) * (load.distance_km || 0)).toFixed(0)}
                            </span>
                          </div>
                          <div className={`text-xs font-medium ${recommendation.color}`}>
                            {recommendation.reason}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-bold text-gray-800">{load.distance_km.toFixed(0)} km</div>
                          <div className="text-xs text-gray-500">{load.weight_tons.toFixed(1)} tons</div>
                        </div>
                      </div>

                      {/* Route */}
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-sm">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <span className="text-gray-600">{load.origin.name}</span>
                        </div>
                        <div className="ml-1 w-0.5 h-3 bg-gray-200"></div>
                        <div className="flex items-center gap-2 text-sm">
                          <MapPin className="w-4 h-4 text-green-600" />
                          <span className="text-gray-600">{load.destination.name}</span>
                        </div>
                      </div>

                      {/* AI Score Indicator */}
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-500">AI Match Score</span>
                          <div className="flex items-center gap-2">
                            <div className="w-24 bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-full rounded-full ${
                                  recommendation.score > 0.8 ? 'bg-green-500' :
                                  recommendation.score > 0.6 ? 'bg-blue-500' : 'bg-orange-500'
                                }`}
                                style={{ width: `${recommendation.score * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-bold text-gray-800">
                              {(recommendation.score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="grid grid-cols-2 gap-0 border-t border-gray-100">
                      <button 
                        className="p-3 text-green-600 hover:bg-green-50 transition-colors font-semibold text-sm flex items-center justify-center gap-2"
                        onClick={(e) => {
                          e.stopPropagation()
                          // Handle accept
                          console.log('Accept load:', load.load_id)
                        }}
                      >
                        <CheckCircle className="w-4 h-4" />
                        Accept
                      </button>
                      <button 
                        className="p-3 text-gray-500 hover:bg-gray-50 transition-colors font-semibold text-sm flex items-center justify-center gap-2 border-l border-gray-100"
                        onClick={(e) => {
                          e.stopPropagation()
                          // Handle reject
                          console.log('Reject load:', load.load_id)
                        }}
                      >
                        <XCircle className="w-4 h-4" />
                        Reject
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* Load Details Modal */}
      {showLoadDetails && selectedLoad && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-4">
          <div className="bg-white rounded-t-3xl sm:rounded-3xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
              <h3 className="font-bold text-lg text-gray-800">Load Details</h3>
              <button 
                onClick={() => setShowLoadDetails(false)}
                className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-xl">
                <div className="text-sm text-gray-600 mb-1">Load ID</div>
                <div className="font-bold text-xl text-gray-800">{selectedLoad.load_id}</div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-50 p-4 rounded-xl">
                  <div className="text-xs text-gray-500 mb-1">Distance</div>
                  <div className="font-bold text-gray-800">{selectedLoad.distance_km.toFixed(0)} km</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-xl">
                  <div className="text-xs text-gray-500 mb-1">Weight</div>
                  <div className="font-bold text-gray-800">{selectedLoad.weight_tons.toFixed(1)} tons</div>
                </div>
                <div className="bg-green-50 p-4 rounded-xl">
                  <div className="text-xs text-green-600 mb-1">Revenue</div>
                  <div className="font-bold text-green-700">rupees {((selectedLoad.offered_rate_per_km || 0) * (selectedLoad.distance_km || 0)).toFixed(0)}</div>
                </div>
                <div className="bg-blue-50 p-4 rounded-xl">
                  <div className="text-xs text-blue-600 mb-1">Rate/km</div>
                  <div className="font-bold text-blue-700">rupees {selectedLoad.offered_rate_per_km.toFixed(2)}</div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="border-l-4 border-blue-500 pl-3">
                  <div className="text-xs text-gray-500">Origin</div>
                  <div className="font-semibold text-gray-800">{selectedLoad.origin.name}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    {selectedLoad.origin.lat.toFixed(4)}, {selectedLoad.origin.lng.toFixed(4)}
                  </div>
                </div>

                <div className="border-l-4 border-green-500 pl-3">
                  <div className="text-xs text-gray-500">Destination</div>
                  <div className="font-semibold text-gray-800">{selectedLoad.destination.name}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    {selectedLoad.destination.lat.toFixed(4)}, {selectedLoad.destination.lng.toFixed(4)}
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-yellow-800 mb-1">AI Recommendation</div>
                    <div className="text-sm text-yellow-700">
                      {getAIRecommendation(selectedLoad).reason}
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-4">
                <button 
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-6 rounded-xl transition-colors flex items-center justify-center gap-2"
                  onClick={() => {
                    // Handle accept
                    console.log('Accept load:', selectedLoad.load_id)
                    setShowLoadDetails(false)
                  }}
                >
                  <CheckCircle className="w-5 h-5" />
                  Accept Load
                </button>
                <button 
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-4 px-6 rounded-xl transition-colors flex items-center justify-center gap-2"
                  onClick={() => {
                    // Handle reject
                    console.log('Reject load:', selectedLoad.load_id)
                    setShowLoadDetails(false)
                  }}
                >
                  <XCircle className="w-5 h-5" />
                  Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg">
        <div className="grid grid-cols-3 gap-0">
          <button className="p-4 flex flex-col items-center gap-1 text-blue-600 bg-blue-50 border-t-2 border-blue-600">
            <Truck className="w-5 h-5" />
            <span className="text-xs font-semibold">Loads</span>
          </button>
          <button className="p-4 flex flex-col items-center gap-1 text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-colors">
            <MapPin className="w-5 h-5" />
            <span className="text-xs font-medium">Map</span>
          </button>
          <button className="p-4 flex flex-col items-center gap-1 text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-colors">
            <TrendingUp className="w-5 h-5" />
            <span className="text-xs font-medium">Earnings</span>
          </button>
        </div>
      </div>
    </div>
  )
}
