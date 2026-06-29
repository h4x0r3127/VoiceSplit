import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'standalone',

  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**.amazonaws.com' },
      { protocol: 'http', hostname: 'localhost' },
      { protocol: 'http', hostname: 'minio' },
      { protocol: 'https', hostname: 'lh3.googleusercontent.com' },
    ],
  },

  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',

    NEXT_PUBLIC_WS_URL:
      process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8000',
  },
}

export default nextConfig
