import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CodeCoach — LLM Dev Advisor',
  description: 'Describe your coding problem, get language-specific best practices powered by AI.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
