import { useState, useEffect } from 'react'
import { Truck, Zap, MapPin, Package, Activity, Globe, Sparkles, Smartphone, Monitor, Clock, TrendingUp } from 'lucide-react'
import EnhancedFleetMap from './components/EnhancedFleetMap'
import AgentControl from './components/AgentControl'
import ProfessionalMetricsDashboard from './components/ProfessionalMetricsDashboard'
import ProfessionalEventTimeline from './components/ProfessionalEventTimeline'
import ProfessionalLoadMatchingPanel from './components/ProfessionalLoadMatchingPanel'
import LivePredictionPanel from './components/LivePredictionPanel'
import DriverMobileView from './components/DriverMobileView'
import { api } from './services/api'
import { FleetState, FleetMetrics } from './types'

function App() {
  const [fleetState, setFleetState] = useState<FleetState | null>(null)
  const [metrics, setMetrics] = useState<FleetMetrics | null>(null)
  const [predictions, setPredictions] = useState<any[]>([])
  const [isInitialized, setIsInitialized] = useState(false)
  const [loading, setLoading] = useState(false)
  const [isSimulating, setIsSimulating] = useState(false)
  const [activeView, setActiveView] = useState<'fleet' | 'driver'>('fleet')
  const [activeTab, setActiveTab] = useState<'map' | 'matching' | 'timeline'>('map')

  useEffect(() => {
    checkInitialization()
    const interval = setInterval(refreshData, 2000)
    return () => clearInterval(interval)
  }, [isInitialized])

  useEffect(() => {
    if (!isInitialized) return
    
    const simulationInterval = setInterval(async () => {
      await handleSimulateMovement()
    }, 3000)
    
    return () => clearInterval(simulationInterval)
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
      // Not initialized yet
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
      // Handle error silently
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

  const handleSimulateMovement = async () => {
    if (isSimulating || !isInitialized) return
    
    try {
      setIsSimulating(true)
      const result = await api.simulateMovement()
      setPredictions(result.predictions || [])
      await refreshData()
    } catch (error) {
      // Handle error silently
    } finally {
      setIsSimulating(false)
    }
  }

  // Splash Screen - Not Initialized
  if (!isInitialized) {
    return (
      <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900">
        {/* Animated Background */}
        <div className="absolute inset-0">
          <div className="absolute top-20 left-20 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>

        <div className="relative min-h-screen flex items-center justify-center p-8">
          <div className="max-w-2xl w-full">
            <div className="backdrop-blur-xl bg-white/10 rounded-3xl border border-white/20 shadow-2xl p-12">
              {/* Logo */}
              <div className="text-center mb-8">
                <div className="relative inline-block mb-6">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-600 rounded-2xl blur-2xl opacity-50"></div>
                  <div className="relative bg-gradient-to-r from-blue-500 to-purple-600 p-6 rounded-2xl">
                    <Truck className="w-20 h-20 text-white" strokeWidth={1.5} />
                  </div>
                </div>
                
                <h1 className="text-5xl font-black tracking-tight text-white mb-4">
                  ADAPTIVE LOGISTICS
                </h1>
                
                <p className="text-xl text-gray-300 font-light">
                  AI-Powered Fleet Intelligence Platform
                </p>
              </div>

              {/* Features */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="backdrop-blur-sm bg-white/5 rounded-xl p-4 border border-white/10">
                  <div className="bg-blue-500 w-10 h-10 rounded-lg flex items-center justify-center mb-3">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-white font-semibold mb-1">Real-time AI</h3>
                  <p className="text-gray-400 text-sm">Adaptive route optimization</p>
                </div>

                <div className="backdrop-blur-sm bg-white/5 rounded-xl p-4 border border-white/10">
                  <div className="bg-purple-500 w-10 h-10 rounded-lg flex items-center justify-center mb-3">
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-white font-semibold mb-1">Smart Matching</h3>
                  <p className="text-gray-400 text-sm">LLM-powered decisions</p>
                </div>

                <div className="backdrop-blur-sm bg-white/5 rounded-xl p-4 border border-white/10">
                  <div className="bg-emerald-500 w-10 h-10 rounded-lg flex items-center justify-center mb-3">
                    <Globe className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-white font-semibold mb-1">Live Tracking</h3>
                  <p className="text-gray-400 text-sm">Real-time monitoring</p>
                </div>
              </div>

              {/* Initialize Button */}
              <button
                onClick={handleInitialize}
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-6 rounded-2xl font-bold text-xl hover:shadow-2xl transform hover:scale-[1.02] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-3">
                    <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                    Initializing Fleet System...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-3">
                    <Zap className="w-6 h-6" />
                    Launch Fleet Intelligence
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Driver Mobile View
  if (activeView === 'driver') {
    return (
      <div className="min-h-screen bg-gray-50">
        <DriverMobileView 
          fleetState={fleetState} 
          onBack={() => setActiveView('fleet')}
        />
      </div>
    )
  }

  // Fleet Management View
  return (
    <div className="min-h-screen bg-white">
      {/* Top Navigation */}
      <nav className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-4">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-2.5 rounded-xl">
                <Truck className="w-6 h-6 text-white" strokeWidth={2} />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">
                  Adaptive Logistics
                </h1>
                <p className="text-xs text-gray-500">Fleet Intelligence Platform</p>
              </div>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-blue-50 px-3 py-2 rounded-lg border border-blue-100">
                <Truck className="w-4 h-4 text-blue-600" />
                <div>
                  <div className="text-xs text-gray-500">Vehicles</div>
                  <div className="text-sm font-bold text-gray-800">{fleetState?.vehicles.length || 0}</div>
                </div>
              </div>
              
              <div className="flex items-center gap-2 bg-green-50 px-3 py-2 rounded-lg border border-green-100">
                <Package className="w-4 h-4 text-green-600" />
                <div>
                  <div className="text-xs text-gray-500">Active Loads</div>
                  <div className="text-sm font-bold text-gray-800">{metrics?.matched_loads || 0}</div>
                </div>
              </div>

              <div className="flex items-center gap-2 bg-purple-50 px-3 py-2 rounded-lg border border-purple-100">
                <TrendingUp className="w-4 h-4 text-purple-600" />
                <div>
                  <div className="text-xs text-gray-500">Efficiency</div>
                  <div className="text-sm font-bold text-gray-800">
                    {metrics ? (metrics.avg_utilization ?? 0).toFixed(0) : 0}%
                  </div>
                </div>
              </div>

              <button
                onClick={() => setActiveView('driver')}
                className="ml-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold text-sm flex items-center gap-2 transition-colors"
              >
                <Smartphone className="w-4 h-4" />
                Driver View
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex items-center gap-1 -mb-px">
            <button
              onClick={() => setActiveTab('map')}
              className={`px-6 py-3 font-semibold text-sm border-b-2 transition-colors ${
                activeTab === 'map'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                Live Fleet Map
              </div>
            </button>
            <button
              onClick={() => setActiveTab('matching')}
              className={`px-6 py-3 font-semibold text-sm border-b-2 transition-colors ${
                activeTab === 'matching'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <div className="flex items-center gap-2">
                <Package className="w-4 h-4" />
                Load Matching
              </div>
            </button>
            <button
              onClick={() => setActiveTab('timeline')}
              className={`px-6 py-3 font-semibold text-sm border-b-2 transition-colors ${
                activeTab === 'timeline'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Events Timeline
              </div>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-6">
        {activeTab === 'map' && (
          <div className="space-y-6">
            {/* Metrics Dashboard */}
            {metrics && <ProfessionalMetricsDashboard metrics={metrics} />}

            {/* Map and Controls Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Map */}
              <div className="lg:col-span-2">
                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                  <div className="h-[600px]">
                    <EnhancedFleetMap fleetState={fleetState} />
                  </div>
                </div>
              </div>

              {/* Right Sidebar */}
              <div className="space-y-6">
                {/* Agent Controls */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                  <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-blue-600" />
                    AI Agent Controls
                  </h3>
                  <AgentControl onRefresh={refreshData} />
                </div>

                {/* Live Predictions */}
                <LivePredictionPanel 
                  predictions={predictions} 
                  onSimulate={handleSimulateMovement} 
                  isSimulating={isSimulating} 
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'matching' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <ProfessionalLoadMatchingPanel fleetState={fleetState} />
            </div>
          </div>
        )}

        {activeTab === 'timeline' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <ProfessionalEventTimeline events={fleetState?.events || []} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
