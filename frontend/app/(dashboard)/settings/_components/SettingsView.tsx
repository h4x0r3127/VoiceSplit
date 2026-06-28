'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Bell, HardDrive, Key, Sliders, User as UserIcon, Shield } from 'lucide-react'
import { GlassCard } from '@/components/common/GlassCard'
import { cn } from '@/lib/utils'

type Tab = 'account' | 'notifications' | 'storage' | 'export' | 'api' | 'security'

const TABS: { id: Tab; label: string; icon: typeof Bell }[] = [
  { id: 'account',       label: 'Account',       icon: UserIcon },
  { id: 'notifications', label: 'Notifications',  icon: Bell },
  { id: 'storage',       label: 'Storage',        icon: HardDrive },
  { id: 'export',        label: 'Export',         icon: Sliders },
  { id: 'api',           label: 'API Keys',       icon: Key },
  { id: 'security',      label: 'Security',       icon: Shield },
]

function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={cn(
        'relative w-11 h-6 rounded-full transition-colors duration-200 focus:outline-none',
        checked ? 'bg-brand-cyan' : 'bg-white/15',
      )}
    >
      <span
        className={cn(
          'absolute top-1 left-1 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200',
          checked && 'translate-x-5',
        )}
      />
    </button>
  )
}

function SettingRow({ label, description, children }: {
  label: string
  description?: string
  children: React.ReactNode
}) {
  return (
    <div className="flex items-center justify-between gap-4 py-4 border-b border-brand-cyan/10 last:border-0">
      <div>
        <p className="text-sm font-medium text-white">{label}</p>
        {description && <p className="text-xs text-muted mt-0.5">{description}</p>}
      </div>
      {children}
    </div>
  )
}

