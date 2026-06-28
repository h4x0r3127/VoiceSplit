'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CloudUpload, FileAudio, X, CheckCircle, AlertCircle,
  Mic, Music, Volume2,
} from 'lucide-react'
import { GradientButton } from '@/components/common/GradientButton'
import { GlassCard } from '@/components/common/GlassCard'
import { formatBytes } from '@/lib/utils'

const ACCEPTED_TYPES: Record<string, string[]> = {
  'audio/mpeg':      ['.mp3'],
  'audio/wav':       ['.wav'],
  'audio/x-wav':     ['.wav'],
  'audio/aac':       ['.aac'],
  'audio/mp4':       ['.m4a'],
  'audio/x-m4a':     ['.m4a'],
  'audio/flac':      ['.flac'],
  'audio/x-flac':    ['.flac'],
  'audio/ogg':       ['.ogg'],
}

const FORMAT_BADGES = ['MP3', 'WAV', 'AAC', 'M4A', 'FLAC', 'OGG']
const MAX_SIZE_MB = 500

type UploadPhase = 'idle' | 'selected' | 'uploading' | 'success' | 'error'

export function UploadInterface() {
  const router = useRouter()
  const { data: session } = useSession()
  const [phase, setPhase] = useState<UploadPhase>('idle')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [progress, setProgress] = useState(0)
  const [errorMessage, setErrorMessage] = useState('')

  const onDrop = useCallback((accepted: File[], rejected: { errors: { message: string }[] }[]) => {
    if (rejected.length > 0) {
      const msg = rejected[0]?.errors[0]?.message ?? 'Unsupported file'
      setErrorMessage(msg)
      setPhase('error')
      return
    }
    if (accepted.length > 0) {
      setSelectedFile(accepted[0])
      setPhase('selected')
      setErrorMessage('')
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: MAX_SIZE_MB * 1024 * 1024,
    multiple: false,
  })

  function clearSelection() {
    setSelectedFile(null)
    setPhase('idle')
    setProgress(0)
    setErrorMessage('')
  }

  async function handleUpload() {
    if (!selectedFile || !session?.accessToken) return
    setPhase('uploading')
    setProgress(0)

    const formData = new FormData()
    formData.append('file', selectedFile)

    return new Promise<void>((resolve) => {
      const xhr = new XMLHttpRequest()
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) setProgress(Math.round((e.loaded / e.total) * 100))
      }
      xhr.onload = () => {
        if (xhr.status === 201) {
          const job = JSON.parse(xhr.response)
          setPhase('success')
          setTimeout(() => router.push(`/history`), 1200)
        } else {
          const err = JSON.parse(xhr.response).detail ?? 'Upload failed'
          setErrorMessage(err)
          setPhase('error')
        }
        resolve()
      }
      xhr.onerror = () => {
        setErrorMessage('Network error. Please check your connection.')
        setPhase('error')
        resolve()
      }
      xhr.open('POST', `${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/upload`)
      xhr.setRequestHeader('Authorization', `Bearer ${session.accessToken}`)
      xhr.send(formData)
    })
  }

  return (
    <div className="space-y-6">
      <AnimatePresence mode="wait">
        {(phase === 'idle' || phase === 'error') && (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
          >
            <div
              {...getRootProps()}
              className={`
                relative flex flex-col items-center justify-center text-center
                rounded-2xl border-2 border-dashed py-20 px-8 cursor-pointer
                transition-all duration-300
                ${isDragActive
                  ? 'border-brand-cyan bg-brand-cyan/5 shadow-glow'
                  : 'border-brand-cyan/20 bg-white/[0.02] hover:border-brand-cyan/40 hover:bg-brand-cyan/5'
                }
              `}
            >
              <input {...getInputProps()} />

              <motion.div
                animate={isDragActive ? { scale: 1.1 } : { scale: 1 }}
                className="mb-6"
              >
                <div className="w-20 h-20 rounded-2xl bg-brand-cyan/10 flex items-center justify-center mx-auto mb-2">
                  <CloudUpload className={`w-10 h-10 transition-colors ${isDragActive ? 'text-brand-cyan' : 'text-brand-cyan/60'}`} />
                </div>
              </motion.div>

              <h3 className="text-xl font-semibold text-white mb-2">
                {isDragActive ? 'Drop it here' : 'Drop your audio file here'}
              </h3>
              <p className="text-muted text-sm mb-6">
                or{' '}
                <span className="text-brand-cyan font-medium">click to browse</span>
                {' '}your computer
              </p>

              <div className="flex flex-wrap justify-center gap-2">
                {FORMAT_BADGES.map((fmt) => (
                  <span
                    key={fmt}
                    className="px-2.5 py-1 rounded-lg bg-white/5 border border-brand-cyan/10 text-xs font-mono text-muted"
                  >
                    {fmt}
                  </span>
                ))}
              </div>

              <p className="mt-4 text-xs text-muted/60">Max file size: {MAX_SIZE_MB} MB</p>
            </div>

            {phase === 'error' && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 p-4 rounded-xl bg-danger/10 border border-danger/30 flex items-center gap-3"
              >
                <AlertCircle className="w-5 h-5 text-danger flex-shrink-0" />
                <p className="text-sm text-danger">{errorMessage}</p>
              </motion.div>
            )}
          </motion.div>
        )}

        {phase === 'selected' && selectedFile && (
          <motion.div
            key="selected"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
          >
            <GlassCard hover={false} className="p-6">
              <div className="flex items-start justify-between gap-4 mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-brand-cyan/10 flex items-center justify-center flex-shrink-0">
                    <FileAudio className="w-6 h-6 text-brand-cyan" />
                  </div>
                  <div>
                    <p className="font-semibold text-white">{selectedFile.name}</p>
                    <p className="text-sm text-muted">{formatBytes(selectedFile.size)}</p>
                  </div>
                </div>
                <button
                  onClick={clearSelection}
                  className="w-8 h-8 rounded-lg glass flex items-center justify-center text-muted hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="flex gap-3">
                <GradientButton onClick={handleUpload} size="md" className="flex-1">
                  <CloudUpload className="w-4 h-4" />
                  Start upload
                </GradientButton>
                <GradientButton onClick={clearSelection} variant="ghost" size="md">
                  Cancel
                </GradientButton>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {phase === 'uploading' && (
          <motion.div
            key="uploading"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <GlassCard hover={false} className="p-6">
              <div className="flex items-center gap-4 mb-5">
                <div className="w-12 h-12 rounded-xl bg-brand-cyan/10 flex items-center justify-center flex-shrink-0">
                  <FileAudio className="w-6 h-6 text-brand-cyan" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-white truncate">{selectedFile?.name}</p>
                  <p className="text-sm text-muted">{formatBytes(selectedFile?.size ?? 0)}</p>
                </div>
                <span className="text-sm font-mono text-brand-cyan tabular-nums">{progress}%</span>
              </div>

              <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-brand-cyan via-brand-blue to-brand-purple rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
              <p className="mt-3 text-xs text-muted text-center">
                Uploading — please don&apos;t close this tab
              </p>
            </GlassCard>
          </motion.div>
        )}

        {phase === 'success' && (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <GlassCard hover={false} className="p-10 text-center">
              <div className="w-16 h-16 rounded-full bg-success/15 flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-success" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Upload complete</h3>
              <p className="text-muted text-sm">Redirecting to your history...</p>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      <GlassCard hover={false} className="p-5">
        <h3 className="text-sm font-semibold text-white mb-3">What happens after upload?</h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          {[
            { icon: Mic, label: 'Speaker detection', desc: 'AI identifies each voice' },
            { icon: Volume2, label: 'Voice isolation', desc: 'Separate speaker tracks' },
            { icon: Music, label: 'Clean output', desc: 'Download selected voices' },
          ].map(({ icon: Icon, label, desc }) => (
            <div key={label} className="flex flex-col items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-brand-cyan/10 flex items-center justify-center">
                <Icon className="w-5 h-5 text-brand-cyan" />
              </div>
              <p className="text-xs font-medium text-white">{label}</p>
              <p className="text-xs text-muted">{desc}</p>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  )
}
