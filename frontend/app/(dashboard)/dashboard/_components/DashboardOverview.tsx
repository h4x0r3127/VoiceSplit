'use client'

import { useQuery } from '@tanstack/react-query'
import { useSession } from 'next-auth/react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  FileAudio,
  Clock,
  Users,
  HardDrive,
  Upload,
  ArrowRight,
  CheckCircle,
  Loader2,
  AlertCircle,
  XCircle,
  LucideIcon,
} from "lucide-react"
import { GlassCard } from '@/components/common/GlassCard'
import { GradientButton } from '@/components/common/GradientButton'
import { EmptyState } from '@/components/common/EmptyState'
import { formatBytes, formatRelativeDate, formatDuration } from '@/lib/utils'
import type { Job } from '@/types/job'
import type { UserAnalytics } from '@/types/user'

const stagger = {
  animate: { transition: { staggerChildren: 0.07 } },
}
const fadeUp = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.35 } },
}

function StatCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: LucideIcon
  label: string
  value: string | number
  color: string
}) {
  return (
    <motion.div variants={fadeUp}>
      <GlassCard hover className="flex items-center gap-4 p-5">
        <div
          className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: `${color}18` }}
        >
          <Icon className="w-5 h-5" style={{ color }} />
        </div>
        <div>
          <p className="text-2xl font-bold text-white">{value}</p>
          <p className="text-sm text-muted">{label}</p>
        </div>
      </GlassCard>
    </motion.div>
  )
}

const STATUS_CONFIG: Record<string, { icon: React.ComponentType<{ className?: string }>; color: string; label: string }> = {
  COMPLETED:   { icon: CheckCircle, color: '#22C55E', label: 'Completed' },
  UPLOADED:    { icon: FileAudio,   color: '#06D6CF', label: 'Queued' },
  FAILED:      { icon: XCircle,     color: '#EF4444', label: 'Failed' },
}
const PROCESSING_STATUSES = new Set([
  'PREPROCESSING', 'VAD', 'DIARIZING', 'EMBEDDING',
  'CLUSTERING', 'SEPARATING', 'TRANSCRIBING', 'ANALYZING', 'RECONSTRUCTING',
])

function JobStatusBadge({ status }: { status: string }) {
  const isProcessing = PROCESSING_STATUSES.has(status)
  const cfg = STATUS_CONFIG[status]
  if (isProcessing) {
    return (
      <span className="flex items-center gap-1.5 text-xs font-medium text-brand-cyan">
        <Loader2 className="w-3.5 h-3.5 animate-spin" />
        Processing
      </span>
    )
  }
  if (!cfg) return <span className="text-xs text-muted">{status}</span>
  const Icon = cfg.icon
  return (
    <span className="flex items-center gap-1.5 text-xs font-medium" style={{ color: cfg.color }}>
      <Icon className="w-3.5 h-3.5" />
      {cfg.label}
    </span>
  )
}

