import type { Metadata } from 'next'
import Link from 'next/link'
import { Logo } from '@/components/brand/Logo'

export const metadata: Metadata = {
  title: {
    template: '%s | VoiceSplit',
    default: 'VoiceSplit',
  },
}

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background px-4 py-12">
      <div
        className="pointer-events-none fixed inset-0 overflow-hidden"
        aria-hidden="true"
      >
        <div className="absolute top-1/4 -left-64 w-[600px] h-[600px] rounded-full bg-brand-cyan/5 blur-[120px]" />
        <div className="absolute bottom-1/4 -right-64 w-[500px] h-[500px] rounded-full bg-brand-purple/5 blur-[120px]" />
      </div>

      <div className="relative w-full max-w-md">
        <div className="flex justify-center mb-10">
          <Logo size={44} href="/" />
        </div>
        {children}
      </div>

      <p className="mt-8 text-xs text-muted">
        © {new Date().getFullYear()} VoiceSplit. All rights reserved.
      </p>
    </div>
  )
}
