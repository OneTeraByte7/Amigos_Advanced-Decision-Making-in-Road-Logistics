import { Truck, Zap, Brain, ArrowRight, Play, CheckCircle } from 'lucide-react'

export default function HeroSection() {
  return (
    <section className="relative bg-white pt-32 pb-20 px-6 overflow-hidden">
      {/* Background Pattern - Subtle */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, #1a2332 1px, transparent 0)`,
          backgroundSize: '40px 40px'
        }}></div>
      </div>

      <div className="container mx-auto max-w-7xl relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left Content */}
          <div className="space-y-8">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-[#f5f7fa] border border-[#e5e7eb] rounded-full px-4 py-2">
              <div className="w-2 h-2 bg-[#0066ff] rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-[#1a2332]">AI-Powered Fleet Intelligence</span>
            </div>

            {/* Headline */}
            <div className="space-y-4">
              <h1 className="text-[48px] leading-[1.2] font-bold text-[#1a2332] tracking-tight">
                Transform Your Logistics with{' '}
                <span className="text-[#0066ff]">Agentic AI</span>
              </h1>
              <p className="text-[18px] leading-[1.6] text-[#64748b] font-normal max-w-xl">
                Real-time fleet optimization, intelligent load matching, and adaptive route management powered by advanced AI agents. Reduce costs by 30% and increase efficiency by 45%.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <button className="group inline-flex items-center justify-center gap-2 bg-[#0066ff] text-white px-8 py-4 rounded-lg font-semibold text-[16px] hover:bg-[#0052cc] transition-all duration-200 shadow-sm hover:shadow-md">
                <span>Start Free Trial</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              
              <button className="inline-flex items-center justify-center gap-2 bg-white text-[#1a2332] px-8 py-4 rounded-lg font-semibold text-[16px] border-2 border-[#e5e7eb] hover:border-[#0066ff] hover:text-[#0066ff] transition-all duration-200">
                <Play className="w-5 h-5" />
                <span>Watch Demo</span>
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="flex items-center gap-8 pt-8">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-[#10b981]" />
                <span className="text-sm text-[#64748b]">No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-[#10b981]" />
                <span className="text-sm text-[#64748b]">14-day free trial</span>
              </div>
            </div>
          </div>

          {/* Right Content - Visual */}
          <div className="relative">
            {/* Main Visual Container */}
            <div className="relative bg-[#f5f7fa] border-2 border-[#e5e7eb] rounded-2xl p-8 shadow-xl">
              {/* Animated Stats Cards */}
              <div className="space-y-4">
                {/* Card 1 */}
                <div className="bg-white border border-[#e5e7eb] rounded-xl p-6 hover:border-[#0066ff] transition-all duration-300 animate-fade-in">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-[#0066ff] rounded-lg flex items-center justify-center">
                        <Truck className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <div className="text-sm text-[#64748b]">Fleet Utilization</div>
                        <div className="text-2xl font-bold text-[#1a2332]">94.2%</div>
                      </div>
                    </div>
                    <div className="text-[#10b981] text-sm font-semibold">+12%</div>
                  </div>
                  <div className="w-full bg-[#f5f7fa] rounded-full h-2">
                    <div className="bg-[#0066ff] h-2 rounded-full" style={{ width: '94%' }}></div>
                  </div>
                </div>

                {/* Card 2 */}
                <div className="bg-white border border-[#e5e7eb] rounded-xl p-6 hover:border-[#0066ff] transition-all duration-300 animate-fade-in" style={{ animationDelay: '100ms' }}>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-[#10b981] rounded-lg flex items-center justify-center">
                        <Zap className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <div className="text-sm text-[#64748b]">Cost Savings</div>
                        <div className="text-2xl font-bold text-[#1a2332]">$247K</div>
                      </div>
                    </div>
                    <div className="text-[#10b981] text-sm font-semibold">+28%</div>
                  </div>
                  <div className="flex gap-1">
                    {[85, 92, 78, 88, 95, 90, 96].map((height, i) => (
                      <div key={i} className="flex-1 bg-[#10b981] rounded-sm" style={{ height: `${height}%`, opacity: 0.8 + (i * 0.02) }}></div>
                    ))}
                  </div>
                </div>

                {/* Card 3 */}
                <div className="bg-white border border-[#e5e7eb] rounded-xl p-6 hover:border-[#0066ff] transition-all duration-300 animate-fade-in" style={{ animationDelay: '200ms' }}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-[#8b5cf6] rounded-lg flex items-center justify-center">
                        <Brain className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <div className="text-sm text-[#64748b]">AI Decisions/min</div>
                        <div className="text-2xl font-bold text-[#1a2332]">1,847</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-[#10b981] rounded-full animate-pulse"></div>
                      <span className="text-xs text-[#64748b]">Live</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating Elements */}
            <div className="absolute -top-4 -right-4 w-24 h-24 bg-[#0066ff] rounded-2xl opacity-10 animate-pulse"></div>
            <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-[#10b981] rounded-full opacity-10 animate-pulse" style={{ animationDelay: '1s' }}></div>
          </div>
        </div>
      </div>

      {/* Bottom Wave Separator */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-[#e5e7eb]"></div>
    </section>
  )
}
