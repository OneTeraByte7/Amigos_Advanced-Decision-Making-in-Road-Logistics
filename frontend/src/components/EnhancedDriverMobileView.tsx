import { useState, useEffect } from 'react'
import { Truck, MapPin, Package, Clock, CheckCircle, XCircle, AlertTriangle, Navigation, DollarSign, Fuel, TrendingUp, ArrowLeft, ChevronRight, Star } from 'lucide-react'
import { FleetState, Load, Vehicle } from '../types'
import { api } from '../services/api'

interface Props {
  fleetState: FleetState | null
  driverId?: string
  onBack?: () => void
}

interface AILoadRecommendation {
  load_id: string
  score: number
  reason: string
  priority: 'high' | 'medium' | 'low'
  estimated_profit: number
  pros: string[]
  cons: string[]
}

export default function EnhancedDriverMobileView({ fleetState, driverId = 'driver_001', onBack }: Props) {
  const [selectedLoad, setSelectedLoad] = useState<Load | null>(null)
  const [showLoadDetails, setShowLoadDetails] = useState(false)
  const [recommendations, setRecommendations] = useState<AILoadRecommendation[]>([])
  const [metrics, setMetrics] = useState<any>(null)

  // Find driver's vehicle
  const myVehicle = fleetState?.vehicles?.find(v => v.driver_id === driverId)
  const myTrip = myVehicle ? fleetState?.trips?.find(t => t.vehicle_id === myVehicle.vehicle_id) : null
  const myLoad = myTrip ? fleetState?.loads?.find(l => l.load_id === myTrip.load_id) : null

  // Get available loads for driver
  const availableLoads = fleetState?.loads?.filter(l => l.status === 'available') || []

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await api.getMetrics()
        setMetrics(data)
      } catch (error) {
        console.error('Failed to fetch metrics:', error)
      }
    }
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 3000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    // Generate AI recommendations for available loads
    if (myVehicle && availableLoads.length > 0) {
      const recs = availableLoads.map(load => generateAIRecommendation(load, myVehicle))
      setRecommendations(recs.sort((a, b) => b.score - a.score))
    }
  }, [availableLoads, myVehicle])

  const generateAIRecommendation = (load: Load, vehicle: Vehicle): AILoadRecommendation => {
    const revenue = load.offered_rate_per_km * load.distance_km
    const fuelCost = load.distance_km * 0.5 // Rough estimate
    const profit = revenue - fuelCost

    // Scoring factors
    const distanceScore = load.distance_km < 500 ? 0.9 : load.distance_km < 1000 ? 0.7 : 0.5
    const revenueScore = load.offered_rate_per_km > 12 ? 0.9 : load.offered_rate_per_km > 8 ? 0.7 : 0.5
    const capacityMatch = load.weight_tons <= vehicle.capacity_tons * 0.9 ? 1.0 : 0.6
    const fuelScore = vehicle.fuel_level_percent > 50 ? 0.9 : 0.6

    const finalScore = (distanceScore * 0.3 + revenueScore * 0.3 + capacityMatch * 0.2 + fuelScore * 0.2)

    const pros: string[] = []
    const cons: string[] = []

    if (load.offered_rate_per_km > 10) pros.push('High paying rate')
    if (load.distance_km < 500) pros.push('Short distance')
    if (load.weight_tons <= vehicle.capacity_tons * 0.7) pros.push('Light load')
    
    if (load.distance_km > 1000) cons.push('Long distance')
    if (vehicle.fuel_level_percent < 40) cons.push('Low fuel - refuel needed')
    if (load.weight_tons > vehicle.capacity_tons * 0.9) cons.push('Heavy load')

    let priority: 'high' | 'medium' | 'low'
    let reason: string

    if (finalScore > 0.8) {
      priority = 'high'
      reason = '🎯 Highly Recommended - Optimal route and excellent revenue'
    } else if (finalScore > 0.6) {
      priority = 'medium'
      reason = '✅ Good Match - Acceptable terms, consider taking'
    } else {
      priority = 'low'
      reason = '⚠️ Low Priority - Better opportunities may be available'
    }

    return {
      load_id: load.load_id,
      score: finalScore,
      reason,
      priority,
      estimated_profit: profit,
      pros,
      cons
    }
  }

  const handleAcceptLoad = async (load: Load) => {
    // In a real system, this would call an API endpoint
    alert(`Load ${load.load_id} accepted! Waiting for dispatch confirmation...`)
    setShowLoadDetails(false)
    setSelectedLoad(null)
  }

  const handleRejectLoad = (load: Load) => {
    alert(`Load ${load.load_id} rejected.`)
    setShowLoadDetails(false)
    setSelectedLoad(null)
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20" style={{ maxWidth: '480px', margin: '0 auto' }}>
      {/* Top Header - Fixed */}
      <div className="sticky top-0 z-50 bg-gradient-to-r from-blue-600 to-indigo-700 text-white shadow-lg">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {onBack && (
                <button
                  onClick={onBack}
                  className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm hover:bg-white/30 transition-colors active:scale-95"
                  aria-label="Back to Fleet View"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
              )}
              <div className="w-11 h-11 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <Truck className="w-6 h-6" />
              </div>
              <div>
                <h1 className="font-bold text-base">Driver Portal</h1>
                <p className="text-xs text-blue-100">{myVehicle?.vehicle_id || driverId}</p>
              </div>
            </div>
            <div className="bg-green-500/30 backdrop-blur-sm px-3 py-1.5 rounded-full border border-green-400/50">
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 bg-green-300 rounded-full animate-pulse"></div>
                <span className="text-xs font-semibold">Online</span>
              </div>
            </div>
          </div>
        </div>

        {/* Driver Stats Bar */}
        {myVehicle && (
          <div className="px-4 pb-3 grid grid-cols-3 gap-2">
            <div className="bg-white/10 rounded-lg p-2 backdrop-blur-sm">
              <div className="flex items-center gap-1 text-xs opacity-90 mb-0.5">
                <Fuel className="w-3 h-3" />
                Fuel
              </div>
              <div className="text-lg font-bold">{myVehicle.fuel_level_percent.toFixed(0)}%</div>
            </div>
            <div className="bg-white/10 rounded-lg p-2 backdrop-blur-sm">
              <div className="flex items-center gap-1 text-xs opacity-90 mb-0.5">
                <Navigation className="w-3 h-3" />
                Distance
              </div>
              <div className="text-lg font-bold">{myVehicle.total_km_today.toFixed(0)}km</div>
            </div>
            <div className="bg-white/10 rounded-lg p-2 backdrop-blur-sm">
              <div className="flex items-center gap-1 text-xs opacity-90 mb-0.5">
                <Clock className="w-3 h-3" />
                Hours
              </div>
              <div className="text-lg font-bold">{myVehicle.max_driving_hours_remaining.toFixed(1)}h</div>
            </div>
          </div>
        )}
      </div>

      {/* Active Trip Card */}
      {myLoad && myTrip && (
        <div className="m-4">
          <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl shadow-xl overflow-hidden text-white">
            <div className="p-5">
              {/* Status Badge */}
              <div className="flex items-center justify-between mb-4">
                <div className="bg-white/20 backdrop-blur-sm px-3 py-1.5 rounded-full flex items-center gap-2">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  <span className="text-xs font-bold uppercase">Active Trip</span>
                </div>
                <div className="text-2xl font-black">{myTrip.progress_percent?.toFixed(0) || 0}%</div>
              </div>

              {/* Route Info */}
              <div className="space-y-2 mb-4">
                <div className="flex items-start gap-2 bg-white/10 rounded-xl p-3 backdrop-blur-sm">
                  <div className="w-6 h-6 bg-white/30 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs opacity-80 mb-0.5">Pickup</div>
                    <div className="font-bold text-sm truncate">{myLoad.origin.name}</div>
                  </div>
                </div>

                <div className="flex justify-center">
                  <div className="w-0.5 h-6 bg-white/40"></div>
                </div>

                <div className="flex items-start gap-2 bg-white/10 rounded-xl p-3 backdrop-blur-sm">
                  <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <MapPin className="w-3.5 h-3.5 text-green-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs opacity-80 mb-0.5">Delivery</div>
                    <div className="font-bold text-sm truncate">{myLoad.destination.name}</div>
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="bg-white/20 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-white h-full rounded-full transition-all duration-500"
                    style={{ width: `${myTrip.progress_percent || 0}%` }}
                  ></div>
                </div>
              </div>

              {/* Trip Stats */}
              <div className="grid grid-cols-3 gap-2">
                <div className="bg-white/10 rounded-lg p-2 backdrop-blur-sm">
                  <div className="text-xs opacity-80">Distance</div>
                  <div className="font-bold text-sm">{myLoad.distance_km.toFixed(0)} km</div>
                </div>
                <div className="bg-white/10 rounded-lg p-2 backdrop-blur-sm">
                  <div className="text-xs opacity-80">Weight</div>
                  <div className="font-bold text-sm">{myLoad.weight_tons.toFixed(1)} tons</div>
                </div>
                <div className="bg-white/10 rounded-lg p-2 backdrop-blur-sm">
                  <div className="text-xs opacity-80">Profit</div>
                    <div className="font-bold text-sm">${((myTrip.estimated_profit ?? 0)).toFixed(0)}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Available Loads Section */}
      {!myLoad && (
        <div className="px-4 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-bold text-gray-900 text-lg flex items-center gap-2">
              <Package className="w-5 h-5 text-blue-600" />
              Available Loads
            </h2>
            <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold">
              {availableLoads.length}
            </span>
          </div>

          {availableLoads.length === 0 ? (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-12 text-center">
              <Package className="w-16 h-16 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-700 font-semibold text-lg mb-1">No loads available</p>
              <p className="text-sm text-gray-500">Check back later for new opportunities</p>
            </div>
          ) : (
            <div className="space-y-3 pb-4">
              {recommendations.map(rec => {
                const load = availableLoads.find(l => l.load_id === rec.load_id)
                if (!load) return null

                const priorityColors = {
                  high: 'border-green-400 bg-green-50',
                  medium: 'border-blue-400 bg-blue-50',
                  low: 'border-gray-300 bg-gray-50'
                }

                const priorityBadgeColors = {
                  high: 'bg-green-500 text-white',
                  medium: 'bg-blue-500 text-white',
                  low: 'bg-gray-400 text-white'
                }

                return (
                  <div 
                    key={load.load_id}
                    className={`rounded-2xl shadow-sm border-2 ${priorityColors[rec.priority]} transition-all active:scale-[0.98]`}
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
                            <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${priorityBadgeColors[rec.priority]}`}>
                              {rec.priority.toUpperCase()}
                            </span>
                            <div className="flex items-center gap-0.5">
                              {[...Array(5)].map((_, i) => (
                                <Star 
                                  key={i} 
                                  className={`w-3 h-3 ${i < rec.score * 5 ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}`} 
                                />
                              ))}
                            </div>
                          </div>
                          <p className="text-xs text-gray-700 font-medium">{rec.reason}</p>
                        </div>
                        <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0 mt-1" />
                      </div>

                      {/* Route */}
                      <div className="space-y-1.5 mb-3">
                        <div className="flex items-center gap-2 text-sm">
                          <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></div>
                          <span className="font-semibold text-gray-900 truncate">{load.origin.name}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <MapPin className="w-4 h-4 text-green-500 flex-shrink-0" />
                          <span className="font-semibold text-gray-900 truncate">{load.destination.name}</span>
                        </div>
                      </div>

                      {/* Stats */}
                      <div className="grid grid-cols-4 gap-2">
                        <div className="bg-white rounded-lg p-2 text-center">
                          <div className="text-xs text-gray-600">Distance</div>
                          <div className="font-bold text-sm text-gray-900">{load.distance_km.toFixed(0)}km</div>
                        </div>
                        <div className="bg-white rounded-lg p-2 text-center">
                          <div className="text-xs text-gray-600">Weight</div>
                          <div className="font-bold text-sm text-gray-900">{load.weight_tons.toFixed(1)}t</div>
                        </div>
                        <div className="bg-white rounded-lg p-2 text-center">
                          <div className="text-xs text-gray-600">Rate</div>
                          <div className="font-bold text-sm text-gray-900">${load.offered_rate_per_km.toFixed(1)}/km</div>
                        </div>
                        <div className="bg-green-100 rounded-lg p-2 text-center">
                          <div className="text-xs text-green-700">Profit</div>
                          <div className="font-bold text-sm text-green-700">${rec.estimated_profit.toFixed(0)}</div>
                        </div>
                      </div>
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
        <div className="fixed inset-0 bg-black/50 z-50 flex items-end" style={{ maxWidth: '480px', margin: '0 auto' }}>
          <div className="bg-white rounded-t-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-5 py-4 flex items-center justify-between">
              <h3 className="font-bold text-lg text-gray-900">Load Details</h3>
              <button 
                onClick={() => setShowLoadDetails(false)}
                className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center hover:bg-gray-200"
              >
                <XCircle className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            <div className="p-5 space-y-6">
              {/* AI Analysis */}
              {recommendations.find(r => r.load_id === selectedLoad.load_id) && (() => {
                const rec = recommendations.find(r => r.load_id === selectedLoad.load_id)!
                return (
                  <div className="bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 rounded-2xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-900">AI Analysis</h4>
                        <p className="text-xs text-gray-600">Based on your vehicle capacity, fuel, and route</p>
                      </div>
                    </div>

                    <div className="bg-white rounded-xl p-3 mb-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-gray-700">Match Score</span>
                        <span className="text-lg font-black text-purple-600">{(rec.score * 100).toFixed(0)}%</span>
                      </div>
                      <div className="bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-purple-500 to-blue-500 h-full rounded-full"
                          style={{ width: `${rec.score * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {rec.pros.length > 0 && (
                      <div className="bg-green-50 border border-green-200 rounded-xl p-3 mb-2">
                        <div className="font-semibold text-green-800 text-sm mb-2 flex items-center gap-1">
                          <CheckCircle className="w-4 h-4" />
                          Pros
                        </div>
                        <ul className="space-y-1">
                          {rec.pros.map((pro, i) => (
                            <li key={i} className="text-sm text-green-700 flex items-center gap-2">
                              <div className="w-1 h-1 bg-green-500 rounded-full"></div>
                              {pro}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {rec.cons.length > 0 && (
                      <div className="bg-orange-50 border border-orange-200 rounded-xl p-3">
                        <div className="font-semibold text-orange-800 text-sm mb-2 flex items-center gap-1">
                          <AlertTriangle className="w-4 h-4" />
                          Considerations
                        </div>
                        <ul className="space-y-1">
                          {rec.cons.map((con, i) => (
                            <li key={i} className="text-sm text-orange-700 flex items-center gap-2">
                              <div className="w-1 h-1 bg-orange-500 rounded-full"></div>
                              {con}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )
              })()}

              {/* Load Information */}
              <div className="space-y-3">
                <h4 className="font-bold text-gray-900">Load Information</h4>
                
                <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Load ID</span>
                    <span className="font-mono font-semibold text-gray-900">{selectedLoad.load_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Distance</span>
                    <span className="font-semibold text-gray-900">{selectedLoad.distance_km.toFixed(1)} km</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Weight</span>
                    <span className="font-semibold text-gray-900">{selectedLoad.weight_tons.toFixed(1)} tons</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Rate</span>
                    <span className="font-semibold text-gray-900">${selectedLoad.offered_rate_per_km.toFixed(2)}/km</span>
                  </div>
                  <div className="flex justify-between border-t border-gray-200 pt-3">
                    <span className="text-gray-900 font-semibold">Total Revenue</span>
                    <span className="font-bold text-green-600 text-lg">
                      ${(selectedLoad.offered_rate_per_km * selectedLoad.distance_km).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-3 pt-4">
                <button
                  onClick={() => handleRejectLoad(selectedLoad)}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-900 px-6 py-4 rounded-xl font-bold text-base transition-colors active:scale-95 flex items-center justify-center gap-2"
                >
                  <XCircle className="w-5 h-5" />
                  Reject
                </button>
                <button
                  onClick={() => handleAcceptLoad(selectedLoad)}
                  className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white px-6 py-4 rounded-xl font-bold text-base shadow-lg transition-all active:scale-95 flex items-center justify-center gap-2"
                >
                  <CheckCircle className="w-5 h-5" />
                  Accept Load
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
