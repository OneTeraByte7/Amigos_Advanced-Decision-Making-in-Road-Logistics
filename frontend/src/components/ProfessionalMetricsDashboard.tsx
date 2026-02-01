import { TrendingUp, Truck, Package, Activity, DollarSign, Gauge } from 'lucide-react'
import { FleetMetrics } from '../types'

interface Props {
  metrics: FleetMetrics
}

export default function ProfessionalMetricsDashboard({ metrics }: Props) {
  
  const utilization = metrics.avg_utilization ?? 0
  
  const cards = [
    {
      title: 'Fleet Size',
      value: metrics.total_vehicles,
      subtitle: `${metrics.available_vehicles} available`,
      icon: Truck,
      color: 'blue',
      gradient: 'from-blue-500 via-blue-600 to-indigo-600',
      bgGradient: 'from-blue-50 to-indigo-50',
      shadowColor: 'shadow-blue-200',
      change: null,
      suffix: 'vehicles'
    },
    {
      title: 'Active Loads',
      value: metrics.matched_loads,
      subtitle: `${metrics.available_loads} available`,
      icon: Package,
      color: 'green',
      gradient: 'from-green-500 via-emerald-600 to-teal-600',
      bgGradient: 'from-green-50 to-emerald-50',
      shadowColor: 'shadow-green-200',
      change: metrics.matched_loads > 0 ? '+active' : null,
      suffix: 'loads'
    },
    {
      title: 'Utilization',
      value: utilization ? utilization.toFixed(1) : 0,
      subtitle: 'Fleet average',
      icon: Gauge,
      color: 'purple',
      gradient: 'from-purple-500 via-purple-600 to-pink-600',
      bgGradient: 'from-purple-50 to-pink-50',
      shadowColor: 'shadow-purple-200',
      change: utilization > 80 ? '+excellent' : null,
      suffix: '%'
    },
    {
      title: 'Distance Today',
      value: metrics.total_km_today ? Math.round(metrics.total_km_today) : 0,
      subtitle: 'Total traveled',
      icon: TrendingUp,
      color: 'orange',
      gradient: 'from-orange-500 via-red-500 to-pink-600',
      bgGradient: 'from-orange-50 to-red-50',
      shadowColor: 'shadow-orange-200',
      change: null,
      suffix: 'km'
    }
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const Icon = card.icon
        return (
          <div 
            key={idx} 
            className={`group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden border border-gray-100`}
          >
            {/* Background Gradient Decoration */}
            <div className={`absolute inset-0 bg-gradient-to-br ${card.bgGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}></div>
            
            {/* Content */}
            <div className="relative p-6">
              {/* Icon and Change Indicator */}
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 bg-gradient-to-br ${card.gradient} rounded-xl shadow-lg transform group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300`}>
                  <Icon className="w-7 h-7 text-white" />
                </div>
                {card.change && (
                  <div className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold animate-pulse">
                    <TrendingUp className="w-3 h-3" />
                    <span>Live</span>
                  </div>
                )}
              </div>

              {/* Value */}
              <div className="mb-2">
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-bold text-gray-800 tracking-tight">
                    {card.value}
                  </span>
                  <span className="text-lg font-medium text-gray-500">
                    {card.suffix}
                  </span>
                </div>
              </div>

              {/* Title and Subtitle */}
              <div className="space-y-1">
                <div className="text-sm font-semibold text-gray-700">
                  {card.title}
                </div>
                <div className="text-xs text-gray-500">
                  {card.subtitle}
                </div>
              </div>

              {/* Progress Bar for Utilization */}
              {card.title === 'Utilization' && (
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div 
                      className={`bg-gradient-to-r ${card.gradient} h-2 rounded-full transition-all duration-1000 ease-out`}
                      style={{ width: `${Math.min(Number(card.value), 100)}%` }}
                    >
                      <div className="w-full h-full bg-white opacity-20 animate-pulse"></div>
                    </div>
                  </div>
                </div>
              )}

              {/* Decorative Corner Element */}
              <div className={`absolute -bottom-2 -right-2 w-20 h-20 bg-gradient-to-br ${card.gradient} opacity-5 rounded-full blur-xl group-hover:opacity-10 transition-opacity duration-300`}></div>
            </div>

            {/* Bottom Accent Line */}
            <div className={`h-1 bg-gradient-to-r ${card.gradient}`}></div>
          </div>
        )
      })}
    </div>
  )
}
