'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Eye, EyeOff, Mail, Lock, User, Chrome } from 'lucide-react'
import { GradientButton } from '@/components/common/GradientButton'
import { GlassCard } from '@/components/common/GlassCard'

const registerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters').max(80, 'Name too long'),
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
  terms: z.boolean().refine((v) => v, 'You must accept the terms to continue'),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
})

type RegisterFields = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const router = useRouter()
  const [showPassword, setShowPassword] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)
  const [googleLoading, setGoogleLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFields>({ resolver: zodResolver(registerSchema) })

  async function onSubmit(data: RegisterFields) {
    setServerError(null)
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: data.name, email: data.email, password: data.password }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Registration failed' }))
        setServerError(err.detail || 'Registration failed. Please try again.')
        return
      }
      await signIn('credentials', {
        email: data.email,
        password: data.password,
        redirect: false,
      })
      router.push('/dashboard')
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
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-white mb-1">Create your account</h1>
          <p className="text-muted text-sm">Start isolating voices in minutes</p>
        </div>

        {serverError && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mb-5 p-3 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm"
          >
            {serverError}
          </motion.div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-slate-300 mb-1.5">
              Full name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted pointer-events-none" />
              <input
                id="name"
                type="text"
                autoComplete="name"
                placeholder="Jane Smith"
                {...register('name')}
                className="w-full bg-white/5 border border-brand-cyan/10 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white placeholder:text-muted focus:outline-none focus:border-brand-cyan/40 focus:bg-white/8 transition-all"
              />
            </div>
            {errors.name && <p className="mt-1 text-xs text-danger">{errors.name.message}</p>}
          </div>

          <div>
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
                className="w-full bg-white/5 border border-brand-cyan/10 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white placeholder:text-muted focus:outline-none focus:border-brand-cyan/40 focus:bg-white/8 transition-all"
              />
            </div>
            {errors.email && <p className="mt-1 text-xs text-danger">{errors.email.message}</p>}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted pointer-events-none" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                placeholder="Min. 8 characters"
                {...register('password')}
                className="w-full bg-white/5 border border-brand-cyan/10 rounded-xl pl-9 pr-10 py-2.5 text-sm text-white placeholder:text-muted focus:outline-none focus:border-brand-cyan/40 focus:bg-white/8 transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-white transition-colors"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.password && <p className="mt-1 text-xs text-danger">{errors.password.message}</p>}
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-300 mb-1.5">
              Confirm password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted pointer-events-none" />
              <input
                id="confirmPassword"
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                placeholder="••••••••"
                {...register('confirmPassword')}
                className="w-full bg-white/5 border border-brand-cyan/10 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white placeholder:text-muted focus:outline-none focus:border-brand-cyan/40 focus:bg-white/8 transition-all"
              />
            </div>
            {errors.confirmPassword && (
              <p className="mt-1 text-xs text-danger">{errors.confirmPassword.message}</p>
            )}
          </div>

          <div className="flex items-start gap-3 pt-1">
            <input
              id="terms"
              type="checkbox"
              {...register('terms')}
              className="mt-0.5 w-4 h-4 rounded border-brand-cyan/20 bg-white/5 accent-brand-cyan"
            />
            <label htmlFor="terms" className="text-sm text-muted leading-relaxed">
              I agree to the{' '}
              <Link href="/terms" className="text-brand-cyan hover:underline">Terms of Service</Link>
              {' '}and{' '}
              <Link href="/privacy" className="text-brand-cyan hover:underline">Privacy Policy</Link>
            </label>
          </div>
          {errors.terms && <p className="text-xs text-danger">{errors.terms.message}</p>}

          <GradientButton
            type="submit"
            size="md"
            loading={isSubmitting}
            className="w-full mt-2"
          >
            Create account
          </GradientButton>
        </form>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-brand-cyan/10" />
          </div>
          <div className="relative flex justify-center">
            <span className="px-3 bg-card text-xs text-muted">or continue with</span>
          </div>
        </div>

        <button
          onClick={() => { setGoogleLoading(true); signIn('google', { callbackUrl: '/dashboard' }) }}
          disabled={googleLoading}
          className="w-full flex items-center justify-center gap-3 py-2.5 px-4 rounded-xl border border-brand-cyan/10 bg-white/5 text-sm font-medium text-white hover:border-brand-cyan/30 hover:bg-white/8 transition-all disabled:opacity-50"
        >
          <Chrome className="w-4 h-4" />
          {googleLoading ? 'Redirecting...' : 'Continue with Google'}
        </button>

        <p className="mt-6 text-center text-sm text-muted">
          Already have an account?{' '}
          <Link href="/login" className="text-brand-cyan hover:text-brand-blue font-medium transition-colors">
            Sign in
          </Link>
        </p>
      </GlassCard>
    </motion.div>
  )
}
