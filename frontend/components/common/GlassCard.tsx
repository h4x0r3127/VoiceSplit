import { cn } from '@/lib/utils'

interface GlassCardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  glow?: boolean
  padding?: boolean
  onClick?: () => void
}

export function GlassCard({
  children,
  className,
  hover = true,
  glow = false,
  padding = true,
  onClick,
}: GlassCardProps) {
  return (
    <div
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
      className={cn(
        'glass rounded-2xl transition-all duration-300',
        padding && 'p-6',
        hover && 'glass-hover',
        glow && 'shadow-[0_0_30px_rgba(6,214,207,0.15)]',
        onClick && 'cursor-pointer',
        className,
      )}
    >
      {children}
    </div>
  )
}
