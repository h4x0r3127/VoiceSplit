'use client'

import { motion } from 'framer-motion'
import {
  Upload,
  Volume2,
  Mic2,
  Users,
  Fingerprint,
  GitBranch,
  Scissors,
  FileText,
  Download,
} from 'lucide-react'

const steps = [
  { icon: Upload, label: 'Upload', description: 'Drag & drop any audio file. MP3, WAV, FLAC, and more accepted.' },
  { icon: Volume2, label: 'Noise Reduction', description: 'Background noise and static are removed using spectral gating.' },
  { icon: Mic2, label: 'Voice Detection', description: 'VAD model pinpoints every region containing human speech.' },
  { icon: Users, label: 'Speaker Diarization', description: 'Deep learning identifies who is speaking at each moment.' },
  { icon: Fingerprint, label: 'Voice Embeddings', description: 'Unique voice fingerprints are created for each detected speaker.' },
  { icon: GitBranch, label: 'Clustering', description: 'Speech segments are grouped by voice similarity.' },
  { icon: Scissors, label: 'Speech Separation', description: 'BSS model isolates each speaker\'s audio stream independently.' },
  { icon: FileText, label: 'Transcription', description: 'Whisper generates a timestamped, per-speaker transcript.' },
  { icon: Download, label: 'Download', description: 'Export isolated audio and transcripts in your preferred format.' },
]

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-6 relative">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1.5 rounded-full glass border border-brand-cyan/20 text-brand-cyan text-sm font-medium mb-4">
            How It Works
          </span>
          <h2 className="text-4xl font-bold text-white mb-4">
            9-stage AI pipeline,{' '}
            <span className="gradient-text">fully automated</span>
          </h2>
          <p className="text-muted max-w-xl mx-auto text-lg">
            From raw audio to perfectly isolated voices — no configuration needed.
          </p>
        </motion.div>

        <div className="relative">
          {/* Connection line */}
          <div className="absolute left-6 md:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-brand-cyan/50 via-brand-blue/30 to-brand-purple/20 -translate-x-1/2 hidden md:block" />

          <div className="space-y-8">
            {steps.map((step, i) => {
              const isLeft = i % 2 === 0
              return (
                <motion.div
                  key={step.label}
                  initial={{ opacity: 0, x: isLeft ? -30 : 30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.08 }}
                  className={`flex items-center gap-6 md:gap-0 ${
                    isLeft ? 'md:flex-row' : 'md:flex-row-reverse'
                  }`}
                >
                  {/* Content */}
                  <div className={`flex-1 ${isLeft ? 'md:text-right md:pr-12' : 'md:text-left md:pl-12'}`}>
                    <div
                      className={`glass rounded-xl p-5 glass-hover ${
                        isLeft ? 'md:ml-auto' : ''
                      } max-w-sm`}
                    >
                      <h3 className="font-semibold text-white mb-1">{step.label}</h3>
                      <p className="text-sm text-muted leading-relaxed">{step.description}</p>
                    </div>
                  </div>

                  {/* Step number with icon */}
                  <div className="relative z-10 flex-shrink-0">
                    <div className="w-12 h-12 rounded-full flex items-center justify-center bg-gradient-to-br from-brand-cyan to-brand-purple shadow-glow">
                      <step.icon className="w-5 h-5 text-white" />
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-[#0B1120] border border-brand-cyan/30 flex items-center justify-center text-[10px] font-bold text-brand-cyan">
                      {i + 1}
                    </div>
                  </div>

                  {/* Spacer for other side */}
                  <div className="hidden md:block flex-1" />
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
