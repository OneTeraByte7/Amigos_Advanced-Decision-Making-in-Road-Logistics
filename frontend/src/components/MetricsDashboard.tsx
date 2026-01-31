import { TrendingUp, Truck, Package, Activity, DollarSign } from 'lucide-react'
import { FleetMetrics } from '../types'

interface Props {
  metrics: FleetMetrics
}

export default function MetricsDashboard({ metrics }: Props) {
  const cards = [
    {
      title: 'Fleet Size',
      value: metrics.total_vehicles,
      subtitle: `${metrics.available_vehicles} available`,
      icon: Truck,
      color: 'blue',
      change: null
    },
    {
      title: 'Active Loads',
      value: metrics.matched_loads,
      subtitle: `${metrics.available_loads} available`,
      icon: Package,
      color: 'green',
      change: null
    },
    {
      title: 'Utilization',
      value: `${metrics.avg_utilization ? metrics.avg_utilization.toFixed(1) : 0}%`,
      subtitle: 'Fleet average',
      icon: Activity,
      color: 'purple',
      change: metrics.avg_utilization && metrics.avg_utilization > 80 ? '+good' : null
    },
    {
      title: 'Distance Today',
      value: `${metrics.total_km_today ? metrics.total_km_today.toFixed(0) : 0} km`,
      subtitle: 'Total traveled',
      icon: TrendingUp,
      color: 'orange',
      change: null
    }
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const Icon = card.icon
        return (
          <div key={idx} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 bg-${card.color}-100 rounded-lg`}>
                <Icon className={`w-6 h-6 text-${card.color}-600`} />
              </div>
              {card.change && (
                <span className="text-green-600 text-sm font-medium">â†‘</span>
              )}
            </div>
            <div className="text-3xl font-bold text-gray-800 mb-1">
              {card.value}
            </div>
            <div className="text-sm text-gray-500">{card.title}</div>
            <div className="text-xs text-gray-400 mt-1">{card.subtitle}</div>
          </div>
        )
      })}
    </div>
  )
}