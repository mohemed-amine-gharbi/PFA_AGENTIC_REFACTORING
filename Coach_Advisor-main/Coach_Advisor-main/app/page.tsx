'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import LangSelector from '@/components/LangSelector'
import ProblemForm from '@/components/ProblemForm'
import ResponseCard from '@/components/ResponseCard'
import HistoryPanel from '@/components/HistoryPanel'
import type { HistoryEntry, Language } from '@/lib/types'
import { isAuthenticated, getCurrentUser } from '@/lib/auth'

type View = 'form' | 'response'

export default function Home() {
  const router = useRouter()
  const [view, setView] = useState<View>('form')
  const [selectedLang, setSelectedLang] = useState<Language | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [current, setCurrent] = useState<HistoryEntry | null>(null)
  const [authenticated, setAuthenticated] = useState(false)

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/auth')
    } else {
      setAuthenticated(true)
    }
  }, [router])

  const handleSubmit = async (problem: string) => {
    if (!selectedLang) return
    setLoading(true)
    setError(null)
    try {
      const user = getCurrentUser()
      const res = await fetch('/api/coach', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          language: selectedLang, 
          problem,
          userId: user?.id 
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'API error')
      const entry: HistoryEntry = {
        id: typeof crypto !== 'undefined' && crypto.randomUUID
          ? crypto.randomUUID()
          : Math.random().toString(36).slice(2) + Date.now().toString(36),
        language: selectedLang,
        problem,
        advice: data.advice,
        timestamp: new Date(),
      }
      setHistory(prev => [entry, ...prev].slice(0, 20))
      setCurrent(entry)
      setView('response')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => { setView('form'); setCurrent(null); setError(null) }
  const handleHistorySelect = (entry: HistoryEntry) => { setCurrent(entry); setView('response') }

  if (!authenticated) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        color: 'var(--text)'
      }}>
        <div>Vérification de l'authentification...</div>
      </div>
    )
  }

  return (
    <div style={{ minHeight:'100vh', display:'flex', flexDirection:'column', alignItems:'center', padding:'0 16px 80px', position:'relative' }}>
      <div style={{ width:'100%', maxWidth:860, position:'relative', zIndex:1 }}>
        <Header />
        <div style={{ display:'grid', gridTemplateColumns: history.length > 0 ? '1fr 300px' : '1fr', gap:20, alignItems:'start' }}>
          <div style={{ display:'flex', flexDirection:'column', gap:20 }}>
            {view === 'form' && (
              <div style={{ background:'var(--surface)', border:'1px solid var(--border)', borderRadius:'var(--r-lg)', padding:'32px 36px', display:'flex', flexDirection:'column', gap:28, animation:'fadeUp 0.5s ease both', position:'relative', overflow:'hidden' }}>
                <div style={{ position:'absolute', top:0, left:0, right:0, height:2, background:'linear-gradient(90deg, transparent, var(--accent), transparent)', opacity:0.6 }} />
                <LangSelector selected={selectedLang} onSelect={setSelectedLang} />
                <ProblemForm language={selectedLang} onSubmit={handleSubmit} loading={loading} />
                {error && (
                  <div style={{ background:'rgba(255,71,87,0.08)', border:'1px solid rgba(255,71,87,0.3)', color:'var(--danger)', borderRadius:8, padding:'12px 16px', fontSize:'0.8rem' }}>
                    ⚠ {error}
                  </div>
                )}
              </div>
            )}
            {view === 'response' && current && (
              <ResponseCard language={current.language} problem={current.problem} advice={current.advice} onReset={handleReset} />
            )}
          </div>
          {history.length > 0 && (
            <HistoryPanel history={history} onSelect={handleHistorySelect} onClear={() => setHistory([])} />
          )}
        </div>
        <footer style={{ marginTop:48, textAlign:'center', fontSize:'0.68rem', color:'var(--text-muted)', letterSpacing:'0.05em' }}>
          Powered by <span style={{ color:'var(--accent)' }}>Claude claude-sonnet-4</span> · Built for developers
        </footer>
      </div>
    </div>
  )
}