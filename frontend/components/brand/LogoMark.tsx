import Image from 'next/image'
import Link from 'next/link'
import { cn } from '@/lib/utils'

interface LogoMarkProps {
  size?: number
  className?: string
  href?: string
}

export function LogoMark({ size = 32, className, href = '/' }: LogoMarkProps) {
  const content = (
    <div className={cn('relative flex-shrink-0', className)}>
      <Image
        src="/logo.png"
        alt="VoiceSplit"
        width={size}
        height={size}
        priority
        className="rounded-lg"
      />
    </div>
  )

  if (href) {
    return (
      <Link href={href} className="inline-flex hover:opacity-90 transition-opacity">
        {content}
      </Link>
    )
  }

  return content
}
