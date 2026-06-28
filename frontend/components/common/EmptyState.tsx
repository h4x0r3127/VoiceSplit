import Link from 'next/link'
import Image from 'next/image'
import { GradientButton } from './GradientButton'

interface ActionProp {
  label: string
  href?: string
  onClick?: () => void
}

interface EmptyStateProps {
  title: string
  description: string
  icon?: React.ReactNode
  action?: ActionProp
  ctaLabel?: string
  ctaHref?: string
  onCtaClick?: () => void
}

export function EmptyState({
  title,
  description,
  icon,
  action,
  ctaLabel,
  ctaHref,
  onCtaClick,
}: EmptyStateProps) {
  const label = action?.label ?? ctaLabel
  const href  = action?.href  ?? ctaHref
  const click = action?.onClick ?? onCtaClick

  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 text-center">
      <div className="mb-6">
        {icon ?? (
          <Image
            src="/logo.png"
            alt="VoiceSplit"
            width={64}
            height={64}
            className="rounded-xl opacity-30"
          />
        )}
      </div>

      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-muted text-sm max-w-sm mb-8">{description}</p>

      {label && (
        href ? (
          <Link href={href}>
            <GradientButton>{label}</GradientButton>
          </Link>
        ) : (
          <GradientButton onClick={click}>{label}</GradientButton>
        )
      )}
    </div>
  )
}
