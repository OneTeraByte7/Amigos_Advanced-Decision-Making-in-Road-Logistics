import { Clock, Truck, AlertTriangle, CheckCircle, Package } from 'lucide-react'
import { Event } from '../types'

interface Props {
  events: Event[]
}

export default function EventTimeline({ events }: Props) {
  const getEventIcon = (type: string) => {
    switch (type) {
      case 'vehicle_moved': return Truck
      case 'load_matched': return CheckCircle
      case 'traffic_detected': return AlertTriangle
      case 'load_available': return Package
      default: return Clock
    }
  }

  const getEventColor = (type: string) => {
    switch (type) {
      case 'vehicle_moved': return 'blue'
      case 'load_matched': return 'green'
      case 'traffic_detected': return 'red'
      case 'load_available': return 'yellow'
      default: return 'gray'
    }
  }

  const sortedEvents = [...events].sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  ).slice(0, 20)

  return (
    <div className="p-6 space-y-4 overflow-y-auto h-full">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Event Timeline</h3>
      <div className="space-y-3">
        {sortedEvents.map((event, idx) => {
          const Icon = getEventIcon(event.event_type)
          const color = getEventColor(event.event_type)
          
          return (
            <div key={idx} className="flex gap-4 items-start">
              <div className={`p-2 bg-${color}-100 rounded-lg flex-shrink-0`}>
                <Icon className={`w-5 h-5 text-${color}-600`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-gray-800 truncate">
                    {event.vehicle_id}
                  </span>
                  <span className="text-xs text-gray-500 whitespace-nowrap">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="text-sm text-gray-600 capitalize">
                  {event.event_type.replace(/_/g, ' ')}
                </div>
                {Object.keys(event.details).length > 0 && (
                  <div className="text-xs text-gray-500 mt-1">
                    {Object.entries(event.details).slice(0, 2).map(([key, value]) => (
                      <div key={key}>
                        {key}: {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}