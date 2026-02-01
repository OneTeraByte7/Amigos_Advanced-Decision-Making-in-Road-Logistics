import { useState, useEffect } from 'react'
import { Activity, TrendingUp, Package, Truck, MapPin, AlertTriangle, CheckCircle, Clock, Zap } from 'lucide-react'
import { Event } from '../types'
import { api } from '../services/api'

interface Props {
  events: Event[]
}

export default function ProfessionalEventTimeline({ events }: Props) {
  const [metrics, setMetrics] = useState<any>(null)

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
  
  // Sort events by timestamp (most recent first)
  const sortedEvents = [...events].sort((a, b) => {
    const timeA = typeof a.timestamp === 'string' ? new Date(a.timestamp).getTime() : a.timestamp * 1000
    const timeB = typeof b.timestamp === 'string' ? new Date(b.timestamp).getTime() : b.timestamp * 1000
    return timeB - timeA
  })
  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'vehicle_position_update':
        return { icon: MapPin, color: 'text-blue-600', bg: 'bg-blue-100', label: 'Position Update' }
      case 'load_posted':
        return { icon: Package, color: 'text-orange-600', bg: 'bg-orange-100', label: 'Load Posted' }
      case 'load_matched':
        return { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100', label: 'Load Matched' }
      case 'trip_started':
        return { icon: Truck, color: 'text-blue-600', bg: 'bg-blue-100', label: 'Trip Started' }
      case 'trip_completed':
        return { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100', label: 'Trip Completed' }
      case 'delivery_delay':
        return { icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-100', label: 'Delay Alert' }
      case 'traffic_alert':
        return { icon: AlertTriangle, color: 'text-yellow-600', bg: 'bg-yellow-100', label: 'Traffic Alert' }
      case 'fuel_low':
        return { icon: Zap, color: 'text-orange-600', bg: 'bg-orange-100', label: 'Fuel Warning' }
      default:
        return { icon: Activity, color: 'text-gray-600', bg: 'bg-gray-100', label: 'Event' }
    }
  }

  const formatTime = (timestamp: string | number) => {
    const date = new Date(typeof timestamp === 'string' ? timestamp : timestamp * 1000)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    if (seconds < 60) return `${seconds}s ago`
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  const recentEvents = sortedEvents.slice(0, 20)
  const eventCounts = {
    total: events.length,
    positions: events.filter(e => e.event_type === 'vehicle_position_update').length,
    loads: events.filter(e => e.event_type === 'load_posted' || e.event_type === 'load_matched').length,
    trips: events.filter(e => e.event_type === 'trip_started' || e.event_type === 'trip_completed').length,
    alerts: events.filter(e => e.event_type === 'delivery_delay' || e.event_type === 'traffic_alert').length,
  }

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full bg-gradient-to-br from-gray-50 to-purple-50">
      {/* Stats Overview */}
      <div className="grid grid-cols-5 gap-3">
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-4 text-white shadow-lg">
          <div className="flex items-center gap-2 mb-1">
            <Activity className="w-4 h-4" />
            <span className="text-xs opacity-90">Total Events</span>
          </div>
          <div className="text-3xl font-bold">{eventCounts.total}</div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-4 text-white shadow-lg">
          <div className="flex items-center gap-2 mb-1">
            <MapPin className="w-4 h-4" />
            <span className="text-xs opacity-90">Positions</span>
          </div>
          <div className="text-3xl font-bold">{eventCounts.positions}</div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-4 text-white shadow-lg">
          <div className="flex items-center gap-2 mb-1">
            <Package className="w-4 h-4" />
            <span className="text-xs opacity-90">Loads</span>
          </div>
          <div className="text-3xl font-bold">{eventCounts.loads}</div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-4 text-white shadow-lg">
          <div className="flex items-center gap-2 mb-1">
            <Truck className="w-4 h-4" />
            <span className="text-xs opacity-90">Trips</span>
          </div>
          <div className="text-3xl font-bold">{eventCounts.trips}</div>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-4 text-white shadow-lg">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-xs opacity-90">Alerts</span>
          </div>
          <div className="text-3xl font-bold">{eventCounts.alerts}</div>
        </div>
      </div>

      {/* Timeline Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <Clock className="w-6 h-6 text-purple-500" />
          Live Activity Feed
        </h3>
        <span className="text-sm text-gray-500">Last {recentEvents.length} events</span>
      </div>

      {/* Timeline */}
      {recentEvents.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center">
          <Activity className="w-20 h-20 mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 text-lg">No events yet</p>
          <p className="text-sm text-gray-400 mt-2">Events will appear here as the system operates</p>
        </div>
      ) : (
        <div className="relative">
          {/* Timeline Line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-purple-300 via-blue-300 to-transparent"></div>

          {/* Events */}
          <div className="space-y-4">
            {recentEvents.map((event, idx) => {
              const eventInfo = getEventIcon(event.event_type)
              const Icon = eventInfo.icon
              
              return (
                <div key={`${event.event_id}-${idx}`} className="relative pl-16">
                  {/* Timeline Dot */}
                  <div className={`absolute left-3 w-6 h-6 rounded-full ${eventInfo.bg} flex items-center justify-center shadow-lg`}>
                    <Icon className={`w-3 h-3 ${eventInfo.color}`} />
                  </div>

                  {/* Event Card */}
                  <div className="bg-white rounded-xl p-4 shadow-md hover:shadow-xl transition-all duration-300 border-l-4 border-purple-500">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${eventInfo.bg} ${eventInfo.color}`}>
                            {eventInfo.label}
                          </span>
                          <span className="text-xs text-gray-500">{formatTime(event.timestamp)}</span>
                        </div>
                        
                        <div className="font-semibold text-gray-800 mb-1">
                          {event.event_id || `Event ${idx + 1}`}
                        </div>

                        {/* Event Details */}
                        {event.payload && Object.keys(event.payload).length > 0 && (
                          <div className="mt-2 space-y-1">
                            {event.payload.vehicle_id && (
                              <div className="text-sm text-gray-600">
                                <span className="font-medium">Vehicle:</span> {event.payload.vehicle_id}
                              </div>
                            )}
                            {event.payload.load_id && (
                              <div className="text-sm text-gray-600">
                                <span className="font-medium">Load:</span> {event.payload.load_id}
                              </div>
                            )}
                            {event.payload.location && (
                              <div className="text-sm text-gray-600">
                                <span className="font-medium">Location:</span> {event.payload.location}
                              </div>
                            )}
                            {event.payload.message && (
                              <div className="text-sm text-gray-700 italic mt-2 p-2 bg-gray-50 rounded">
                                {event.payload.message}
                              </div>
                            )}
                            {event.payload.distance_km && (
                              <div className="text-sm text-gray-600">
                                <span className="font-medium">Distance:</span> {event.payload.distance_km}km
                              </div>
                            )}
                            {event.payload.revenue && (
                              <div className="text-sm text-green-600 font-semibold">
                                💰 Revenue: ${event.payload.revenue}
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Priority Indicator */}
                      {event.event_type.includes('alert') || event.event_type.includes('delay') && (
                        <div className="ml-3">
                          <span className="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Load More Indicator */}
          {events.length > 20 && (
            <div className="text-center mt-6 text-sm text-gray-500">
              Showing 20 of {events.length} events
            </div>
          )}
        </div>
      )}
    </div>
  )
}
