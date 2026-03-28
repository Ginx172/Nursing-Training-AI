/** @type {import('next').NextConfig} */
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const nextConfig = {
  images: {
    domains: ['localhost', '127.0.0.1'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.onrender.com',
      },
    ],
  },
  env: {
    NEXT_PUBLIC_API_URL: API_URL,
    NEXT_PUBLIC_APP_NAME: 'Nursing Training AI',
    NEXT_PUBLIC_APP_VERSION: '1.0.0',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${API_URL}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
