import { Clock, TrendingUp, Fuel, AlertTriangle, CheckCircle, Navigation } from 'lucide-react'
import { useEffect, useState } from 'react'

interface Prediction {
  vehicle_id: string
  load_id: string
  current_progress: number
  remaining_distance_km: number
  eta_hours: number
  eta_timestamp: number
  current_speed_kmh: number
  fuel_remaining: number
  estimated_fuel_cost: number
  on_time_status: 'on-time' | 'delayed'
  recommendations: Array<{
    type: string
    priority: string
    message: string
  }>
}

interface Props {
  predictions: Prediction[]
  onSimulate: () => void
  isSimulating: boolean
}

export default function LivePredictionPanel({ predictions, onSimulate, isSimulating }: Props) {
  const [localTime, setLocalTime] = useState(Date.now())

  useEffect(() => {
    const interval = setInterval(() => setLocalTime(Date.now()), 1000)
    return () => clearInterval(interval)
  }, [])

  const formatETA = (etaTimestamp: number) => {
    const diff = etaTimestamp - Date.now() / 1000
    const hours = Math.floor(diff / 3600)
    const minutes = Math.floor((diff % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const formatTime = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString()
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
            <Navigation className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-800">Live Predictions</h3>
            <p className="text-sm text-gray-500">Real-time route analysis</p>
          </div>
        </div>
        <button
          onClick={onSimulate}
          disabled={isSimulating}
          className={`px-4 py-2 rounded-lg font-medium transition-all ${
            isSimulating
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:shadow-lg transform hover:scale-105'
          }`}
        >
          {isSimulating ? (
            <span className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Simulating...
            </span>
          ) : (
            'Simulate Movement'
          )}
        </button>
      </div>

      {predictions.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <Navigation className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <p className="text-lg">No active trips to predict</p>
          <p className="text-sm">Match loads to vehicles to see predictions</p>
        </div>
      ) : (
        <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
          {predictions.map((pred, idx) => (
            <div
              key={idx}
              className="border-2 border-gray-100 rounded-xl p-4 hover:border-blue-200 transition-all bg-gradient-to-br from-white to-gray-50"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-4 pb-3 border-b">
                <div>
                  <div className="font-bold text-gray-800">{pred.vehicle_id}</div>
                  <div className="text-sm text-gray-500">{pred.load_id}</div>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    pred.on_time_status === 'on-time'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {pred.on_time_status === 'on-time' ? '✓ On Time' : '⚠ Delayed'}
                </span>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600">Trip Progress</span>
                  <span className="font-bold text-blue-600">{pred.current_progress.toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-1000 relative"
                    style={{ width: `${pred.current_progress}%` }}
                  >
                    <div className="absolute inset-0 bg-white opacity-30 animate-pulse"></div>
                  </div>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-blue-50 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Clock className="w-4 h-4 text-blue-600" />
                    <span className="text-xs text-gray-600">ETA</span>
                  </div>
                  <div className="font-bold text-blue-700">{formatETA(pred.eta_timestamp)}</div>
                  <div className="text-xs text-gray-500">{formatTime(pred.eta_timestamp)}</div>
                </div>

                <div className="bg-green-50 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <TrendingUp className="w-4 h-4 text-green-600" />
                    <span className="text-xs text-gray-600">Speed</span>
                  </div>
                  <div className="font-bold text-green-700">{pred.current_speed_kmh} km/h</div>
                  <div className="text-xs text-gray-500">Average</div>
                </div>

                <div className="bg-purple-50 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Navigation className="w-4 h-4 text-purple-600" />
                    <span className="text-xs text-gray-600">Remaining</span>
                  </div>
                  <div className="font-bold text-purple-700">
                    {pred.remaining_distance_km.toFixed(0)} km
                  </div>
                  <div className="text-xs text-gray-500">Distance</div>
                </div>

                <div className="bg-orange-50 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Fuel className="w-4 h-4 text-orange-600" />
                    <span className="text-xs text-gray-600">Fuel</span>
                  </div>
                  <div className="font-bold text-orange-700">{pred.fuel_remaining.toFixed(0)}%</div>
                  <div className="text-xs text-gray-500">${pred.estimated_fuel_cost.toFixed(0)} cost</div>
                </div>
              </div>

              {/* Recommendations */}
              {pred.recommendations.length > 0 && (
                <div className="space-y-2">
                  {pred.recommendations.map((rec, recIdx) => (
                    <div
                      key={recIdx}
                      className={`flex items-center gap-3 p-2 rounded-lg text-sm ${
                        rec.priority === 'high'
                          ? 'bg-red-50 text-red-700 border border-red-200'
                          : rec.type === 'delivery'
                          ? 'bg-green-50 text-green-700 border border-green-200'
                          : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
                      }`}
                    >
                      {rec.priority === 'high' ? (
                        <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                      ) : (
                        <CheckCircle className="w-4 h-4 flex-shrink-0" />
                      )}
                      <span className="font-medium">{rec.message}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
