import type { Metadata } from 'next'
import { ResultsView } from './_components/ResultsView'

interface ResultsPageProps {
  params: Promise<{ jobId: string }>
}

export async function generateMetadata({
  params,
}: ResultsPageProps): Promise<Metadata> {
  const { jobId } = await params

  return {
    title: `Results — ${jobId.slice(0, 8)}`,
  }
}

export default async function ResultsPage({
  params,
}: ResultsPageProps) {
  const { jobId } = await params

  return (
    <div className="max-w-6xl mx-auto">
      <ResultsView jobId={jobId} />
    </div>
  )
}