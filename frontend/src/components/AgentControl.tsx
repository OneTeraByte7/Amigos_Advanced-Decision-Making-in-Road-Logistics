import { useState } from 'react'
import { Bot, Zap, TrendingUp, Play, Loader } from 'lucide-react'
import { api } from '../services/api'

interface Props {
  onRefresh: () => void
}

export default function AgentControl({ onRefresh }: Props) {
  const [loading, setLoading] = useState<string | null>(null)
  const [results, setResults] = useState<Record<string, any>>({})

  const runAgent = async (agent: string, action: () => Promise<any>) => {
    setLoading(agent)
    try {
      const result = await action()
      setResults(prev => ({ ...prev, [agent]: result }))
      onRefresh()
    } catch (error: any) {
      setResults(prev => ({ ...prev, [agent]: { error: error.message } }))
    } finally {
      setLoading(null)
    }
  }

  const agents = [
    {
      id: 'monitor',
      name: 'Fleet Monitor',
      icon: TrendingUp,
      description: 'Track vehicles and collect events',
      color: 'blue',
      action: () => api.runCycle()
    },
    {
      id: 'matcher',
      name: 'Load Matcher',
      icon: Zap,
      description: 'AI-powered optimal matching',
      color: 'yellow',
      action: () => api.matchLoads()
    },
    {
      id: 'manager',
      name: 'Route Manager',
      icon: Bot,
      description: 'Adaptive route decisions',
      color: 'green',
      action: () => api.manageRoutes()
    }
  ]

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-xl shadow-lg">
        <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <Bot className="w-6 h-6" />
          AI Agent Control
        </h2>
        <p className="text-purple-100 text-sm">
          Trigger intelligent agents to optimize operations
        </p>
      </div>

      {/* Quick Start Guide */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <div className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 font-bold text-sm">
            ℹ
          </div>
          <div className="text-sm">
            <p className="font-semibold text-blue-900 mb-2">Quick Start:</p>
            <ol className="space-y-1 text-blue-800">
              <li>1. Click <strong>"Initialize Fleet System"</strong> above if not done</li>
              <li>2. Run <strong>Load Matcher</strong> to assign loads to vehicles</li>
              <li>3. Watch trucks move automatically with live predictions</li>
            </ol>
          </div>
        </div>
      </div>

      {agents.map(agent => {
        const Icon = agent.icon
        const result = results[agent.id]
        const isLoading = loading === agent.id

        return (
          <div key={agent.id} className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className={`p-4 border-b ${
              agent.color === 'blue' ? 'bg-blue-50 border-blue-100' :
              agent.color === 'yellow' ? 'bg-yellow-50 border-yellow-100' :
              'bg-green-50 border-green-100'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${
                    agent.color === 'blue' ? 'bg-blue-100' :
                    agent.color === 'yellow' ? 'bg-yellow-100' :
                    'bg-green-100'
                  }`}>
                    <Icon className={`w-6 h-6 ${
                      agent.color === 'blue' ? 'text-blue-600' :
                      agent.color === 'yellow' ? 'text-yellow-600' :
                      'text-green-600'
                    }`} />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-800">{agent.name}</h3>
                    <p className="text-sm text-gray-600">{agent.description}</p>
                  </div>
                </div>
                <button
                  onClick={() => runAgent(agent.id, agent.action)}
                  disabled={isLoading}
                  className={`px-4 py-2 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 ${
                    agent.color === 'blue' ? 'bg-gradient-to-r from-blue-600 to-blue-700' :
                    agent.color === 'yellow' ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
                    'bg-gradient-to-r from-green-600 to-green-700'
                  }`}
                >
                  {isLoading ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Run
                    </>
                  )}
                </button>
              </div>
            </div>

            {result && (
              <div className="p-4 bg-gray-50">
                {result.error ? (
                  <div className="text-red-600 text-sm">
                    <strong>Error:</strong> {result.error.includes('not initialized') ? 'Please initialize the system first' : result.error}
                  </div>
                ) : (
                  <div className="space-y-2 text-sm">
                    {agent.id === 'monitor' && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Vehicles Tracked:</span>
                          <span className="font-semibold">{result.vehicles_count || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Events Generated:</span>
                          <span className="font-semibold">{result.events_count || 0}</span>
                        </div>
                      </>
                    )}
                    {agent.id === 'matcher' && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Opportunities:</span>
                          <span className="font-semibold">{result.opportunities_analyzed || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Matches Created:</span>
                          <span className="font-semibold text-green-600">{result.matches_created || 0}</span>
                        </div>
                        {result.llm_reasoning && (
                          <div className="mt-2 p-3 bg-white rounded border">
                            <div className="text-xs text-gray-500 mb-1">AI Reasoning:</div>
                            <div className="text-xs text-gray-700 line-clamp-3">
                              {result.llm_reasoning}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                    {agent.id === 'manager' && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Routes Managed:</span>
                          <span className="font-semibold">{result.routes_managed || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Decisions Made:</span>
                          <span className="font-semibold text-green-600">
                            {result.decisions?.length || 0}
                          </span>
                        </div>
                        {result.decisions && result.decisions.length > 0 && (
                          <div className="mt-2 space-y-2">
                            {result.decisions.slice(0, 2).map((decision: any, idx: number) => (
                              <div key={idx} className="p-3 bg-white rounded border">
                                <div className="text-xs font-semibold text-gray-700">
                                  {decision.vehicle_id}
                                </div>
                                <div className="text-xs text-gray-600 mt-1">
                                  {decision.reasoning}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}