import Image from 'next/image'
import Link from 'next/link'
import { GradientButton } from './GradientButton'

interface EmptyStateProps {
  title: string
  description: string
  ctaLabel?: string
  ctaHref?: string
  onCtaClick?: () => void
  icon?: React.ReactNode
}

export function EmptyState({
  title,
  description,
  ctaLabel,
  ctaHref,
  onCtaClick,
  icon,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 text-center">
      <div className="mb-6 opacity-60">
        {icon ?? (
          <Image
            src="/logo.png"
            alt="VoiceSplit"
            width={64}
            height={64}
            className="rounded-xl opacity-40"
          />
        )}
      </div>

      <h3 className="text-xl font-semibold text-foreground mb-2">{title}</h3>
      <p className="text-muted text-sm max-w-sm mb-8">{description}</p>

      {ctaLabel && (
        <>
          {ctaHref ? (
            <Link href={ctaHref}>
              <GradientButton>{ctaLabel}</GradientButton>
            </Link>
          ) : (
            <GradientButton onClick={onCtaClick}>{ctaLabel}</GradientButton>
          )}
        </>
      )}
    </div>
  )
}
