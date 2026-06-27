import Image from 'next/image'
import Link from 'next/link'
import { cn } from '@/lib/utils'

interface LogoProps {
  size?: number
  showText?: boolean
  className?: string
  href?: string
}

export function Logo({ size = 40, showText = true, className, href = '/' }: LogoProps) {
  const content = (
    <div className={cn('flex items-center gap-3', className)}>
      <div className="relative flex-shrink-0">
        <Image
          src="/logo.png"
          alt="VoiceSplit"
          width={size}
          height={size}
          priority
          className="rounded-lg"
        />
      </div>
      {showText && (
        <span
          className="font-bold gradient-text tracking-tight"
          style={{ fontSize: size * 0.5 }}
        >
          VoiceSplit
        </span>
      )}
    </div>
  )

  if (href) {
    return (
      <Link href={href} className="inline-flex items-center hover:opacity-90 transition-opacity">
        {content}
      </Link>
    )
  }

  return content
}
