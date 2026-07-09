import type { Metadata } from 'next'

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
      <h1 className="text-3xl font-bold text-white">
        Results Page
      </h1>

      <p className="text-muted mt-2">
        Job ID: {jobId}
      </p>
    </div>
  )
}