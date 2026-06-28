import type { Metadata } from 'next'
import { ProcessingStatusView } from './_components/ProcessingStatusView'

interface ProcessingPageProps {
  params: Promise<{ jobId: string }>
}

export async function generateMetadata({ params }: ProcessingPageProps): Promise<Metadata> {
  const { jobId } = await params
  return {
    title: `Processing — ${jobId.slice(0, 8)}`,
  }
}

export default async function ProcessingPage({ params }: ProcessingPageProps) {
  const { jobId } = await params
  return (
    <div className="max-w-3xl mx-auto">
      <ProcessingStatusView jobId={jobId} />
    </div>
  )
}
