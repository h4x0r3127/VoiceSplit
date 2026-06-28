import type { Metadata } from 'next'
import { ProfileView } from './_components/ProfileView'

export const metadata: Metadata = { title: 'Profile' }

export default function ProfilePage() {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Profile</h1>
        <p className="text-muted">Your account information and usage stats.</p>
      </div>
      <ProfileView />
    </div>
  )
}
