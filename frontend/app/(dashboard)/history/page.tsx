import type { Metadata } from 'next'
import { HistoryView } from './_components/HistoryView'

export const metadata: Metadata = { title: 'History' }

export default function HistoryPage() {
  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">History</h1>
        <p className="text-muted">All your audio uploads and processing jobs.</p>
      </div>
      <HistoryView />
    </div>
  )
}
