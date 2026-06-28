'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react'
import { GradientButton } from '@/components/common/GradientButton'
import { GlassCard } from '@/components/common/GlassCard'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
})

type Fields = z.infer<typeof schema>

export default function ForgotPasswordPage() {
  const [submitted, setSubmitted] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Fields>({ resolver: zodResolver(schema) })

  async function onSubmit(data: Fields) {
    setServerError(null)
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: data.email }),
      })
      setSubmitted(true)
    } catch {
      setServerError('Something went wrong. Please try again.')
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <GlassCard hover={false} className="p-8">
        <AnimatePresence mode="wait">
          {submitted ? (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-4"
            >
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 rounded-full bg-success/15 flex items-center justify-center">
                  <CheckCircle className="w-8 h-8 text-success" />
                </div>
              </div>
              <h1 className="text-xl font-bold text-white mb-2">Check your email</h1>
              <p className="text-muted text-sm mb-6">
                If that address is registered, we&apos;ve sent a password reset link. Check your inbox and spam folder.
              </p>
              <Link href="/login">
                <GradientButton variant="outline" size="sm" className="mx-auto">
                  Back to sign in
                </GradientButton>
              </Link>
            </motion.div>
          ) : (
            <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="mb-8">
                <Link
                  href="/login"
                  className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-white transition-colors mb-6"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back to sign in
                </Link>
                <h1 className="text-2xl font-bold text-white mb-1">Reset your password</h1>
                <p className="text-muted text-sm">
                  Enter your email and we&apos;ll send you a reset link.
                </p>
              </div>

              {serverError && (
                <div className="mb-5 p-3 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm">
                  {serverError}
                </div>
              )}

              <form onSubmit={handleSubmit(onSubmit)} noValidate>
                <div className="mb-5">
                  <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-1.5">
                    Email address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted pointer-events-none" />
                    <input
                      id="email"
                      type="email"
                      autoComplete="email"
                      placeholder="you@example.com"
                      {...register('email')}
                      className="w-full bg-white/5 border border-brand-cyan/10 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white placeholder:text-muted focus:outline-none focus:border-brand-cyan/40 transition-all"
                    />
                  </div>
                  {errors.email && (
                    <p className="mt-1 text-xs text-danger">{errors.email.message}</p>
                  )}
                </div>

                <GradientButton type="submit" size="md" loading={isSubmitting} className="w-full">
                  Send reset link
                </GradientButton>
              </form>
            </motion.div>
          )}
        </AnimatePresence>
      </GlassCard>
    </motion.div>
  )
}
