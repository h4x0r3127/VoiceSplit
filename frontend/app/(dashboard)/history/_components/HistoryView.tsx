'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSession } from 'next-auth/react'
import { motion } from 'framer-motion'
import {
  FileAudio, Search, Trash2, ExternalLink, Loader2,
  CheckCircle, XCircle, Clock, Filter,
} from 'lucide-react'
import { GlassCard } from '@/components/common/GlassCard'
import { GradientButton } from '@/components/common/GradientButton'
import { EmptyState } from '@/components/common/EmptyState'
import { formatBytes, formatRelativeDate, formatDuration, cn } from '@/lib/utils'
import type { Job, JobStatus } from '@/types/job'
import Link from 'next/link'

const STATUS_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'All statuses' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'UPLOADED', label: 'Queued' },
  { value: 'FAILED', label: 'Failed' },
]

const PROCESSING_STATUSES = new Set([
  'PREPROCESSING', 'VAD', 'DIARIZING', 'EMBEDDING',
  'CLUSTERING', 'SEPARATING', 'TRANSCRIBING', 'ANALYZING', 'RECONSTRUCTING',
])

function StatusChip({ status }: { status: string }) {
  if (PROCESSING_STATUSES.has(status)) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-brand-cyan/10 text-brand-cyan text-xs font-medium">
        <Loader2 className="w-3 h-3 animate-spin" /> Processing
      </span>
    )
  }
  const map: Record<string, { color: string; bg: string; icon: typeof CheckCircle }> = {
    COMPLETED: { color: '#22C55E', bg: 'bg-success/10', icon: CheckCircle },
    UPLOADED:  { color: '#06D6CF', bg: 'bg-brand-cyan/10', icon: Clock },
    FAILED:    { color: '#EF4444', bg: 'bg-danger/10', icon: XCircle },
  }
  const cfg = map[status]
  if (!cfg) return <span className="text-xs text-muted">{status}</span>
  const Icon = cfg.icon
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full ${cfg.bg} text-xs font-medium`}
      style={{ color: cfg.color }}
    >
      <Icon className="w-3 h-3" /> {status.charAt(0) + status.slice(1).toLowerCase()}
    </span>
  )
}

export function HistoryView() {
  const { data: session } = useSession()
  const token = session?.accessToken
  const queryClient = useQueryClient()

  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)
  const perPage = 10

  const { data, isLoading } = useQuery<{ items: Job[]; total: number; page: number; per_page: number }>({
    queryKey: ['jobs', 'history', page, statusFilter],
    queryFn: () => {
      const params = new URLSearchParams({ page: String(page), per_page: String(perPage) })
      if (statusFilter) params.set('status_filter', statusFilter)
      return fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      }).then((r) => r.json())
    },
    enabled: !!token,
    refetchInterval: 15000,
  })

  const deleteMutation = useMutation({
    mutationFn: (jobId: string) =>
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/${jobId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['jobs'] }),
  })

  const jobs = (data?.items ?? []).filter((j) =>
    search ? j.original_filename.toLowerCase().includes(search.toLowerCase()) : true,
  )
  const total = data?.total ?? 0
  const totalPages = Math.ceil(total / perPage)

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted pointer-events-none" />
          <input
            type="search"
            placeholder="Search by filename..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-white/5 border border-brand-cyan/10 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white placeholder:text-muted focus:outline-none focus:border-brand-cyan/30 transition-all"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted pointer-events-none" />
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
            className="appearance-none bg-white/5 border border-brand-cyan/10 rounded-xl pl-9 pr-8 py-2.5 text-sm text-white focus:outline-none focus:border-brand-cyan/30 transition-all cursor-pointer"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-card">
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-8 h-8 text-brand-cyan animate-spin" />
        </div>
      ) : jobs.length === 0 ? (
        <EmptyState
          title="No uploads found"
          description={search || statusFilter ? 'Try adjusting your filters' : 'Upload your first audio file to get started'}
          action={!search && !statusFilter ? { label: 'Upload audio', href: '/upload' } : undefined}
        />
      ) : (
        <div className="space-y-2">
          {jobs.map((job, i) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
            >
              <GlassCard hover={false} padding={false}>
                <div className="flex items-center gap-4 p-4">
                  <div className="w-10 h-10 rounded-xl bg-brand-cyan/10 flex items-center justify-center flex-shrink-0">
                    <FileAudio className="w-5 h-5 text-brand-cyan" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{job.original_filename}</p>
                    <p className="text-xs text-muted mt-0.5">
                      {formatBytes(job.file_size_bytes)}
                      {job.duration_seconds ? ` · ${formatDuration(job.duration_seconds)}` : ''}
                      {' · '}{formatRelativeDate(job.created_at)}
                    </p>
                  </div>

                  {PROCESSING_STATUSES.has(job.status) && (
                    <div className="hidden sm:flex items-center gap-2 w-28">
                      <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-brand-cyan to-brand-blue rounded-full transition-all"
                          style={{ width: `${job.progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-muted tabular-nums">{job.progress}%</span>
                    </div>
                  )}

                  <StatusChip status={job.status} />

                  <div className="flex items-center gap-1 flex-shrink-0">
                    {job.status === 'COMPLETED' && (
                      <Link href={`/processing/${job.id}`}>
                        <button className="w-8 h-8 rounded-lg glass flex items-center justify-center text-muted hover:text-brand-cyan transition-colors">
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </Link>
                    )}
                    <button
                      onClick={() => deleteMutation.mutate(job.id.toString())}
                      disabled={deleteMutation.isPending}
                      className="w-8 h-8 rounded-lg glass flex items-center justify-center text-muted hover:text-danger transition-colors disabled:opacity-40"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <p className="text-sm text-muted">
            Showing {Math.min((page - 1) * perPage + 1, total)}–{Math.min(page * perPage, total)} of {total}
          </p>
          <div className="flex gap-2">
            <GradientButton
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </GradientButton>
            <GradientButton
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
            </GradientButton>
          </div>
        </div>
      )}
    </div>
  )
}
