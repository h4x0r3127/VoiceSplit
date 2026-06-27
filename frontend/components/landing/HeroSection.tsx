'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Play, ArrowDown } from 'lucide-react'
import { GradientButton } from '@/components/common/GradientButton'

const WAVEFORM_BARS = Array.from({ length: 48 }, (_, i) => ({
  height: 20 + Math.random() * 60,
  duration: 1.0 + Math.random() * 0.8,
  delay: i * 0.04,
}))

const MOCK_SPEAKERS = [
  { label: 'Speaker 1', color: '#06D6CF', width: '45%', bars: 12 },
  { label: 'Speaker 2', color: '#3B82F6', width: '30%', bars: 8 },
  { label: 'Speaker 3', color: '#7C3AED', width: '25%', bars: 6 },
]

export function HeroSection() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden">
      {/* Background waveform */}
      <div className="absolute bottom-0 left-0 right-0 flex items-end justify-center gap-[3px] h-48 opacity-20 pointer-events-none">
        {WAVEFORM_BARS.map((bar, i) => (
          <motion.div
            key={i}
            className="w-1.5 rounded-full"
            style={{
              height: bar.height,
              background: 'linear-gradient(to top, #7C3AED, #3B82F6, #06D6CF)',
            }}
            animate={{ scaleY: [0.3, 1, 0.3] }}
            transition={{
              duration: bar.duration,
              repeat: Infinity,
              delay: bar.delay,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass border border-brand-cyan/20 text-brand-cyan text-sm font-medium mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-cyan animate-pulse" />
            AI-Powered Speaker Isolation
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white leading-[1.1] mb-6"
        >
          Choose the voice
          <br />
          <span className="gradient-text">that matters.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-lg sm:text-xl text-muted max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          Upload any multi-speaker recording. Our AI automatically detects, separates, and
          isolates each voice — preserving every nuance, breath, and emotion.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
        >
          <Link href="/register">
            <GradientButton size="lg">Start For Free</GradientButton>
          </Link>
          <Link href="/#how-it-works">
            <GradientButton size="lg" variant="outline">
              <Play className="w-5 h-5" />
              See How It Works
            </GradientButton>
          </Link>
        </motion.div>

        {/* Mock UI */}
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.4 }}
          className="glass rounded-2xl p-6 border border-brand-cyan/15 max-w-3xl mx-auto shadow-[0_0_60px_rgba(6,214,207,0.1)]"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="flex gap-1.5">
              {['bg-danger/60', 'bg-warning/60', 'bg-success/60'].map((c, i) => (
                <div key={i} className={`w-3 h-3 rounded-full ${c}`} />
              ))}
            </div>
            <span className="text-xs text-muted font-mono">podcast_episode_42.mp3</span>
          </div>

          {/* Waveform mockup */}
          <div className="h-14 bg-white/5 rounded-xl flex items-end gap-[2px] px-3 pb-2 mb-4 overflow-hidden">
            {Array.from({ length: 80 }).map((_, i) => (
              <div
                key={i}
                className="flex-1 rounded-sm bg-brand-cyan/40"
                style={{ height: `${20 + Math.sin(i * 0.4) * 40 + Math.random() * 20}%` }}
              />
            ))}
          </div>

          {/* Speaker lanes */}
          <div className="space-y-2">
            {MOCK_SPEAKERS.map((s, idx) => (
              <div key={idx} className="flex items-center gap-3">
                <span className="text-xs text-muted w-20 text-right">{s.label}</span>
                <div className="flex-1 h-8 bg-white/5 rounded-lg overflow-hidden relative">
                  <motion.div
                    className="absolute top-1 bottom-1 left-0 rounded-md flex items-center gap-0.5 px-1 overflow-hidden"
                    style={{ width: s.width, background: `${s.color}30`, borderLeft: `2px solid ${s.color}` }}
                    initial={{ width: 0 }}
                    animate={{ width: s.width }}
                    transition={{ duration: 0.8, delay: 0.6 + idx * 0.15 }}
                  >
                    {Array.from({ length: s.bars }).map((_, j) => (
                      <div
                        key={j}
                        className="w-0.5 rounded-full flex-shrink-0"
                        style={{ height: `${40 + Math.random() * 50}%`, background: s.color }}
                      />
                    ))}
                  </motion.div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 1.5, repeat: Infinity }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-muted"
      >
        <span className="text-xs">Scroll to explore</span>
        <ArrowDown className="w-4 h-4" />
      </motion.div>
    </section>
  )
}
