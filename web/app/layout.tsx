import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'MemoryAid - AI-Powered Memory Assistant',
  description: 'Capture, store, and search through your visual memories with AI assistance',
  keywords: ['memory', 'AI', 'assistant', 'image', 'search', 'capture'],
  authors: [{ name: 'MemoryAid Team' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50 text-gray-900 antialiased`}>
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}
