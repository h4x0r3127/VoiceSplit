'use client'

import { motion } from 'framer-motion'
import { Play, Pause, Download } from 'lucide-react'
import { useState } from 'react'
import { GlassCard } from '@/components/common/GlassCard'
import { GradientButton } from '@/components/common/GradientButton'

const speakers = [
  { label: 'Speaker 1', color: '#06D6CF', duration: '4:32', pct: 52 },
  { label: 'Speaker 2', color: '#3B82F6', duration: '2:48', pct: 32 },
  { label: 'Speaker 3', color: '#7C3AED', duration: '1:24', pct: 16 },
]

export function InteractiveDemo() {
  const [selected, setSelected] = useState<number[]>([0])
  const [playing, setPlaying] = useState(false)

  const toggle = (i: number) => {
    setSelected((prev) =>
      prev.includes(i) ? prev.filter((x) => x !== i) : [...prev, i],
    )
  }

  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <span className="inline-block px-4 py-1.5 rounded-full glass border border-brand-cyan/20 text-brand-cyan text-sm font-medium mb-4">
            Interactive Demo
          </span>
          <h2 className="text-4xl font-bold text-white mb-4">
            See it in <span className="gradient-text">action</span>
          </h2>
          <p className="text-muted max-w-xl mx-auto">
            Select which speakers to keep, then isolate them with one click.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <GlassCard className="p-8" glow>
            {/* Timeline mockup */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs text-muted font-mono">0:00</span>
                <span className="text-xs text-muted font-mono">8:44</span>
              </div>
              <div className="space-y-2">
                {speakers.map((s, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-xs text-muted w-20 text-right">{s.label}</span>
                    <div className="flex-1 h-8 bg-white/5 rounded-lg overflow-hidden">
                      <motion.div
                        className="h-full rounded-lg flex items-center gap-0.5 px-1 overflow-hidden"
                        style={{ width: `${s.pct}%`, background: `${s.color}25`, borderRight: `2px solid ${s.color}` }}
                        initial={{ width: 0 }}
                        whileInView={{ width: `${s.pct}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.7, delay: i * 0.15 }}
                      >
                        {Array.from({ length: 10 }).map((_, j) => (
                          <div key={j} className="flex-1 rounded-sm" style={{ height: `${30 + Math.random() * 60}%`, background: s.color }} />
                        ))}
                      </motion.div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Speaker cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              {speakers.map((s, i) => {
                const isSelected = selected.includes(i)
                return (
                  <button
                    key={i}
                    onClick={() => toggle(i)}
                    className={`p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                      isSelected
                        ? 'border-current shadow-[0_0_20px_rgba(6,214,207,0.2)]'
                        : 'border-white/10 hover:border-white/20'
                    }`}
                    style={{ borderColor: isSelected ? s.color : undefined }}
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white" style={{ background: s.color }}>
                        S{i + 1}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{s.label}</p>
                        <p className="text-xs text-muted">{s.duration}</p>
                      </div>
                      <div className={`ml-auto w-5 h-5 rounded-full border-2 flex items-center justify-center ${isSelected ? 'border-current bg-current' : 'border-white/20'}`} style={{ borderColor: isSelected ? s.color : undefined, background: isSelected ? s.color : undefined }}>
                        {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
                      </div>
                    </div>
                    <div className="h-1.5 bg-white/10 rounded-full">
                      <div className="h-full rounded-full" style={{ width: `${s.pct}%`, background: s.color }} />
                    </div>
                    <p className="text-xs text-muted mt-1">{s.pct}% speaking time</p>
                  </button>
                )
              })}
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => setPlaying((p) => !p)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl glass text-sm text-muted hover:text-white transition-colors"
              >
                {playing ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                {playing ? 'Pause Preview' : 'Play Preview'}
              </button>
              <div className="flex items-center gap-3">
                <span className="text-sm text-muted">{selected.length} of {speakers.length} selected</span>
                <GradientButton size="sm">
                  <Download className="w-4 h-4" />
                  Isolate &amp; Export
                </GradientButton>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </section>
  )
}
