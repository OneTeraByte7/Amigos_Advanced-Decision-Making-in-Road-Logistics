import { useState, useEffect } from 'react'
import { Truck, Zap, TrendingUp, MapPin, Package, Radio, Gauge, Activity, BarChart3, Globe, Sparkles } from 'lucide-react'
import EnhancedFleetMap from './components/EnhancedFleetMap'
import AgentControl from './components/AgentControl'
import ProfessionalMetricsDashboard from './components/ProfessionalMetricsDashboard'
import ProfessionalEventTimeline from './components/ProfessionalEventTimeline'
import ProfessionalLoadMatchingPanel from './components/ProfessionalLoadMatchingPanel'
import LivePredictionPanel from './components/LivePredictionPanel'
import { api } from './services/api'
import { FleetState, FleetMetrics } from './types'

function App() {
  const [fleetState, setFleetState] = useState<FleetState | null>(null)
  const [metrics, setMetrics] = useState<FleetMetrics | null>(null)
  const [predictions, setPredictions] = useState<any[]>([])
  const [isInitialized, setIsInitialized] = useState(false)
  const [loading, setLoading] = useState(false)
  const [isSimulating, setIsSimulating] = useState(false)
  const [activeView, setActiveView] = useState<'map' | 'matching' | 'timeline'>('map')

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
      // console.log('Not initialized yet')
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
      // Silently handle refresh errors when not initialized
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
      // Silently handle simulation errors
    } finally {
      setIsSimulating(false)
    }
  }

  if (!isInitialized) {
    return (
      <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-950 via-blue-950 to-purple-950">
        {/* Animated Background */}
        <div className="absolute inset-0">
          <div className="absolute top-20 left-20 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        </div>

        {/* Grid Pattern Overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:100px_100px]"></div>

        <div className="relative min-h-screen flex items-center justify-center p-8">
          <div className="max-w-2xl w-full">
            {/* Glass Card */}
            <div className="backdrop-blur-xl bg-white/10 rounded-3xl border border-white/20 shadow-2xl p-12">
              {/* Logo Area */}
              <div className="text-center mb-8">
                <div className="relative inline-block">
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 rounded-2xl blur-2xl opacity-50 animate-pulse"></div>
                  <div className="relative bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 p-6 rounded-2xl">
                    <Truck className="w-20 h-20 text-white" strokeWidth={1.5} />
                  </div>
                </div>
                
                <h1 className="mt-8 text-6xl font-black tracking-tight">
                  <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                    ADAPTIVE
                  </span>
                  <br />
                  <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-red-400 bg-clip-text text-transparent">
                    LOGISTICS
                  </span>
                </h1>
                
                <p className="mt-4 text-xl text-gray-300 font-light">
                  Next-Generation Fleet Intelligence Platform
                </p>
              </div>

              {/* Features Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="backdrop-blur-sm bg-white/5 rounded-xl p-4 border border-white/10 hover:bg-white/10 transition-all duration-300">
                  <div className="bg-gradient-to-br from-cyan-500 to-blue-600 w-10 h-10 rounded-lg flex items-center justify-center mb-3">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-white font-semibold mb-1">Real-time AI</h3>
                  <p className="text-gray-400 text-sm">Adaptive route optimization</p>
                </div>

                <div className="backdrop-blur-sm bg-white/5 rounded-xl p-4 border border-white/10 hover:bg-white/10 transition-all duration-300">
                  <div className="bg-gradient-to-br from-purple-500 to-pink-600 w-10 h-10 rounded-lg flex items-center justify-center mb-3">
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-white font-semibold mb-1">Smart Matching</h3>
                  <p className="text-gray-400 text-sm">LLM-powered decisions</p>
                </div>

                <div className="backdrop-blur-sm bg-white/5 rounded-xl p-4 border border-white/10 hover:bg-white/10 transition-all duration-300">
                  <div className="bg-gradient-to-br from-emerald-500 to-teal-600 w-10 h-10 rounded-lg flex items-center justify-center mb-3">
                    <Globe className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-white font-semibold mb-1">Live Tracking</h3>
                  <p className="text-gray-400 text-sm">Real-time fleet monitoring</p>
                </div>
              </div>

              {/* Initialize Button */}
              <button
                onClick={handleInitialize}
                disabled={loading}
                className="w-full group relative overflow-hidden bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 text-white px-8 py-6 rounded-2xl font-bold text-xl hover:shadow-2xl hover:shadow-blue-500/50 transform hover:scale-[1.02] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <span className="relative flex items-center justify-center gap-3">
                  {loading ? (
                    <>
                      <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                      Initializing Fleet System...
                    </>
                  ) : (
                    <>
                      <Zap className="w-6 h-6" />
                      Launch Fleet Intelligence
                    </>
                  )}
                </span>
              </button>

              {/* Tech Specs */}
              <div className="mt-8 pt-8 border-t border-white/10">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-cyan-400 text-2xl font-bold">5+</div>
                    <div className="text-gray-400 text-xs">AI Agents</div>
                  </div>
                  <div>
                    <div className="text-purple-400 text-2xl font-bold">24/7</div>
                    <div className="text-gray-400 text-xs">Monitoring</div>
                  </div>
                  <div>
                    <div className="text-pink-400 text-2xl font-bold">∞</div>
                    <div className="text-gray-400 text-xs">Scalability</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer Badge */}
            <div className="mt-6 text-center">
              <div className="inline-flex items-center gap-2 backdrop-blur-sm bg-white/5 px-4 py-2 rounded-full border border-white/10">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-400">Powered by Groq AI • Real-time Analytics</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Top Navigation Bar */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-gray-200/50 shadow-lg">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-xl blur-lg opacity-50"></div>
                <div className="relative bg-gradient-to-r from-cyan-500 to-purple-600 p-3 rounded-xl">
                  <Truck className="w-7 h-7 text-white" strokeWidth={2} />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-black bg-gradient-to-r from-cyan-600 to-purple-600 bg-clip-text text-transparent">
                  Intelligent Logistics
                </h1>
                <p className="text-xs text-gray-500 font-medium">Fleet Intelligence Platform</p>
              </div>
            </div>

            {/* Live Stats */}
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-3 backdrop-blur-sm bg-blue-50/50 px-4 py-2 rounded-xl border border-blue-200/50">
                <Truck className="w-5 h-5 text-blue-600" />
                <div>
                  <div className="text-xs text-gray-500">Fleet</div>
                  <div className="text-lg font-bold text-gray-800">{fleetState?.vehicles.length || 0}</div>
                </div>
              </div>
              
              <div className="flex items-center gap-3 backdrop-blur-sm bg-emerald-50/50 px-4 py-2 rounded-xl border border-emerald-200/50">
                <Package className="w-5 h-5 text-emerald-600" />
                <div>
                  <div className="text-xs text-gray-500">Active</div>
                  <div className="text-lg font-bold text-gray-800">{metrics?.matched_loads || 0}</div>
                </div>
              </div>
              
              <div className="flex items-center gap-3 backdrop-blur-sm bg-purple-50/50 px-4 py-2 rounded-xl border border-purple-200/50">
                <Gauge className="w-5 h-5 text-purple-600" />
                <div>
                  <div className="text-xs text-gray-500">Utilization</div>
                  <div className="text-lg font-bold text-gray-800">
                    {metrics?.avg_utilization ? metrics.avg_utilization.toFixed(0) : 0}%
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 backdrop-blur-sm bg-green-50/50 px-4 py-2 rounded-xl border border-green-200/50">
                <Radio className="w-4 h-4 text-green-500 animate-pulse" />
                <span className="text-sm font-semibold text-green-700">LIVE</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Main Content Area - 8 columns */}
          <div className="col-span-12 lg:col-span-8 space-y-6">
            {/* View Tabs + Map */}
            <div className="backdrop-blur-xl bg-white/90 rounded-3xl border border-gray-200/50 shadow-2xl overflow-hidden">
              {/* Tab Navigation */}
              <div className="bg-gradient-to-r from-gray-50 to-white p-4 border-b border-gray-200/50">
                <div className="flex gap-2">
                  <button
                    onClick={() => setActiveView('map')}
                    className={`group flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                      activeView === 'map'
                        ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-blue-500/30 scale-105'
                        : 'bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 hover:shadow-md'
                    }`}
                  >
                    <MapPin className={`w-5 h-5 ${activeView === 'map' ? 'animate-pulse' : ''}`} />
                    <span>Live Map</span>
                    {activeView === 'map' && <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>}
                  </button>
                  
                  <button
                    onClick={() => setActiveView('matching')}
                    className={`group flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                      activeView === 'matching'
                        ? 'bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg shadow-purple-500/30 scale-105'
                        : 'bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 hover:shadow-md'
                    }`}
                  >
                    <Package className={`w-5 h-5 ${activeView === 'matching' ? 'animate-bounce' : ''}`} />
                    <span>Load Matching</span>
                  </button>
                  
                  <button
                    onClick={() => setActiveView('timeline')}
                    className={`group flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                      activeView === 'timeline'
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/30 scale-105'
                        : 'bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 hover:shadow-md'
                    }`}
                  >
                    <Activity className={`w-5 h-5 ${activeView === 'timeline' ? 'animate-pulse' : ''}`} />
                    <span>Activity Feed</span>
                  </button>
                </div>
              </div>

              {/* Content Area */}
              <div className="h-[650px] relative">
                {activeView === 'map' && fleetState && <EnhancedFleetMap fleetState={fleetState} />}
                {activeView === 'matching' && fleetState && <ProfessionalLoadMatchingPanel fleetState={fleetState} />}
                {activeView === 'timeline' && fleetState && <ProfessionalEventTimeline events={fleetState.events || []} />}
              </div>
            </div>

            {/* Metrics Dashboard */}
            {metrics && (
              <div className="backdrop-blur-xl bg-white/90 rounded-3xl border border-gray-200/50 shadow-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="bg-gradient-to-r from-orange-500 to-red-600 p-2 rounded-lg">
                    <BarChart3 className="w-5 h-5 text-white" />
                  </div>
                  <h2 className="text-xl font-bold text-gray-800">Performance Metrics</h2>
                </div>
                <ProfessionalMetricsDashboard metrics={metrics} />
              </div>
            )}
          </div>

          {/* Sidebar - 4 columns */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            {/* Live Predictions */}
            <div className="backdrop-blur-xl bg-white/90 rounded-3xl border border-gray-200/50 shadow-2xl overflow-hidden">
              <LivePredictionPanel 
                predictions={predictions} 
                onSimulate={handleSimulateMovement}
                isSimulating={isSimulating}
              />
            </div>

            {/* Agent Control */}
            <div className="backdrop-blur-xl bg-white/90 rounded-3xl border border-gray-200/50 shadow-2xl overflow-hidden">
              <AgentControl onRefresh={refreshData} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
