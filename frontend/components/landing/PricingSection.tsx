'use client'

import { motion } from 'framer-motion'
import { Check, Zap, Building2 } from 'lucide-react'
import Link from 'next/link'
import { GlassCard } from '@/components/common/GlassCard'
import { GradientButton } from '@/components/common/GradientButton'
import { cn } from '@/lib/utils'

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: '/month',
    description: 'Perfect for trying out VoiceSplit',
    icon: Zap,
    featured: false,
    cta: 'Get Started Free',
    href: '/register',
    features: [
      '5 minutes / month',
      'Up to 2 speakers',
      'MP3 export',
      'Basic transcript',
      'Standard processing',
    ],
  },
  {
    name: 'Pro',
    price: '$19',
    period: '/month',
    description: 'For podcasters and content creators',
    icon: Zap,
    featured: true,
    cta: 'Start Pro Trial',
    href: '/register?plan=pro',
    badge: 'Most Popular',
    features: [
      '2 hours / month',
      'Unlimited speakers',
      'All export formats (MP3, WAV, FLAC)',
      'Full transcript + search',
      'Priority processing',
      'Analytics dashboard',
      'API access',
    ],
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For teams and large-scale operations',
    icon: Building2,
    featured: false,
    cta: 'Contact Sales',
    href: 'mailto:sales@voicesplit.ai',
    features: [
      'Unlimited processing',
      'Custom AI models',
      'Dedicated infrastructure',
      'SLA guarantee',
      'Priority support',
      'Custom integrations',
      'On-premise option',
    ],
  },
]

export function PricingSection() {
  return (
    <section id="pricing" className="py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1.5 rounded-full glass border border-brand-cyan/20 text-brand-cyan text-sm font-medium mb-4">
            Pricing
          </span>
          <h2 className="text-4xl font-bold text-white mb-4">
            Simple, <span className="gradient-text">transparent pricing</span>
          </h2>
          <p className="text-muted max-w-xl mx-auto text-lg">
            No hidden fees. Cancel anytime. Start for free.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              <div
                className={cn(
                  'relative rounded-2xl p-6 transition-all duration-300',
                  plan.featured
                    ? 'gradient-border shadow-[0_0_40px_rgba(6,214,207,0.2)] scale-105'
                    : 'glass glass-hover',
                )}
              >
                {plan.badge && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="px-4 py-1 bg-gradient-to-r from-brand-cyan to-brand-blue rounded-full text-xs font-semibold text-white whitespace-nowrap">
                      {plan.badge}
                    </span>
                  </div>
                )}

                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-white mb-1">{plan.name}</h3>
                  <p className="text-sm text-muted mb-4">{plan.description}</p>
                  <div className="flex items-baseline gap-1">
                    <span className={cn('text-4xl font-bold', plan.featured ? 'gradient-text' : 'text-white')}>
                      {plan.price}
                    </span>
                    {plan.period && <span className="text-muted text-sm">{plan.period}</span>}
                  </div>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2.5">
                      <Check className="w-4 h-4 text-brand-cyan flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-slate-300">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link href={plan.href}>
                  <GradientButton
                    className="w-full"
                    variant={plan.featured ? 'gradient' : 'outline'}
                  >
                    {plan.cta}
                  </GradientButton>
                </Link>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
