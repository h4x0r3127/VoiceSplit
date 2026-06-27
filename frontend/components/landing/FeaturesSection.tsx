'use client'

import { motion } from 'framer-motion'
import {
  Mic2,
  AudioWaveform,
  Sparkles,
  Download,
  FileText,
  BarChart3,
} from 'lucide-react'
import { GlassCard } from '@/components/common/GlassCard'

const features = [
  {
    icon: Mic2,
    title: 'Speaker Detection',
    description:
      'AI automatically finds and identifies every distinct voice in your recording within seconds.',
  },
  {
    icon: AudioWaveform,
    title: 'Perfect Isolation',
    description:
      'Remove unwanted speakers with surgical precision. Keep only the voices that matter.',
  },
  {
    icon: Sparkles,
    title: 'Voice Preservation',
    description:
      'Every nuance, pause, and breath kept intact. No artifacts, no quality loss.',
  },
  {
    icon: Download,
    title: 'Multi-Format Export',
    description:
      'Export as MP3, WAV, FLAC or download a full transcript in TXT, JSON, or CSV.',
  },
  {
    icon: FileText,
    title: 'Real-Time Transcript',
    description:
      'Timestamped, speaker-labeled transcript generated automatically. Searchable and downloadable.',
  },
  {
    icon: BarChart3,
    title: 'Analytics Dashboard',
    description:
      'Visual speaking time breakdown, confidence scores, and per-speaker insights.',
  },
]

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
}

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
}

export function FeaturesSection() {
  return (
    <section id="features" className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1.5 rounded-full glass border border-brand-cyan/20 text-brand-cyan text-sm font-medium mb-4">
            Features
          </span>
          <h2 className="text-4xl font-bold text-white mb-4">
            Everything you need to{' '}
            <span className="gradient-text">isolate any voice</span>
          </h2>
          <p className="text-muted max-w-xl mx-auto text-lg">
            Professional-grade audio separation powered by cutting-edge deep learning models.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature) => (
            <motion.div key={feature.title} variants={cardVariants}>
              <GlassCard className="h-full group hover:-translate-y-1 hover:shadow-glow transition-all duration-300">
                <div className="w-12 h-12 rounded-xl bg-brand-cyan/10 flex items-center justify-center mb-5 group-hover:bg-brand-cyan/20 transition-colors">
                  <feature.icon className="w-6 h-6 text-brand-cyan" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-muted text-sm leading-relaxed">{feature.description}</p>
              </GlassCard>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
