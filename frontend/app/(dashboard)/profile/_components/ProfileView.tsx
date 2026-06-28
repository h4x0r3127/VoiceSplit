'use client'

import { useQuery } from '@tanstack/react-query'
import { useSession, signOut } from 'next-auth/react'
import { motion } from 'framer-motion'
import { FileAudio, Clock, Users, HardDrive, LogOut, Zap, Calendar } from 'lucide-react'
import { GlassCard } from '@/components/common/GlassCard'
import { GradientButton } from '@/components/common/GradientButton'
import { formatBytes, formatDate, getInitials } from '@/lib/utils'
import type { UserAnalytics } from '@/types/user'

const fadeUp = {
  initial: { opacity: 0, y: 16 },
  animate: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.08, duration: 0.35 } }),
}

export function ProfileView() {
  const { data: session } = useSession()
  const token = session?.accessToken
  const user = session?.user

  const { data: analytics } = useQuery<UserAnalytics>({
    queryKey: ['analytics'],
    queryFn: () =>
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/me/analytics`, {
        headers: { Authorization: `Bearer ${token}` },
      }).then((r) => r.json()),
    enabled: !!token,
  })

  const stats = [
    { icon: FileAudio, label: 'Total uploads',    value: analytics?.total_jobs ?? '—',               color: '#06D6CF' },
    { icon: Clock,     label: 'Minutes processed', value: analytics?.total_minutes_processed ?? '—',  color: '#3B82F6' },
    { icon: Users,     label: 'Speakers found',   value: analytics?.total_speakers_found ?? '—',     color: '#7C3AED' },
    { icon: HardDrive, label: 'Storage used',     value: analytics ? formatBytes(analytics.storage_used_bytes) : '—', color: '#F59E0B' },
  ]

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
      >
        <GlassCard hover={false}>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
            <div className="relative flex-shrink-0">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-cyan via-brand-blue to-brand-purple flex items-center justify-center text-2xl font-bold text-white shadow-glow">
                {getInitials(user?.name ?? 'User')}
              </div>
              <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-success border-2 border-background" />
            </div>

            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h2 className="text-xl font-bold text-white">{user?.name ?? 'User'}</h2>
                <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-brand-cyan/10 text-brand-cyan text-xs font-medium">
                  <Zap className="w-3 h-3" /> Free plan
                </span>
              </div>
              <p className="text-sm text-muted">{user?.email}</p>
              <div className="flex items-center gap-1.5 mt-2 text-xs text-muted">
                <Calendar className="w-3.5 h-3.5" />
                Member since {formatDate(new Date().toISOString())}
              </div>
            </div>

            <GradientButton
              variant="ghost"
              size="sm"
              onClick={() => signOut({ callbackUrl: '/login' })}
              className="flex-shrink-0"
            >
              <LogOut className="w-4 h-4" />
              Sign out
            </GradientButton>
          </div>
        </GlassCard>
      </motion.div>

      <div className="grid grid-cols-2 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon
          return (
            <motion.div key={stat.label} custom={i} variants={fadeUp} initial="initial" animate="animate">
              <GlassCard hover className="flex items-center gap-4 p-5">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: `${stat.color}15` }}
                >
                  <Icon className="w-5 h-5" style={{ color: stat.color }} />
                </div>
                <div>
                  <p className="text-xl font-bold text-white">{stat.value}</p>
                  <p className="text-xs text-muted">{stat.label}</p>
                </div>
              </GlassCard>
            </motion.div>
          )
        })}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <GlassCard hover={false}>
          <h3 className="text-sm font-semibold text-white mb-4">Plan &amp; credits</h3>
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-muted">Available credits</span>
            <span className="text-sm font-semibold text-brand-cyan">300 credits</span>
          </div>
          <div className="h-2 bg-white/10 rounded-full overflow-hidden mb-3">
            <div className="h-full w-full bg-gradient-to-r from-brand-cyan to-brand-blue rounded-full" />
          </div>
          <p className="text-xs text-muted">
            Credits reset on the 1st of each month. Upgrade for more.
          </p>
          <div className="mt-4 pt-4 border-t border-brand-cyan/10">
            <GradientButton size="sm">
              <Zap className="w-3.5 h-3.5" />
              Upgrade to Pro
            </GradientButton>
          </div>
        </GlassCard>
      </motion.div>
    </div>
  )
}
