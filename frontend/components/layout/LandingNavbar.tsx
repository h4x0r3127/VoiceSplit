'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Menu, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { Logo } from '@/components/brand/Logo'
import { GradientButton } from '@/components/common/GradientButton'

const navLinks = [
  { label: 'Features', href: '/#features' },
  { label: 'How it Works', href: '/#how-it-works' },
  { label: 'Pricing', href: '/#pricing' },
  { label: 'FAQ', href: '/#faq' },
]

export function LandingNavbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        scrolled ? 'glass-strong border-b border-brand-cyan/10' : 'bg-transparent',
      )}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center gap-8">
        <Logo size={36} />

        {/* Center nav */}
        <nav className="hidden md:flex items-center gap-1 flex-1 justify-center">
          {navLinks.map(({ label, href }) => (
            <Link
              key={label}
              href={href}
              className="px-4 py-2 text-sm text-muted hover:text-white rounded-lg hover:bg-white/5 transition-all"
            >
              {label}
            </Link>
          ))}
        </nav>

        {/* CTAs */}
        <div className="hidden md:flex items-center gap-3 ml-auto">
          <Link href="/login">
            <GradientButton variant="ghost" size="sm">Sign In</GradientButton>
          </Link>
          <Link href="/register">
            <GradientButton size="sm">Get Started</GradientButton>
          </Link>
        </div>

        {/* Mobile toggle */}
        <button
          onClick={() => setMobileOpen((o) => !o)}
          className="md:hidden ml-auto p-2 rounded-lg text-muted hover:text-white"
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass-strong border-t border-brand-cyan/10 overflow-hidden"
          >
            <nav className="px-6 py-4 space-y-1">
              {navLinks.map(({ label, href }) => (
                <Link
                  key={label}
                  href={href}
                  onClick={() => setMobileOpen(false)}
                  className="block px-4 py-2.5 text-sm text-muted hover:text-white rounded-lg hover:bg-white/5 transition-all"
                >
                  {label}
                </Link>
              ))}
              <div className="pt-3 flex flex-col gap-2">
                <Link href="/login" onClick={() => setMobileOpen(false)}>
                  <GradientButton variant="outline" className="w-full">Sign In</GradientButton>
                </Link>
                <Link href="/register" onClick={() => setMobileOpen(false)}>
                  <GradientButton className="w-full">Get Started</GradientButton>
                </Link>
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
