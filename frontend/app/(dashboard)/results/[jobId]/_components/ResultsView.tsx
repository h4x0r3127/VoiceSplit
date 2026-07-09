'use client'

import { useSession } from 'next-auth/react'
import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'

interface ResultsViewProps {
  jobId: string
}

export function ResultsView({ jobId }: ResultsViewProps) {
  const { data: session } = useSession()
  const token = session?.accessToken

  const {
    data: job,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['job', jobId],
    enabled: !!token,
    queryFn: async () => {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/${jobId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('Failed to load job')
      }

      return response.json()
    },
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-brand-cyan" />
      </div>
    )
  }

  if (isError || !job) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-semibold text-red-400">
          Failed to load results.
        </h2>
      </div>
    )
  }

  return (
    <div className="space-y-6">

      <div className="glass rounded-2xl p-6">

        <h2 className="text-2xl font-bold text-white mb-6">
          Audio Details
        </h2>

        <div className="grid md:grid-cols-2 gap-4">

          <div>
            <p className="text-muted">Filename</p>
            <p className="text-white">{job.original_filename}</p>
          </div>

          <div>
            <p className="text-muted">Status</p>
            <p className="text-white">{job.status}</p>
          </div>

          <div>
            <p className="text-muted">Duration</p>
            <p className="text-white">
              {job.duration_seconds ?? 'Unknown'}
            </p>
          </div>

          <div>
            <p className="text-muted">Progress</p>
            <p className="text-white">
              {job.progress}%
            </p>
          </div>

        </div>

      </div>

    </div>
  )
}