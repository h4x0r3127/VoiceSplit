import type { Metadata } from 'next'
import { DashboardOverview } from './_components/DashboardOverview'

export const metadata: Metadata = { title: 'Dashboard' }

export default function DashboardPage() {
  return <DashboardOverview />
}
