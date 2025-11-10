import type { Metadata } from 'next'
import { Righteous } from 'next/font/google'
import './globals.css'

const righteous = Righteous({
  weight: '400',
  subsets: ['latin'],
  variable: '--font-righteous',
})

export const metadata: Metadata = {
  title: 'Research Agents',
  description: 'A modern Next.js application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={righteous.variable}>{children}</body>
    </html>
  )
}

