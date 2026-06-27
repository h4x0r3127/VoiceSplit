import Link from 'next/link'
import { Twitter, Github, MessageCircle } from 'lucide-react'
import { Logo } from '@/components/brand/Logo'

const footerLinks = {
  Product: [
    { label: 'Features', href: '/#features' },
    { label: 'Pricing', href: '/#pricing' },
    { label: 'Changelog', href: '/changelog' },
    { label: 'Docs', href: '/docs' },
  ],
  Company: [
    { label: 'About', href: '/about' },
    { label: 'Blog', href: '/blog' },
    { label: 'Careers', href: '/careers' },
    { label: 'Contact', href: '/contact' },
  ],
  Legal: [
    { label: 'Privacy Policy', href: '/privacy' },
    { label: 'Terms of Service', href: '/terms' },
    { label: 'Cookie Policy', href: '/cookies' },
  ],
}

const socials = [
  { icon: Twitter, href: 'https://twitter.com/voicesplit', label: 'Twitter' },
  { icon: Github, href: 'https://github.com/voicesplit', label: 'GitHub' },
  { icon: MessageCircle, href: 'https://discord.gg/voicesplit', label: 'Discord' },
]

export function Footer() {
  return (
    <footer className="border-t border-brand-cyan/10 bg-[#0d1628]/80">
      <div className="max-w-7xl mx-auto px-6 pt-16 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 mb-12">
          {/* Brand */}
          <div className="lg:col-span-2 space-y-4">
            <Logo size={40} />
            <p className="text-muted text-sm max-w-xs leading-relaxed">
              AI-powered speaker isolation. Choose the voice that matters — with studio-quality precision.
            </p>
            <div className="flex items-center gap-3">
              {socials.map(({ icon: Icon, href, label }) => (
                <Link
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className="w-9 h-9 rounded-xl glass flex items-center justify-center text-muted hover:text-brand-cyan hover:border-brand-cyan/30 transition-colors"
                >
                  <Icon className="w-4 h-4" />
                </Link>
              ))}
            </div>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([section, links]) => (
            <div key={section}>
              <h4 className="text-sm font-semibold text-white mb-4">{section}</h4>
              <ul className="space-y-2.5">
                {links.map(({ label, href }) => (
                  <li key={label}>
                    <Link
                      href={href}
                      className="text-sm text-muted hover:text-white transition-colors"
                    >
                      {label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="border-t border-brand-cyan/10 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted">
            © {new Date().getFullYear()} VoiceSplit. All rights reserved.
          </p>
          <p className="text-sm text-muted/60">
            Built with ❤️ for podcasters, researchers &amp; creators
          </p>
        </div>
      </div>
    </footer>
  )
}
