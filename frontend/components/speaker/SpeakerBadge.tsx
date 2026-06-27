import { cn } from '@/lib/utils'

interface SpeakerBadgeProps {
  label: string
  color: string
  size?: 'xs' | 'sm'
  className?: string
}

export function SpeakerBadge({ label, color, size = 'sm', className }: SpeakerBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-medium',
        size === 'xs' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-xs',
        className,
      )}
      style={{
        background: `${color}18`,
        color: color,
        border: `1px solid ${color}40`,
      }}
    >
      <span
        className="inline-block rounded-full flex-shrink-0"
        style={{ width: 6, height: 6, background: color }}
      />
      {label}
    </span>
  )
}
