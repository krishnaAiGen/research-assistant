import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Research Assistant',
  description: 'AI-powered research assistant for scientific literature',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        <div className="container mx-auto px-4 py-8">
          <header className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Research Assistant
            </h1>
            <p className="text-gray-600">
              Ask questions about scientific literature and get AI-powered answers
            </p>
          </header>
          <main>
            {children}
          </main>
        </div>
      </body>
    </html>
  )
} 