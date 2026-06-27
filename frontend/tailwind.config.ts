import type { Config } from 'tailwindcss'
import { fontFamily } from 'tailwindcss/defaultTheme'

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: '',
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        brand: {
          cyan: '#06D6CF',
          blue: '#3B82F6',
          purple: '#7C3AED',
        },
        background: '#0B1120',
        card: '#111827',
        'card-hover': '#1a2236',
        border: 'rgba(6,214,207,0.15)',
        muted: {
          DEFAULT: '#94A3B8',
          foreground: '#64748B',
        },
        foreground: '#F8FAFC',
        success: '#22C55E',
        danger: '#EF4444',
        warning: '#F59E0B',
        input: 'rgba(255,255,255,0.06)',
        ring: '#06D6CF',
        primary: {
          DEFAULT: '#06D6CF',
          foreground: '#0B1120',
        },
        secondary: {
          DEFAULT: '#111827',
          foreground: '#F8FAFC',
        },
        destructive: {
          DEFAULT: '#EF4444',
          foreground: '#F8FAFC',
        },
        accent: {
          DEFAULT: '#3B82F6',
          foreground: '#F8FAFC',
        },
        popover: {
          DEFAULT: '#111827',
          foreground: '#F8FAFC',
        },
      },
      fontFamily: {
        sans: ['Inter', ...fontFamily.sans],
      },
      borderRadius: {
        lg: '1rem',
        md: '0.75rem',
        sm: '0.5rem',
        xl: '1.25rem',
        '2xl': '1.5rem',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        'glow-pulse': {
          '0%,100%': { boxShadow: '0 0 20px rgba(6,214,207,0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(6,214,207,0.6)' },
        },
        waveform: {
          '0%,100%': { scaleY: '0.3' },
          '50%': { scaleY: '1' },
        },
        float: {
          '0%,100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'fade-in': {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        waveform: 'waveform 1.2s ease-in-out infinite',
        float: 'float 3s ease-in-out infinite',
        'fade-in': 'fade-in 0.5s ease-out',
        shimmer: 'shimmer 2s linear infinite',
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(135deg, #06D6CF, #3B82F6, #7C3AED)',
        'card-gradient': 'linear-gradient(135deg, rgba(17,24,39,0.8), rgba(11,17,32,0.9))',
      },
      boxShadow: {
        glow: '0 0 20px rgba(6,214,207,0.35)',
        'glow-lg': '0 0 40px rgba(6,214,207,0.4)',
        'glow-purple': '0 0 20px rgba(124,58,237,0.35)',
        card: '0 4px 24px rgba(0,0,0,0.4)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config
