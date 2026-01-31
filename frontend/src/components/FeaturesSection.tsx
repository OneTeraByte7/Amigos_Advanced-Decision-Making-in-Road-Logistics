import { Brain, Zap, Globe, TrendingUp, Shield, BarChart3 } from 'lucide-react'

export default function FeaturesSection() {
  const features = [
    {
      icon: Brain,
      title: 'Agentic AI Decision Making',
      description: 'Autonomous AI agents continuously analyze fleet data, market conditions, and real-time events to make optimal routing and matching decisions.',
      stats: '1,847 decisions/min'
    },
    {
      icon: Zap,
      title: 'Real-Time Load Matching',
      description: 'LLM-powered algorithms instantly match available loads with optimal vehicles considering distance, capacity, revenue, and strategic positioning.',
      stats: '98.5% match rate'
    },
    {
      icon: Globe,
      title: 'Live Fleet Tracking',
      description: 'Monitor your entire fleet in real-time with sub-second position updates, fuel levels, driver hours, and cargo status across all vehicles.',
      stats: '2s refresh rate'
    },
    {
      icon: TrendingUp,
      title: 'Adaptive Route Optimization',
      description: 'Dynamic route adjustments based on traffic, weather, fuel prices, and new opportunities. Reduce deadhead miles by up to 40%.',
      stats: '40% reduction'
    },
    {
      icon: Shield,
      title: 'Predictive Maintenance',
      description: 'AI-powered alerts for vehicle maintenance needs, fuel warnings, and driver fatigue detection to prevent breakdowns and ensure safety.',
      stats: '99.2% uptime'
    },
    {
      icon: BarChart3,
      title: 'Analytics & Insights',
      description: 'Comprehensive dashboards with KPI tracking, revenue optimization, cost analysis, and custom reports for data-driven decisions.',
      stats: '30+ metrics'
    }
  ]

  return (
    <section id="features" className="py-24 px-6 bg-[#f5f7fa]">
      <div className="container mx-auto max-w-7xl">
        {/* Section Header */}
        <div className="text-center mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 bg-white border border-[#e5e7eb] rounded-full px-4 py-2">
            <span className="text-sm font-semibold text-[#0066ff]">PLATFORM FEATURES</span>
          </div>
          <h2 className="text-[36px] font-bold text-[#1a2332] tracking-tight">
            Enterprise-Grade Fleet Intelligence
          </h2>
          <p className="text-[18px] text-[#64748b] max-w-2xl mx-auto leading-[1.6]">
            Powered by advanced AI agents that work 24/7 to optimize your logistics operations
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div 
                key={index}
                className="bg-white border border-[#e5e7eb] rounded-2xl p-8 hover:border-[#0066ff] transition-all duration-300 group"
              >
                {/* Icon */}
                <div className="w-14 h-14 bg-[#0066ff] rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Icon className="w-7 h-7 text-white" strokeWidth={2} />
                </div>

                {/* Content */}
                <h3 className="text-[24px] font-bold text-[#1a2332] mb-3">
                  {feature.title}
                </h3>
                <p className="text-[16px] text-[#64748b] leading-[1.6] mb-4">
                  {feature.description}
                </p>

                {/* Stats Badge */}
                <div className="inline-flex items-center gap-2 bg-[#f5f7fa] border border-[#e5e7eb] rounded-lg px-3 py-1.5">
                  <div className="w-1.5 h-1.5 bg-[#10b981] rounded-full"></div>
                  <span className="text-sm font-semibold text-[#1a2332]">{feature.stats}</span>
                </div>
              </div>
            )
          })}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <button className="inline-flex items-center gap-2 bg-[#0066ff] text-white px-8 py-4 rounded-lg font-semibold text-[16px] hover:bg-[#0052cc] transition-all duration-200 shadow-sm">
            <span>Explore All Features</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </button>
        </div>
      </div>
    </section>
  )
}
