'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSession } from 'next-auth/react'
import { getJob, getJobs, deleteJob, processJob, getTranscript } from '@/services/jobs.service'
import type { JobStatus } from '@/types/job'

const TERMINAL_STATES: JobStatus[] = ['COMPLETED', 'FAILED']

export function useJob(id: string) {
  const { data: session } = useSession()
  const token = session?.accessToken ?? ''

  return useQuery({
    queryKey: ['job', id],
    queryFn: () => getJob(token, id),
    enabled: !!token && !!id,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      if (!status || TERMINAL_STATES.includes(status)) return false
      return 3000
    },
  })
}

export function useJobs(page = 1, status?: string) {
  const { data: session } = useSession()
  const token = session?.accessToken ?? ''

  return useQuery({
    queryKey: ['jobs', page, status],
    queryFn: () => getJobs(token, page, status),
    enabled: !!token,
  })
}

export function useDeleteJob() {
  const { data: session } = useSession()
  const queryClient = useQueryClient()
  const token = session?.accessToken ?? ''

  return useMutation({
    mutationFn: (id: string) => deleteJob(token, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
}

export function useProcessJob() {
  const { data: session } = useSession()
  const queryClient = useQueryClient()
  const token = session?.accessToken ?? ''

  return useMutation({
    mutationFn: ({ id, speakerIds }: { id: string; speakerIds: string[] }) =>
      processJob(token, id, speakerIds),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['job', variables.id] })
    },
  })
}

export function useTranscript(jobId: string) {
  const { data: session } = useSession()
  const token = session?.accessToken ?? ''

  return useQuery({
    queryKey: ['transcript', jobId],
    queryFn: () => getTranscript(token, jobId),
    enabled: !!token && !!jobId,
  })
}