export function SettingsView() {
  const [activeTab, setActiveTab] = useState<Tab>('account')
  const [notifications, setNotifications] = useState({
    jobComplete: true,
    jobFailed: true,
    weeklyDigest: false,
    marketing: false,
  })
  const [exportFormat, setExportFormat] = useState('mp3')
  const [exportQuality, setExportQuality] = useState('high')

  return (
    <div className="flex gap-6 flex-col sm:flex-row">
      <nav className="sm:w-44 flex-shrink-0">
        <ul className="space-y-1">
          {TABS.map((tab) => {
            const Icon = tab.icon
            return (
              <li key={tab.id}>
                <button
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    'w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm transition-all',
                    activeTab === tab.id
                      ? 'bg-brand-cyan/10 text-brand-cyan font-medium'
                      : 'text-muted hover:text-white hover:bg-white/5',
                  )}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  {tab.label}
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="flex-1">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'account' && (
            <GlassCard hover={false}>
              <h2 className="text-base font-semibold text-white mb-4">Account details</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Display name</label>
                  <input
                    type="text"
                    placeholder="Your name"
                    className="w-full bg-white/5 border border-brand-cyan/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-muted focus:outline-none focus:border-brand-cyan/30 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Email address</label>
                  <input
                    type="email"
                    placeholder="you@example.com"
                    disabled
                    className="w-full bg-white/5 border border-brand-cyan/10 rounded-xl px-4 py-2.5 text-sm text-muted cursor-not-allowed"
                  />
                  <p className="mt-1 text-xs text-muted">Email cannot be changed</p>
                </div>
                <button className="px-5 py-2 rounded-xl bg-brand-cyan/10 border border-brand-cyan/20 text-brand-cyan text-sm font-medium hover:bg-brand-cyan/20 transition-colors">
                  Save changes
                </button>
              </div>
            </GlassCard>
          )}

          {activeTab === 'notifications' && (
            <GlassCard hover={false}>
              <h2 className="text-base font-semibold text-white mb-1">Notification preferences</h2>
              <p className="text-xs text-muted mb-4">Choose which emails you&apos;d like to receive.</p>
              <div>
                <SettingRow label="Job completed" description="When your audio processing finishes">
                  <Toggle checked={notifications.jobComplete} onChange={(v) => setNotifications((n) => ({ ...n, jobComplete: v }))} />
                </SettingRow>
                <SettingRow label="Job failed" description="When a processing job encounters an error">
                  <Toggle checked={notifications.jobFailed} onChange={(v) => setNotifications((n) => ({ ...n, jobFailed: v }))} />
                </SettingRow>
                <SettingRow label="Weekly digest" description="Summary of your activity each week">
                  <Toggle checked={notifications.weeklyDigest} onChange={(v) => setNotifications((n) => ({ ...n, weeklyDigest: v }))} />
                </SettingRow>
                <SettingRow label="Marketing emails" description="Product updates and announcements">
                  <Toggle checked={notifications.marketing} onChange={(v) => setNotifications((n) => ({ ...n, marketing: v }))} />
                </SettingRow>
              </div>
            </GlassCard>
          )}

          {activeTab === 'storage' && (
            <GlassCard hover={false}>
              <h2 className="text-base font-semibold text-white mb-4">Storage usage</h2>
              <div className="mb-6">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted">Used</span>
                  <span className="text-white">0 MB of 5 GB</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full w-0 bg-gradient-to-r from-brand-cyan to-brand-blue rounded-full" />
                </div>
              </div>
              <p className="text-xs text-muted mb-4">
                Processed audio files are stored for 30 days. Original uploads are kept for 7 days.
              </p>
              <button className="px-5 py-2 rounded-xl border border-danger/30 text-danger text-sm font-medium hover:bg-danger/10 transition-colors">
                Clear all uploads
              </button>
            </GlassCard>
          )}

          {activeTab === 'export' && (
            <GlassCard hover={false}>
              <h2 className="text-base font-semibold text-white mb-4">Default export settings</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Default format</label>
                  <div className="flex gap-2 flex-wrap">
                    {['mp3', 'wav', 'flac'].map((fmt) => (
                      <button
                        key={fmt}
                        onClick={() => setExportFormat(fmt)}
                        className={cn(
                          'px-4 py-2 rounded-xl text-sm font-mono font-medium border transition-all',
                          exportFormat === fmt
                            ? 'border-brand-cyan bg-brand-cyan/10 text-brand-cyan'
                            : 'border-brand-cyan/10 bg-white/5 text-muted hover:border-brand-cyan/30 hover:text-white',
                        )}
                      >
                        {fmt.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Quality</label>
                  <div className="flex gap-2">
                    {['low', 'medium', 'high', 'lossless'].map((q) => (
                      <button
                        key={q}
                        onClick={() => setExportQuality(q)}
                        className={cn(
                          'px-4 py-2 rounded-xl text-sm font-medium border capitalize transition-all',
                          exportQuality === q
                            ? 'border-brand-cyan bg-brand-cyan/10 text-brand-cyan'
                            : 'border-brand-cyan/10 bg-white/5 text-muted hover:border-brand-cyan/30 hover:text-white',
                        )}
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </GlassCard>
          )}

          {activeTab === 'api' && (
            <GlassCard hover={false}>
              <h2 className="text-base font-semibold text-white mb-1">API keys</h2>
              <p className="text-xs text-muted mb-4">
                Use API keys to integrate VoiceSplit into your own applications.
              </p>
              <div className="p-4 rounded-xl bg-white/5 border border-brand-cyan/10 mb-4">
                <p className="text-sm text-muted text-center">No API keys yet</p>
              </div>
              <button className="px-5 py-2 rounded-xl bg-brand-cyan/10 border border-brand-cyan/20 text-brand-cyan text-sm font-medium hover:bg-brand-cyan/20 transition-colors">
                Generate API key
              </button>
            </GlassCard>
          )}

          {activeTab === 'security' && (
            <GlassCard hover={false}>
              <h2 className="text-base font-semibold text-white mb-4">Security</h2>
              <div>
                <SettingRow label="Change password" description="Update your login password">
                  <button className="px-4 py-1.5 rounded-xl border border-brand-cyan/20 text-brand-cyan text-sm hover:bg-brand-cyan/10 transition-colors">
                    Change
                  </button>
                </SettingRow>
                <SettingRow label="Active sessions" description="Manage devices logged into your account">
                  <button className="px-4 py-1.5 rounded-xl border border-brand-cyan/20 text-brand-cyan text-sm hover:bg-brand-cyan/10 transition-colors">
                    View
                  </button>
                </SettingRow>
                <SettingRow label="Delete account" description="Permanently remove your account and all data">
                  <button className="px-4 py-1.5 rounded-xl border border-danger/30 text-danger text-sm hover:bg-danger/10 transition-colors">
                    Delete
                  </button>
                </SettingRow>
              </div>
            </GlassCard>
          )}
        </motion.div>
      </div>
    </div>
  )
}
