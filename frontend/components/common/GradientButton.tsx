'use client'

import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface GradientButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  size?: 'sm' | 'md' | 'lg'
  variant?: 'gradient' | 'outline' | 'ghost'
  loading?: boolean
}

const sizeClasses = {
  sm: 'px-4 py-2 text-sm h-9',
  md: 'px-6 py-3 text-base h-11',
  lg: 'px-8 py-4 text-lg h-14',
}

const variantClasses = {
  gradient:
    'bg-gradient-to-r from-brand-cyan via-brand-blue to-brand-purple text-white hover:shadow-[0_0_25px_rgba(6,214,207,0.4)] hover:scale-[1.02] active:scale-[0.98]',
  outline:
    'border border-brand-cyan/40 text-brand-cyan hover:border-brand-cyan hover:bg-brand-cyan/10 bg-transparent',
  ghost:
    'text-slate-400 hover:text-white hover:bg-white/5 bg-transparent',
}

export const GradientButton = forwardRef<HTMLButtonElement, GradientButtonProps>(
  (
    {
      className,
      size = 'md',
      variant = 'gradient',
      loading = false,
      children,
      disabled,
      ...props
    },
    ref,
  ) => {
    const isDisabled = disabled || loading

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={cn(
          'relative font-semibold rounded-xl transition-all duration-200 flex items-center gap-2 justify-center whitespace-nowrap',
          sizeClasses[size],
          variantClasses[variant],
          isDisabled && 'opacity-50 cursor-not-allowed !scale-100 !shadow-none',
          className,
        )}
        {...props}
      >
        {loading && <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" />}
        {children}
      </button>
    )
  },
)

GradientButton.displayName = 'GradientButton'
