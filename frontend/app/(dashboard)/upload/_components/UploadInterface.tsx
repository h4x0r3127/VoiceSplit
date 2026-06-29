'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CloudUpload, FileAudio, AlertCircle, Mic, Music, Volume2,
} from 'lucide-react'
import { GradientButton } from '@/components/common/GradientButton'
import { GlassCard } from '@/components/common/GlassCard'
import { formatBytes } from '@/lib/utils'
import { useUploadQueue } from '@/hooks/useUploadQueue'
import { UploadQueue } from './UploadQueue'
import { AudioPreview } from './AudioPreview'
import type { FileRejection } from 'react-dropzone'

const ACCEPTED_TYPES: Record<string, string[]> = {
  'audio/mpeg':   ['.mp3'],
  'audio/wav':    ['.wav'],
  'audio/x-wav':  ['.wav'],
  'audio/aac':    ['.aac'],
  'audio/mp4':    ['.m4a'],
  'audio/x-m4a':  ['.m4a'],
  'audio/flac':   ['.flac'],
  'audio/x-flac': ['.flac'],
  'audio/ogg':    ['.ogg'],
}

const FORMAT_BADGES = ['MP3', 'WAV', 'AAC', 'M4A', 'FLAC', 'OGG']
const MAX_SIZE_MB = 500

export function UploadInterface() {
  const router = useRouter()
  const { data: session } = useSession()
  const { upload, items } = useUploadQueue()

  const [previewFile, setPreviewFile] = useState<File | null>(null)
  const [dropError, setDropError] = useState<string | null>(null)

  const onDrop = useCallback(
    async (accepted: File[], rejected: readonly FileRejection[]) => {
      setDropError(null)
      if (rejected.length > 0) {
        setDropError(rejected[0]?.errors?.[0]?.message ?? 'Unsupported file or size exceeded')
        return
      }
      if (accepted.length === 0) return

      // Show preview of first file
      setPreviewFile(accepted[0])

      // Enqueue & start uploads
      const result = await upload(accepted)
      if (result?.errors?.length) {
        setDropError(result.errors[0])
      }
    },
    [upload],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: MAX_SIZE_MB * 1024 * 1024,
    multiple: true,
  })

  // Navigate to processing page when the first upload completes
  const firstUploaded = items.find((i) => i.status === 'uploaded')

  return (
    <div className="space-y-6">
      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`
          relative flex flex-col items-center justify-center text-center
          rounded-2xl border-2 border-dashed py-16 px-8 cursor-pointer
          transition-all duration-300 select-none
          ${isDragActive
            ? 'border-brand-cyan bg-brand-cyan/5 shadow-[0_0_30px_rgba(6,214,207,0.15)]'
            : 'border-brand-cyan/20 bg-white/[0.02] hover:border-brand-cyan/40 hover:bg-brand-cyan/5'
          }
        `}
      >
        <input {...getInputProps()} />

        <motion.div
          animate={isDragActive ? { scale: 1.08, rotate: -3 } : { scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          className="mb-5"
        >
          <div className="w-20 h-20 rounded-2xl bg-brand-cyan/10 flex items-center justify-center mx-auto">
            <CloudUpload
              className={`w-10 h-10 transition-colors ${isDragActive ? 'text-brand-cyan' : 'text-brand-cyan/60'}`}
            />
          </div>
        </motion.div>

        <h3 className="text-xl font-semibold text-white mb-2">
          {isDragActive ? 'Drop to upload' : 'Drop audio files here'}
        </h3>
        <p className="text-sm text-muted mb-5">
          or{' '}
          <span className="text-brand-cyan font-medium">click to browse</span>
          {' '}— up to {MAX_SIZE_MB} MB · multiple files supported
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
      </div>

      {/* Drop error */}
      <AnimatePresence>
        {dropError && (
          <motion.div
            key="drop-error"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="flex items-center gap-3 p-4 rounded-xl bg-danger/10 border border-danger/30"
          >
            <AlertCircle className="w-5 h-5 text-danger flex-shrink-0" />
            <p className="text-sm text-danger">{dropError}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Audio preview */}
      <AnimatePresence>
        {previewFile && (
          <motion.div
            key="preview"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <h3 className="text-sm font-semibold text-white mb-3">Preview</h3>
            <AudioPreview file={previewFile} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload queue */}
      <AnimatePresence>
        {items.length > 0 && (
          <motion.div
            key="queue"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-white">Uploads</h3>
              {firstUploaded?.jobId && (
                <GradientButton
                  size="sm"
                  onClick={() => router.push(`/processing/${firstUploaded.jobId}`)}
                >
                  View processing →
                </GradientButton>
              )}
            </div>
            <UploadQueue />
          </motion.div>
        )}
      </AnimatePresence>

      {/* How it works */}
      {items.length === 0 && (
        <GlassCard hover={false} className="p-5">
          <h3 className="text-sm font-semibold text-white mb-4">What happens next?</h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            {[
              { icon: Mic,    label: 'Speaker detection', desc: 'AI identifies each voice' },
              { icon: Volume2, label: 'Voice isolation',  desc: 'Separate speaker tracks' },
              { icon: Music,  label: 'Clean output',      desc: 'Download selected voices' },
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
      )}
    </div>
  )
}
