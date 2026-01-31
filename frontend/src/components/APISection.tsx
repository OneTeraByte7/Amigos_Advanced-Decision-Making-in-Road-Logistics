import { Code, Copy, Check } from 'lucide-react'
import { useState } from 'react'

export default function APISection() {
  const [copied, setCopied] = useState(false)

  const codeExample = `// Initialize Fleet Management
import { AdaptiveLogistics } from '@adaptive/sdk';

const client = new AdaptiveLogistics({
  apiKey: process.env.ADAPTIVE_API_KEY
});

// Match loads to vehicles
const matches = await client.loadMatcher.match({
  vehicles: fleet.getAvailableVehicles(),
  loads: await loadboard.fetchAvailable(),
  optimize: 'revenue' // or 'distance', 'fuel'
});

// Start real-time tracking
client.monitor.startTracking({
  vehicleIds: matches.map(m => m.vehicleId),
  interval: 2000, // 2 second updates
  onUpdate: (state) => {
    console.log(\`Fleet utilization: \${state.utilization}%\`);
  }
});`

  const handleCopy = () => {
    navigator.clipboard.writeText(codeExample)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section id="api" className="py-24 px-6 bg-white">
      <div className="container mx-auto max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left Content */}
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 bg-[#f5f7fa] border border-[#e5e7eb] rounded-full px-4 py-2">
              <Code className="w-4 h-4 text-[#0066ff]" />
              <span className="text-sm font-semibold text-[#0066ff]">DEVELOPER API</span>
            </div>

            <h2 className="text-[36px] font-bold text-[#1a2332] tracking-tight leading-tight">
              Powerful API for Seamless Integration
            </h2>

            <p className="text-[18px] text-[#64748b] leading-[1.6]">
              RESTful API with comprehensive documentation, SDKs for popular languages, and webhook support for real-time events.
            </p>

            <div className="space-y-4 pt-4">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-[#10b981] rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Check className="w-4 h-4 text-white" strokeWidth={3} />
                </div>
                <div>
                  <h4 className="text-[16px] font-semibold text-[#1a2332] mb-1">
                    Complete SDK Libraries
                  </h4>
                  <p className="text-[16px] text-[#64748b]">
                    Python, JavaScript, Go, and Java SDKs with full TypeScript support
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-[#10b981] rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Check className="w-4 h-4 text-white" strokeWidth={3} />
                </div>
                <div>
                  <h4 className="text-[16px] font-semibold text-[#1a2332] mb-1">
                    Real-Time Webhooks
                  </h4>
                  <p className="text-[16px] text-[#64748b]">
                    Subscribe to fleet events and receive instant notifications
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-[#10b981] rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Check className="w-4 h-4 text-white" strokeWidth={3} />
                </div>
                <div>
                  <h4 className="text-[16px] font-semibold text-[#1a2332] mb-1">
                    99.99% Uptime SLA
                  </h4>
                  <p className="text-[16px] text-[#64748b]">
                    Enterprise-grade reliability with global CDN distribution
                  </p>
                </div>
              </div>
            </div>

            <div className="pt-6">
              <button className="inline-flex items-center gap-2 bg-[#0066ff] text-white px-8 py-4 rounded-lg font-semibold text-[16px] hover:bg-[#0052cc] transition-all duration-200">
                View Full Documentation
              </button>
            </div>
          </div>

          {/* Right Content - Code Block */}
          <div className="relative">
            <div className="bg-[#1a2332] rounded-2xl border border-[#2d3748] overflow-hidden shadow-xl">
              {/* Code Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-[#2d3748]">
                <div className="flex items-center gap-3">
                  <div className="flex gap-2">
                    <div className="w-3 h-3 bg-[#ef4444] rounded-full"></div>
                    <div className="w-3 h-3 bg-[#f59e0b] rounded-full"></div>
                    <div className="w-3 h-3 bg-[#10b981] rounded-full"></div>
                  </div>
                  <span className="text-sm text-[#94a3b8] font-medium">quickstart.js</span>
                </div>
                <button 
                  onClick={handleCopy}
                  className="flex items-center gap-2 text-sm text-[#94a3b8] hover:text-white transition-colors"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4" />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>

              {/* Code Content */}
              <div className="p-6 overflow-x-auto">
                <pre className="text-sm leading-relaxed">
                  <code className="text-[#e2e8f0] font-mono">
                    <span className="text-[#94a3b8]">// Initialize Fleet Management</span>
                    {'\n'}
                    <span className="text-[#c792ea]">import</span> <span className="text-[#89ddff]">{'{'}</span> <span className="text-[#82aaff]">AdaptiveLogistics</span> <span className="text-[#89ddff]">{'}'}</span> <span className="text-[#c792ea]">from</span> <span className="text-[#c3e88d]">'@adaptive/sdk'</span><span className="text-[#89ddff]">;</span>
                    {'\n\n'}
                    <span className="text-[#c792ea]">const</span> <span className="text-[#82aaff]">client</span> <span className="text-[#89ddff]">=</span> <span className="text-[#c792ea]">new</span> <span className="text-[#ffcb6b]">AdaptiveLogistics</span><span className="text-[#89ddff]">(</span>
                    <span className="text-[#89ddff]">{'{'}</span>
                    {'\n  '}
                    <span className="text-[#82aaff]">apiKey</span><span className="text-[#89ddff]">:</span> <span className="text-[#82aaff]">process</span><span className="text-[#89ddff]">.</span><span className="text-[#82aaff]">env</span><span className="text-[#89ddff]">.</span><span className="text-[#f07178]">ADAPTIVE_API_KEY</span>
                    {'\n'}
                    <span className="text-[#89ddff]">{'}'}</span><span className="text-[#89ddff]">);</span>
                    {'\n\n'}
                    <span className="text-[#94a3b8]">// Match loads to vehicles</span>
                    {'\n'}
                    <span className="text-[#c792ea]">const</span> <span className="text-[#82aaff]">matches</span> <span className="text-[#89ddff]">=</span> <span className="text-[#c792ea]">await</span> <span className="text-[#82aaff]">client</span><span className="text-[#89ddff]">.</span><span className="text-[#82aaff]">loadMatcher</span><span className="text-[#89ddff]">.</span><span className="text-[#ffcb6b]">match</span><span className="text-[#89ddff]">(</span>
                    <span className="text-[#89ddff]">{'{'}</span>{'\n  '}
                    <span className="text-[#82aaff]">optimize</span><span className="text-[#89ddff]">:</span> <span className="text-[#c3e88d]">'revenue'</span>
                    {'\n'}
                    <span className="text-[#89ddff]">{'}'}</span><span className="text-[#89ddff]">);</span>
                  </code>
                </pre>
              </div>
            </div>

            {/* Floating Badge */}
            <div className="absolute -top-4 -right-4 bg-[#0066ff] text-white px-4 py-2 rounded-lg shadow-lg">
              <div className="text-xs font-semibold">REST API v2.0</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
