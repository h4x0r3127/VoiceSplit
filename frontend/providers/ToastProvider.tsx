'use client'

import { Toaster } from 'sonner'

export function ToastProvider() {
  return (
    <Toaster
      theme="dark"
      position="bottom-right"
      toastOptions={{
        style: {
          background: '#111827',
          border: '1px solid rgba(6, 214, 207, 0.15)',
          color: '#F8FAFC',
        },
        classNames: {
          success: 'border-l-4 border-l-[#22C55E]',
          error: 'border-l-4 border-l-[#EF4444]',
          warning: 'border-l-4 border-l-[#F59E0B]',
          info: 'border-l-4 border-l-[#06D6CF]',
        },
      }}
    />
  )
}
