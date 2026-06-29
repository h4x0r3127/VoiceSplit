'use client'

import { useState } from 'react'
import { Play, Pause, Check } from 'lucide-react'
import { motion } from 'framer-motion'
import { cn, formatDuration } from '@/lib/utils'
import { SpeakerAvatar } from './SpeakerAvatar'
import type { Speaker } from '@/types/speaker'

interface SpeakerCardProps {
  speaker: Speaker
  index: number
  isSelected: boolean
  onToggle: (id: string) => void
}

const GENDER_LABELS: Record<string, string> = {
  male: '♂ Male',
  female: '♀ Female',
  unknown: '? Unknown',
}

export function SpeakerCard({ speaker, index, isSelected, onToggle }: SpeakerCardProps) {
  const [isPreviewPlaying, setIsPreviewPlaying] = useState(false)

  const handlePreview = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (!speaker.preview_s3_key) return
    setIsPreviewPlaying((p) => !p)
  }

  const confidencePct = Math.round(speaker.confidence * 100)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={cn(
        'relative glass rounded-2xl overflow-hidden transition-all duration-300 cursor-pointer select-none',
        isSelected
          ? 'shadow-[0_0_30px_rgba(6,214,207,0.2)]'
          : 'hover:border-white/15',
      )}
      style={{
        borderTop: `3px solid ${speaker.color}`,
        border: isSelected ? `1px solid ${speaker.color}50` : undefined,
      }}
      onClick={() => onToggle(speaker.id)}
    >
      {/* Selection indicator */}
      <div className={cn(
        'absolute top-3 right-3 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-200 z-10',
        isSelected ? 'border-transparent' : 'border-white/20',
      )}
        style={isSelected ? { background: speaker.color } : {}}
      >
        {isSelected && <Check className="w-3 h-3 text-white" />}
      </div>

      <div className="p-5">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <SpeakerAvatar
            label={speaker.label}
            color={speaker.color}
            size="md"
            selected={isSelected}
            index={index}
          />
          <div className="min-w-0 flex-1">
            <h3 className="font-semibold text-white truncate">{speaker.label}</h3>
            <p className="text-xs text-muted">{formatDuration(speaker.speaking_duration)} speaking</p>
          </div>
        </div>

        {/* Attributes */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {speaker.gender && (
            <span className="px-2 py-0.5 rounded-full text-xs bg-white/5 text-muted border border-white/10">
              {GENDER_LABELS[speaker.gender] ?? speaker.gender}
            </span>
          )}
          {speaker.age_range && (
            <span className="px-2 py-0.5 rounded-full text-xs bg-white/5 text-muted border border-white/10">
              {speaker.age_range}
            </span>
          )}
          {speaker.language && (
            <span className="px-2 py-0.5 rounded-full text-xs bg-white/5 text-muted border border-white/10">
              {speaker.language.toUpperCase()}
            </span>
          )}
          {speaker.emotion && (
            <span
              className="px-2 py-0.5 rounded-full text-xs border"
              style={{ color: speaker.color, background: `${speaker.color}15`, borderColor: `${speaker.color}30` }}
            >
              {speaker.emotion}
            </span>
          )}
        </div>

        {/* Confidence */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-muted">Confidence</span>
            <span className="text-xs font-medium" style={{ color: speaker.color }}>{confidencePct}%</span>
          </div>
          <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ background: speaker.color }}
              initial={{ width: 0 }}
              animate={{ width: `${confidencePct}%` }}
              transition={{ duration: 0.8, delay: 0.2 }}
            />
          </div>
        </div>

        {/* Waveform */}
        <div className="h-8 w-full rounded bg-white/5" />

        {/* Preview */}
        {speaker.preview_s3_key && (
          <button
            onClick={handlePreview}
            className="mt-3 flex items-center gap-2 text-xs text-muted hover:text-white transition-colors w-full"
          >
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ background: `${speaker.color}20` }}
            >
              {isPreviewPlaying ? (
                <Pause className="w-3.5 h-3.5" style={{ color: speaker.color }} />
              ) : (
                <Play className="w-3.5 h-3.5" style={{ color: speaker.color }} />
              )}
            </div>
            {isPreviewPlaying ? 'Pause preview' : 'Play preview'}
          </button>
        )}
      </div>
    </motion.div>
  )
}
