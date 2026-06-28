import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { QueryProvider } from '@/providers/QueryProvider'
import { AuthProvider } from '@/providers/AuthProvider'
import { ToastProvider } from '@/providers/ToastProvider'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: 'VoiceSplit — Choose the voice that matters',
    template: '%s | VoiceSplit',
  },
  description:
    'AI-powered speaker isolation. Upload any multi-speaker recording and isolate individual voices while preserving every nuance, pause, and emotion.',
  keywords: ['speaker isolation', 'voice separation', 'audio AI', 'diarization', 'voice extraction'],
  authors: [{ name: 'VoiceSplit' }],
  creator: 'VoiceSplit',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://voicesplit.app',
    siteName: 'VoiceSplit',
    title: 'VoiceSplit — Choose the voice that matters',
    description: 'AI-powered speaker isolation platform. Detect, separate, and preserve individual voices from any recording.',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'VoiceSplit' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VoiceSplit — Choose the voice that matters',
    description: 'AI-powered speaker isolation platform.',
    images: ['/og-image.png'],
  },
  icons: {
    icon: '/logo.png',
    apple: '/logo.png',
  },
  manifest: '/manifest.json',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} dark`} suppressHydrationWarning>
      <body className="bg-background text-foreground antialiased">
        <AuthProvider>
          <QueryProvider>
            {children}
            <ToastProvider />
          </QueryProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
