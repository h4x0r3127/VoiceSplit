'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Logo } from '@/components/brand/Logo'
import { GradientButton } from '@/components/common/GradientButton'

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background px-4">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <Link href="/" className="inline-flex justify-center mb-12">
          <Logo size={48} />
        </Link>

        <div className="relative mb-6">
          <span className="text-[160px] font-bold leading-none gradient-text select-none opacity-20">
            404
          </span>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex items-end gap-1.5 h-20">
              {Array.from({ length: 28 }).map((_, i) => (
                <motion.div
                  key={i}
                  className="w-1.5 rounded-full bg-gradient-to-t from-brand-purple via-brand-blue to-brand-cyan"
                  animate={{ scaleY: [0.2, 1, 0.2] }}
                  transition={{
                    duration: 1.4 + Math.random() * 0.6,
                    repeat: Infinity,
                    delay: i * 0.06,
                    ease: 'easeInOut',
                  }}
                  style={{ height: `${16 + Math.random() * 48}px` }}
                />
              ))}
            </div>
          </div>
        </div>

        <h1 className="text-2xl font-bold text-white mb-3">Page not found</h1>
        <p className="text-muted mb-8 max-w-sm mx-auto">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>

        <div className="flex items-center justify-center gap-4">
          <Link href="/dashboard">
            <GradientButton size="md">Back to Dashboard</GradientButton>
          </Link>
          <Link href="/">
            <GradientButton size="md" variant="outline">Go Home</GradientButton>
          </Link>
        </div>
      </motion.div>
    </div>
  )
}
