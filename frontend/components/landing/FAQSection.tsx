'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

const faqs = [
  {
    q: 'How does VoiceSplit work?',
    a: 'VoiceSplit uses a 9-stage AI pipeline: it first removes background noise, then detects voice activity, performs speaker diarization to identify who speaks when, creates unique voice embeddings, clusters segments by speaker identity, separates each audio stream independently using blind source separation, generates a timestamped transcript, and finally packages everything for download.',
  },
  {
    q: 'Will it modify the selected speaker\'s voice?',
    a: 'No. VoiceSplit preserves the original voice 100% — including every nuance, breath, pause, and emotional inflection. We only remove the unwanted speakers, we never synthesize or modify the target voice.',
  },
  {
    q: 'What audio formats are supported?',
    a: 'We accept MP3, WAV, AAC, M4A, FLAC, OGG, and OPUS as input. You can export your isolated audio as MP3, WAV, or FLAC, and transcripts as TXT, JSON, or CSV.',
  },
  {
    q: 'How long does processing take?',
    a: 'Processing time depends on file length and number of speakers. Typically, a 30-minute file completes in 3-5 minutes on Pro, or 8-12 minutes on Free. We use GPU-accelerated inference to minimize wait times.',
  },
  {
    q: 'Is my audio stored securely?',
    a: 'Yes. All files are encrypted in transit (TLS 1.3) and at rest (AES-256). We store your files on our servers only for as long as necessary. Free users have files deleted after 7 days; Pro users can configure retention up to 90 days.',
  },
  {
    q: 'Can I process phone call recordings?',
    a: 'Absolutely. Phone recordings are one of the most common use cases. VoiceSplit handles compressed, low-bitrate audio well and works even with significant codec artifacts.',
  },
  {
    q: 'What is the maximum file size?',
    a: 'Free users can upload files up to 100MB. Pro users can upload up to 2GB per file. For Enterprise, limits are custom. File duration limits are 5 minutes (Free) and 2 hours (Pro) per job.',
  },
  {
    q: 'Do you offer an API?',
    a: 'Yes! Pro and Enterprise plans include full REST API access. You can integrate VoiceSplit into your own workflows, automate batch processing, and receive webhook notifications when jobs complete.',
  },
]

export function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  return (
    <section id="faq" className="py-24 px-6">
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1.5 rounded-full glass border border-brand-cyan/20 text-brand-cyan text-sm font-medium mb-4">
            FAQ
          </span>
          <h2 className="text-4xl font-bold text-white mb-4">
            Frequently asked <span className="gradient-text">questions</span>
          </h2>
        </motion.div>

        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.06 }}
            >
              <div className={cn('glass rounded-xl overflow-hidden transition-all duration-200', openIndex === i && 'border-brand-cyan/20')}>
                <button
                  onClick={() => setOpenIndex(openIndex === i ? null : i)}
                  className="w-full flex items-center justify-between px-6 py-4 text-left group"
                >
                  <span className={cn('font-medium text-sm sm:text-base transition-colors', openIndex === i ? 'text-brand-cyan' : 'text-white group-hover:text-brand-cyan')}>
                    {faq.q}
                  </span>
                  <ChevronDown
                    className={cn('w-5 h-5 text-muted flex-shrink-0 ml-4 transition-transform duration-200', openIndex === i && 'rotate-180 text-brand-cyan')}
                  />
                </button>

                <AnimatePresence initial={false}>
                  {openIndex === i && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="px-6 pb-5">
                        <div className="h-px bg-brand-cyan/10 mb-4" />
                        <p className="text-sm text-muted leading-relaxed">{faq.a}</p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