export function DashboardOverview() {
  const { data: session } = useSession()
  const token = session?.accessToken

  const { data: analytics } = useQuery<UserAnalytics>({
    queryKey: ['analytics'],
    queryFn: () =>
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/me/analytics`, {
        headers: { Authorization: `Bearer ${token}` },
      }).then((r) => r.json()),
    enabled: !!token,
  })

  const { data: jobsData } = useQuery<{ items: Job[]; total: number }>({
    queryKey: ['jobs', 'recent'],
    queryFn: () =>
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs?per_page=6`, {
        headers: { Authorization: `Bearer ${token}` },
      }).then((r) => r.json()),
    enabled: !!token,
    refetchInterval: 10000,
  })

  const recentJobs = jobsData?.items ?? []
  const processingJobs = recentJobs.filter((j) => PROCESSING_STATUSES.has(j.status))
  const greetingHour = new Date().getHours()
  const greeting =
    greetingHour < 12 ? 'Good morning' : greetingHour < 18 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <motion.div variants={fadeUp} initial="initial" animate="animate">
        <h1 className="text-2xl font-bold text-white">
          {greeting}, {session?.user?.name?.split(' ')[0] ?? 'there'} 👋
        </h1>
        <p className="text-muted mt-1">Here&apos;s what&apos;s happening with your audio projects.</p>
      </motion.div>

      <motion.div
        variants={stagger}
        initial="initial"
        animate="animate"
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
    <StatCard icon={FileAudio} label="Total uploads"       value={analytics?.total_jobs ?? '—'}              color="#06D6CF" />
        <StatCard icon={Clock}     label="Minutes processed"   value={analytics?.total_minutes_processed ?? '—'} color="#3B82F6" />
        <StatCard icon={Users}     label="Speakers found"      value={analytics?.total_speakers_found ?? '—'}    color="#7C3AED" />
        <StatCard icon={HardDrive} label="Storage used"        value={analytics ? formatBytes(analytics.storage_used_bytes) : '—'} color="#F59E0B" />
      </motion.div>

      {processingJobs.length > 0 && (
        <motion.div variants={fadeUp} initial="initial" animate="animate">
          <h2 className="text-base font-semibold text-white mb-3">Processing queue</h2>
          <div className="space-y-3">
            {processingJobs.map((job) => (
              <GlassCard key={job.id} hover={false} className="p-4">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 min-w-0">
                    <Loader2 className="w-4 h-4 text-brand-cyan animate-spin flex-shrink-0" />
                  <span className="text-sm text-white font-medium truncate">{job.original_filename}</span>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <span className="text-xs text-muted">{job.progress}%</span>
                    <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-brand-cyan to-brand-blue rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${job.progress}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        </motion.div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        <motion.div
          variants={fadeUp}
          initial="initial"
          animate="animate"
          className="lg:col-span-2"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-white">Recent uploads</h2>
            <Link href="/history" className="text-sm text-brand-cyan hover:text-brand-blue transition-colors flex items-center gap-1">
              View all <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {recentJobs.length === 0 ? (
            <EmptyState
              title="No uploads yet"
              description="Upload your first audio file to get started"
              action={{ label: 'Upload audio', href: '/upload' }}
            />
          ) : (
            <div className="space-y-2">
              {recentJobs.slice(0, 5).map((job) => (
                <GlassCard key={job.id} hover className="p-4" padding={false}>
                  <Link href={`/processing/${job.id}`}>
                    <div className="flex items-center gap-4 p-4">
                      <div className="w-9 h-9 rounded-xl bg-brand-cyan/10 flex items-center justify-center flex-shrink-0">
                        <FileAudio className="w-4 h-4 text-brand-cyan" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">{job.original_filename}</p>
                        <p className="text-xs text-muted mt-0.5">
                          {formatBytes(job.file_size_bytes)}
                          {job.duration_seconds ? ` · ${formatDuration(job.duration_seconds)}` : ''}
                          {' · '}{formatRelativeDate(job.created_at)}
                        </p>
                      </div>
                      <JobStatusBadge status={job.status} />
                    </div>
                  </Link>
                </GlassCard>
              ))}
            </div>
          )}
        </motion.div>

        <motion.div variants={fadeUp} initial="initial" animate="animate">
          <h2 className="text-base font-semibold text-white mb-4">Quick upload</h2>
          <Link href="/upload">
            <GlassCard
              hover
              className="flex flex-col items-center justify-center text-center py-10 border-dashed border-2 border-brand-cyan/20 hover:border-brand-cyan/40 transition-colors"
            >
              <div className="w-14 h-14 rounded-2xl bg-brand-cyan/10 flex items-center justify-center mb-4">
                <Upload className="w-6 h-6 text-brand-cyan" />
              </div>
              <p className="text-white font-medium mb-1">Upload audio</p>
              <p className="text-xs text-muted">MP3, WAV, AAC, FLAC, OGG</p>
            </GlassCard>
          </Link>
        </motion.div>
      </div>
    </div>
  )
}
