import { Truck, Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-[#e5e7eb] shadow-sm">
      <div className="container mx-auto max-w-7xl px-6">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#0066ff] rounded-lg flex items-center justify-center">
              <Truck className="w-6 h-6 text-white" strokeWidth={2.5} />
            </div>
            <div>
              <div className="text-xl font-bold text-[#1a2332]">Adaptive Logistics</div>
              <div className="text-xs text-[#64748b] font-medium">AI Fleet Platform</div>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center gap-8">
            <a href="#features" className="text-[16px] font-medium text-[#64748b] hover:text-[#0066ff] transition-colors">
              Features
            </a>
            <a href="#solutions" className="text-[16px] font-medium text-[#64748b] hover:text-[#0066ff] transition-colors">
              Solutions
            </a>
            <a href="#api" className="text-[16px] font-medium text-[#64748b] hover:text-[#0066ff] transition-colors">
              API Docs
            </a>
            <a href="#pricing" className="text-[16px] font-medium text-[#64748b] hover:text-[#0066ff] transition-colors">
              Pricing
            </a>
            <a href="#company" className="text-[16px] font-medium text-[#64748b] hover:text-[#0066ff] transition-colors">
              Company
            </a>
          </div>

          {/* CTA Buttons */}
          <div className="hidden lg:flex items-center gap-4">
            <button className="text-[16px] font-semibold text-[#1a2332] hover:text-[#0066ff] transition-colors px-4 py-2">
              Sign In
            </button>
            <button className="bg-[#0066ff] text-white px-6 py-2.5 rounded-lg font-semibold text-[16px] hover:bg-[#0052cc] transition-all duration-200 shadow-sm">
              Get Started
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button 
            className="lg:hidden p-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6 text-[#1a2332]" />
            ) : (
              <Menu className="w-6 h-6 text-[#1a2332]" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden py-6 space-y-4 border-t border-[#e5e7eb]">
            <a href="#features" className="block text-[16px] font-medium text-[#64748b] hover:text-[#0066ff] py-2">
              Features
            </a>
            <a href="#solutions" className="block text-[16px] font-medium text-[#64748b] hover:text-[#0066ff] py-2">
              Solutions
            </a>
            <a href="#api" className="block text-[16px] font-medium text-[#64748b] hover:text-[#0066ff] py-2">
              API Docs
            </a>
            <a href="#pricing" className="block text-[16px] font-medium text-[#64748b] hover:text-[#0066ff] py-2">
              Pricing
            </a>
            <a href="#company" className="block text-[16px] font-medium text-[#64748b] hover:text-[#0066ff] py-2">
              Company
            </a>
            <div className="pt-4 space-y-3">
              <button className="w-full text-[16px] font-semibold text-[#1a2332] border border-[#e5e7eb] px-6 py-3 rounded-lg">
                Sign In
              </button>
              <button className="w-full bg-[#0066ff] text-white px-6 py-3 rounded-lg font-semibold text-[16px]">
                Get Started
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
