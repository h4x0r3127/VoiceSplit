'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import {
  CheckCircle, XCircle, Loader2, FileAudio,
  Clock, HardDrive, Music2, Mic2, ArrowLeft, RefreshCw,
} from 'lucide-react'
import { GlassCard } from '@/components/common/GlassCard'
import { GradientButton } from '@/components/common/GradientButton'
import { useJobWebSocket } from '@/hooks/useJobWebSocket'
import { formatBytes, formatDuration, formatRelativeDate } from '@/lib/utils'
import type { Job } from '@/types/job'

// Pipeline stages shown in the UI (Phase 3 uses PREPROCESSING + COMPLETED)
const PIPELINE_STEPS = [
  { key: 'DOWNLOADING',        label: 'Downloading',       desc: 'Fetching audio from storage' },
  { key: 'EXTRACTING_METADATA',label: 'Extracting metadata', desc: 'Reading duration, codec, sample rate' },
  { key: 'SAVING_METADATA',    label: 'Saving',            desc: 'Persisting metadata to database' },
  // Phase 4 stages (shown as upcoming)
  { key: 'VAD',                label: 'Voice detection',   desc: 'Locating speech regions' },
  { key: 'DIARIZING',          label: 'Diarization',       desc: 'Identifying speakers' },
  { key: 'SEPARATING',         label: 'Separation',        desc: 'Isolating each voice' },
  { key: 'RECONSTRUCTING',     label: 'Reconstruction',    desc: 'Building final audio' },
]

type PhaseStatus = 'pending' | 'active' | 'done' | 'skipped'

function getStepStatus(
  stepKey: string,
  currentStage: string | null | undefined,
  jobStatus: string,
  progress: number,
): PhaseStatus {
  if (jobStatus === 'COMPLETED') return 'done'
  if (jobStatus === 'FAILED') return 'skipped'

  const activePhase3 = ['DOWNLOADING', 'EXTRACTING_METADATA', 'SAVING_METADATA']
  const currentIdx = activePhase3.indexOf(currentStage ?? '')
  const stepIdx = activePhase3.indexOf(stepKey)

  if (stepIdx === -1) return 'pending'           // Phase 4 step — not started yet
  if (stepIdx < currentIdx) return 'done'
  if (stepIdx === currentIdx) return 'active'
  return 'pending'
}

function StepIcon({ status }: { status: PhaseStatus }) {
  if (status === 'done')    return <CheckCircle className="w-5 h-5 text-success" />
  if (status === 'active')  return <Loader2 className="w-5 h-5 text-brand-cyan animate-spin" />
  if (status === 'skipped') return <XCircle className="w-5 h-5 text-danger" />
  return <div className="w-5 h-5 rounded-full border-2 border-white/20" />
}

interface ProcessingStatusViewProps {
  jobId: string
}

