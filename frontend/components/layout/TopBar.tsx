'use client'

import { Bell, Search, ChevronDown, User, Settings, LogOut } from 'lucide-react'
import { signOut } from 'next-auth/react'
import Link from 'next/link'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { useAuth } from '@/hooks/useAuth'

interface TopBarProps {
  title?: string
}

export function TopBar({ title }: TopBarProps) {
  const { user } = useAuth()
  const [dropdownOpen, setDropdownOpen] = useState(false)

  return (
    <header className="h-16 glass-strong border-b border-brand-cyan/10 flex items-center px-6 gap-4 flex-shrink-0">
      {/* Page title */}
      {title && (
        <h1 className="text-lg font-semibold text-white mr-4 hidden sm:block">{title}</h1>
      )}

      {/* Search */}
      <div className="flex-1 max-w-md relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
        <input
          type="search"
          placeholder="Search jobs, speakers..."
          className="w-full bg-white/5 border border-brand-cyan/10 rounded-xl pl-9 pr-4 py-2 text-sm text-white placeholder:text-muted focus:outline-none focus:border-brand-cyan/30 focus:bg-white/8 transition-all"
        />
      </div>

      <div className="flex items-center gap-3 ml-auto">
        {/* Notifications */}
        <button className="relative w-9 h-9 rounded-xl glass flex items-center justify-center text-muted hover:text-white transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-brand-cyan" />
        </button>

        {/* User dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen((o) => !o)}
            className="flex items-center gap-2 px-3 py-2 rounded-xl glass hover:border-brand-cyan/20 transition-all"
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-brand-cyan to-brand-purple flex items-center justify-center text-xs font-bold text-white">
              {user?.name?.[0]?.toUpperCase() ?? 'U'}
            </div>
            <span className="text-sm font-medium text-white hidden sm:block max-w-[120px] truncate">
              {user?.name ?? 'User'}
            </span>
            <ChevronDown className={cn('w-4 h-4 text-muted transition-transform', dropdownOpen && 'rotate-180')} />
          </button>

          <AnimatePresence>
            {dropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: -8, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8, scale: 0.96 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 mt-2 w-48 glass-strong rounded-xl border border-brand-cyan/10 overflow-hidden z-50 shadow-card"
                onMouseLeave={() => setDropdownOpen(false)}
              >
                <div className="p-2">
                  <p className="px-3 py-1 text-xs text-muted">{user?.email}</p>
                  <div className="my-1 border-t border-brand-cyan/10" />
                  <Link href="/profile" onClick={() => setDropdownOpen(false)}>
                    <DropdownItem icon={<User className="w-4 h-4" />} label="Profile" />
                  </Link>
                  <Link href="/settings" onClick={() => setDropdownOpen(false)}>
                    <DropdownItem icon={<Settings className="w-4 h-4" />} label="Settings" />
                  </Link>
                  <div className="my-1 border-t border-brand-cyan/10" />
                  <button
                    onClick={() => signOut({ callbackUrl: '/login' })}
                    className="w-full"
                  >
                    <DropdownItem icon={<LogOut className="w-4 h-4" />} label="Sign out" danger />
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  )
}

function DropdownItem({
  icon,
  label,
  danger,
}: {
  icon: React.ReactNode
  label: string
  danger?: boolean
}) {
  return (
    <div
      className={cn(
        'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer',
        danger
          ? 'text-danger hover:bg-danger/10'
          : 'text-slate-300 hover:text-white hover:bg-white/5',
      )}
    >
      {icon}
      {label}
    </div>
  )
}
