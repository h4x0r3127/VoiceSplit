'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X, LayoutDashboard, Upload, Clock, Settings, User } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { Logo } from '@/components/brand/Logo'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/upload', label: 'Upload', icon: Upload },
  { href: '/history', label: 'History', icon: Clock },
  { href: '/settings', label: 'Settings', icon: Settings },
  { href: '/profile', label: 'Profile', icon: User },
]

export function MobileSidebar() {
  const [open, setOpen] = useState(false)
  const pathname = usePathname()

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 lg:hidden z-40 w-12 h-12 rounded-2xl glass-strong border border-brand-cyan/20 flex items-center justify-center text-white shadow-glow"
        aria-label="Open navigation"
      >
        <Menu className="w-5 h-5" />
      </button>

      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
              className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
            />
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="fixed inset-y-0 left-0 z-50 w-72 glass-strong border-r border-brand-cyan/10 flex flex-col lg:hidden"
            >
              <div className="h-16 flex items-center justify-between px-4 border-b border-brand-cyan/10">
                <Logo size={32} />
                <button
                  onClick={() => setOpen(false)}
                  className="w-8 h-8 rounded-lg glass flex items-center justify-center text-muted hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <nav className="flex-1 py-6 px-3 space-y-1">
                {navItems.map((item) => {
                  const active = pathname.startsWith(item.href)
                  return (
                    <Link key={item.href} href={item.href} onClick={() => setOpen(false)}>
                      <div
                        className={cn(
                          'flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-150',
                          active
                            ? 'bg-brand-cyan/10 text-brand-cyan'
                            : 'text-slate-400 hover:text-white hover:bg-white/5',
                        )}
                      >
                        <item.icon className="w-5 h-5 flex-shrink-0" />
                        <span className="font-medium text-sm">{item.label}</span>
                      </div>
                    </Link>
                  )
                })}
              </nav>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
