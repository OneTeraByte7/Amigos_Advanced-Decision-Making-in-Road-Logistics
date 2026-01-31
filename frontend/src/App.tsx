import { useState, useEffect } from 'react'
import { Truck, Activity, Zap, TrendingUp, MapPin, Package, Radio } from 'lucide-react'
import EnhancedFleetMap from './components/EnhancedFleetMap'
import AgentControl from './components/AgentControl'
import MetricsDashboard from './components/MetricsDashboard'
import EventTimeline from './components/EventTimeline'
import LoadMatchingPanel from './components/LoadMatchingPanel'
import { api } from './services/api'
import { FleetState, FleetMetrics } from './types'

function App() {
  const [fleetState, setFleetState] = useState<FleetState | null>(null)
  const [metrics, setMetrics] = useState<FleetMetrics | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  const [loading, setLoading] = useState(false)
  const [activeView, setActiveView] = useState<'map' | 'matching' | 'timeline'>('map')

  useEffect(() => {
    checkInitialization()
    const interval = setInterval(refreshData, 2000) // Update every 2 seconds for smooth animation
    return () => clearInterval(interval)
  }, [isInitialized])

  const checkInitialization = async () => {
    try {
      const state = await api.getState()
      if (state.vehicles && state.vehicles.length > 0) {
        setIsInitialized(true)
        setFleetState(state)
        const metricsData = await api.getMetrics()
        setMetrics(metricsData)
      }
    } catch (error) {
      console.log('Not initialized yet')
    }
  }

  const refreshData = async () => {
    if (!isInitialized) return
    try {
      const state = await api.getState()
      setFleetState(state)
      const metricsData = await api.getMetrics()
      setMetrics(metricsData)
    } catch (error) {
      console.error('Error refreshing data:', error)
    }
  }

  const handleInitialize = async () => {
    setLoading(true)
    try {
      await api.initialize()
      await checkInitialization()
    } catch (error) {
      console.error('Initialization error:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center space-y-6 p-8 bg-white rounded-2xl shadow-2xl max-w-md">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full blur-3xl opacity-20 animate-pulse-slow"></div>
            <Truck className="w-24 h-24 mx-auto text-blue-600 relative z-10" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Adaptive Logistics
          </h1>
          <p className="text-gray-600 text-lg">
            AI-Powered Fleet Management System
          </p>
          <div className="space-y-3 pt-4">
            <div className="flex items-center gap-3 text-left">
              <Zap className="w-5 h-5 text-yellow-500" />
              <span className="text-sm text-gray-700">Real-time Route Adaptation</span>
            </div>
            <div className="flex items-center gap-3 text-left">
              <Activity className="w-5 h-5 text-green-500" />
              <span className="text-sm text-gray-700">AI-Powered Load Matching</span>
            </div>
            <div className="flex items-center gap-3 text-left">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              <span className="text-sm text-gray-700">Continuous Fleet Monitoring</span>
            </div>
          </div>
          <button
            onClick={handleInitialize}
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Initializing Fleet...
              </span>
            ) : (
              'Initialize Fleet System'
            )}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Truck className="w-8 h-8" />
              <div>
                <h1 className="text-2xl font-bold">Adaptive Logistics</h1>
                <p className="text-blue-100 text-sm">AI-Powered Fleet Management</p>
              </div>
            </div>
            <div className="flex gap-4 items-center">
              <div className="text-right">
                <div className="text-sm text-blue-100">Fleet Size</div>
                <div className="text-2xl font-bold">{fleetState?.vehicles.length || 0}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-blue-100">Active Loads</div>
                <div className="text-2xl font-bold">{metrics?.matched_loads || 0}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-blue-100">Utilization</div>
                <div className="text-2xl font-bold">{metrics?.avg_utilization ? metrics.avg_utilization.toFixed(0) : 0}%</div>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-white/20 rounded-lg">
                <Radio className="w-4 h-4 animate-pulse text-green-400" />
                <span className="text-sm">Live Tracking</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="p-4 bg-gradient-to-r from-gray-50 to-white border-b flex gap-2">
                <button
                  onClick={() => setActiveView('map')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    activeView === 'map'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-white text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <MapPin className="w-4 h-4" />
                  Live Map
                </button>
                <button
                  onClick={() => setActiveView('matching')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    activeView === 'matching'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-white text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Package className="w-4 h-4" />
                  Load Matching
                </button>
                <button
                  onClick={() => setActiveView('timeline')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    activeView === 'timeline'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-white text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Activity className="w-4 h-4" />
                  Events
                </button>
              </div>
              <div className="h-[600px]">
                {activeView === 'map' && fleetState && <EnhancedFleetMap fleetState={fleetState} />}
                {activeView === 'matching' && fleetState && <LoadMatchingPanel fleetState={fleetState} />}
                {activeView === 'timeline' && fleetState && <EventTimeline events={fleetState.events || []} />}
              </div>
            </div>

            {metrics && <MetricsDashboard metrics={metrics} />}
          </div>

          <div className="space-y-6">
            <AgentControl onRefresh={refreshData} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App