import type { Metadata } from 'next'
import { UploadInterface } from './_components/UploadInterface'

export const metadata: Metadata = { title: 'Upload Audio' }

export default function UploadPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Upload audio</h1>
        <p className="text-muted">
          Upload a recording with multiple speakers. Our AI will detect and isolate each voice.
        </p>
      </div>
      <UploadInterface />
    </div>
  )
}
