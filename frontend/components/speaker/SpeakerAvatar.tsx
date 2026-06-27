import { cn } from '@/lib/utils'

interface SpeakerAvatarProps {
  label: string
  color: string
  size?: 'sm' | 'md' | 'lg'
  selected?: boolean
  index: number
}

const sizeMap = {
  sm: { outer: 'w-8 h-8', text: 'text-xs' },
  md: { outer: 'w-12 h-12', text: 'text-sm' },
  lg: { outer: 'w-16 h-16', text: 'text-base' },
}

export function SpeakerAvatar({ label, color, size = 'md', selected, index }: SpeakerAvatarProps) {
  const initials = `S${index + 1}`

  return (
    <div className="relative flex-shrink-0">
      {selected && (
        <div
          className="absolute -inset-1 rounded-full animate-pulse"
          style={{ background: `${color}30`, boxShadow: `0 0 16px ${color}60` }}
        />
      )}
      <div
        className={cn(
          sizeMap[size].outer,
          'rounded-full flex items-center justify-center font-bold text-white relative z-10',
        )}
        style={{
          background: `radial-gradient(circle at 35% 35%, ${color}dd, ${color}66)`,
          boxShadow: selected ? `0 0 20px ${color}50` : `0 2px 8px ${color}30`,
        }}
      >
        <span className={sizeMap[size].text}>{initials}</span>
      </div>
    </div>
  )
}
