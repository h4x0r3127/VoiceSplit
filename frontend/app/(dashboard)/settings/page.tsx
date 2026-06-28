import type { Metadata } from 'next'
import { SettingsView } from './_components/SettingsView'

export const metadata: Metadata = { title: 'Settings' }

export default function SettingsPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Settings</h1>
        <p className="text-muted">Manage your account and application preferences.</p>
      </div>
      <SettingsView />
    </div>
  )
}