export function ProcessingStatusView({ jobId }: ProcessingStatusViewProps) {
  const router = useRouter()
  const { data: session } = useSession()
  const token = session?.accessToken

  const [wsProgress, setWsProgress] = useState<number | null>(null)
  const [wsStage, setWsStage] = useState<string | null>(null)
  const [wsStatus, setWsStatus] = useState<string | null>(null)
  const [wsMessage, setWsMessage] = useState<string | null>(null)
  const [wsError, setWsError] = useState<string | null>(null)

  // Fetch initial job data
  const { data: job, refetch } = useQuery<Job>({
    queryKey: ['job', jobId],
    queryFn: () =>
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/${jobId}`, {
        headers: { Authorization: `Bearer ${token}` },
      }).then((r) => r.json()),
    enabled: !!token,
    refetchInterval: wsStatus && ['COMPLETED', 'FAILED'].includes(wsStatus) ? false : 5000,
  })

  // WebSocket for real-time updates
  const { latest, isConnected, isTerminal } = useJobWebSocket({
    jobId,
    token,
    enabled: !!token && !!job && !['COMPLETED', 'FAILED'].includes(job.status),
    onComplete: () => {
      refetch()

      setTimeout(() => {
        router.push(`/results/${jobId}`)
      }, 1000)
    },
    
    onFailed: (event) => {
      setWsError(event.error ?? 'Processing failed')
      refetch()
    },
  })

  // Sync WS events to state
  useEffect(() => {
    if (!latest || latest.type === 'ping') return
    setWsProgress(latest.progress)
    setWsStage(latest.stage)
    setWsStatus(latest.status)
    setWsMessage(latest.message)
    if (latest.error) setWsError(latest.error)
  }, [latest])

  const effectiveStatus = wsStatus ?? job?.status ?? 'UPLOADED'
  const effectiveProgress = wsProgress ?? job?.progress ?? 0
  const effectiveStage = wsStage ?? job?.pipeline_stage ?? null
  const isCompleted = effectiveStatus === 'COMPLETED'
  const isFailed = effectiveStatus === 'FAILED'
  const isProcessing = !isCompleted && !isFailed

  const metadata = job?.audio_metadata as Record<string, unknown> | undefined

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-2">
        <Link href="/history">
          <button className="w-8 h-8 rounded-lg glass flex items-center justify-center text-muted hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-white">
            {isCompleted ? 'Processing complete' : isFailed ? 'Processing failed' : 'Processing…'}
          </h1>
          <p className="text-muted text-sm mt-0.5">
            {job?.original_filename ?? 'Loading…'}
          </p>
        </div>
      </div>

      {/* Status card */}
      <GlassCard hover={false} glow={isCompleted}>
        <div className="flex items-center gap-4 mb-6">
          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0 ${
            isCompleted ? 'bg-success/15' : isFailed ? 'bg-danger/15' : 'bg-brand-cyan/10'
          }`}>
            {isCompleted && <CheckCircle className="w-7 h-7 text-success" />}
            {isFailed   && <XCircle className="w-7 h-7 text-danger" />}
            {isProcessing && <Loader2 className="w-7 h-7 text-brand-cyan animate-spin" />}
          </div>

          <div className="flex-1">
            <div className="flex items-center justify-between gap-2 mb-2">
              <p className="text-base font-semibold text-white">
                {wsMessage ?? (isCompleted ? 'All done!' : isFailed ? 'An error occurred' : 'Processing your audio…')}
              </p>
              <span className="text-sm font-mono text-brand-cyan tabular-nums">
                {effectiveProgress}%
              </span>
            </div>

            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                className={`h-full rounded-full ${
                  isFailed
                    ? 'bg-danger'
                    : 'bg-gradient-to-r from-brand-cyan via-brand-blue to-brand-purple'
                }`}
                animate={{ width: `${effectiveProgress}%` }}
                transition={{ duration: 0.4, ease: 'easeOut' }}
              />
            </div>

            {/* WS connection indicator */}
            <div className="flex items-center gap-1.5 mt-2">
              <div className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-success animate-pulse' : 'bg-muted'}`} />
              <span className="text-xs text-muted">
                {isConnected ? 'Live updates active' : 'Polling for updates'}
              </span>
            </div>
          </div>
        </div>

        {/* Error */}
        {(wsError || (isFailed && job?.error_message)) && (
          <div className="mb-4 p-3 rounded-xl bg-danger/10 border border-danger/30 text-sm text-danger">
            {wsError ?? job?.error_message}
          </div>
        )}

        {/* Pipeline steps */}
        <div className="space-y-2">
          {PIPELINE_STEPS.map((step, idx) => {
            const stepStatus = getStepStatus(step.key, effectiveStage, effectiveStatus, effectiveProgress)
            const isActive = stepStatus === 'active'

            return (
              <div
                key={step.key}
                className={`flex items-center gap-3 p-3 rounded-xl transition-all ${
                  isActive ? 'bg-brand-cyan/5 border border-brand-cyan/20' : ''
                }`}
              >
                <StepIcon status={stepStatus} />
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${
                    stepStatus === 'done'   ? 'text-success' :
                    stepStatus === 'active' ? 'text-white' :
                    stepStatus === 'skipped'? 'text-danger' :
                    'text-muted'
                  }`}>
                    {step.label}
                    {idx > 2 && (
                      <span className="ml-2 text-xs text-muted font-normal">(Phase 4)</span>
                    )}
                  </p>
                  {isActive && (
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-xs text-muted mt-0.5"
                    >
                      {step.desc}
                    </motion.p>
                  )}
                </div>
                {stepStatus === 'done' && (
                  <CheckCircle className="w-4 h-4 text-success/60 flex-shrink-0" />
                )}
              </div>
            )
          })}
        </div>
      </GlassCard>

      {/* Metadata card — shown when complete */}
      <AnimatePresence>
        {isCompleted && metadata && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <GlassCard hover={false}>
              <h2 className="text-base font-semibold text-white mb-4">Audio details</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
{
    icon: Clock,
    label: 'Duration',
    value: formatDuration(Number(metadata.duration_seconds ?? 0)),
  },
  {
    icon: HardDrive,
    label: 'File size',
    value: formatBytes(Number(metadata.file_size_bytes ?? job?.file_size_bytes ?? 0)),
  },
  {
    icon: Music2,
    label: 'Format',
    value: String(metadata.format ?? 'Unknown').toUpperCase(),
  },
  {
    icon: Mic2,
    label: 'Sample rate',
    value: metadata.sample_rate
      ? `${Number(metadata.sample_rate) / 1000} kHz`
      : 'Unknown',
  },
].map(({ icon: Icon, label, value }) => (
                  <div key={label} className="flex flex-col gap-1">
                    <div className="flex items-center gap-1.5 text-muted">
                      <Icon className="w-3.5 h-3.5" />
                      <span className="text-xs">{label}</span>
                    </div>
                    <p className="text-sm font-semibold text-white">{value}</p>
                  </div>
                ))}
              </div>

              {metadata.channels && (
                <div className="mt-3 pt-3 border-t border-brand-cyan/10 grid grid-cols-2 sm:grid-cols-3 gap-4">
                  {metadata.channels && (
                    <div>
                      <p className="text-xs text-muted">Channels</p>
                      <p className="text-sm font-semibold text-white">
                        {metadata.channels === 1 ? 'Mono' : metadata.channels === 2 ? 'Stereo' : String(metadata.channels)}
                      </p>
                    </div>
                  )}
                  {metadata.bitrate_kbps && (
                    <div>
                      <p className="text-xs text-muted">Bitrate</p>
                      <p className="text-sm font-semibold text-white">{String(metadata.bitrate_kbps)} kbps</p>
                    </div>
                  )}
                  {metadata.codec && (
                    <div>
                      <p className="text-xs text-muted">Codec</p>
                      <p className="text-sm font-semibold text-white capitalize">{String(metadata.codec)}</p>
                    </div>
                  )}
                </div>
              )}
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Actions */}
      <AnimatePresence>
        {(isCompleted || isFailed) && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex items-center gap-3"
          >
            {isCompleted && (
              <GradientButton
              size="md"
              onClick={() => router.push(`/results/${jobId}`)}
              >
                <CheckCircle className="w-4 h-4" />
                View Results
              </GradientButton>
            )}
            
            {isFailed && (
              <GradientButton size="md" onClick={() => router.push('/upload')}>
                <RefreshCw className="w-4 h-4" />
                Upload again
              </GradientButton>
            )}
            <GradientButton variant="outline" size="md" onClick={() => router.push('/upload')}>
              Upload another
            </GradientButton>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
