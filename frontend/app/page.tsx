'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { LandingNavbar } from '@/components/layout/LandingNavbar'
import { Footer } from '@/components/layout/Footer'
import { HeroSection } from '@/components/landing/HeroSection'
import { FeaturesSection } from '@/components/landing/FeaturesSection'
import { HowItWorks } from '@/components/landing/HowItWorks'
import { InteractiveDemo } from '@/components/landing/InteractiveDemo'
import { PricingSection } from '@/components/landing/PricingSection'
import { FAQSection } from '@/components/landing/FAQSection'

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <LandingNavbar />
      <main className="flex-1">
        <HeroSection />
        <FeaturesSection />
        <HowItWorks />
        <InteractiveDemo />
        <PricingSection />
        <FAQSection />
      </main>
      <Footer />
    </div>
  )
}
