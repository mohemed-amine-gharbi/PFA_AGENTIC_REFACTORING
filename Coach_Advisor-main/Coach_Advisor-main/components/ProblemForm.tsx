'use client'
import { useState } from 'react'
import type { Language } from '@/lib/types'

interface Props {
  language: Language | null
  onSubmit: (problem: string) => void
  loading: boolean
}

const MAX = 500

export default function ProblemForm({ language, onSubmit, loading }: Props) {
  const [problem, setProblem] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (e.target.value.length <= MAX) setProblem(e.target.value)
  }

  const canSubmit = !!language && problem
  .trim().length > 10 && !loading

  return (
    <div>
      <label style={{
        display: 'block',
        fontSize: '0.68rem',
        letterSpacing: '0.16em',
        textTransform: 'uppercase',
        color: 'var(--accent)',
        marginBottom: 14,
        fontWeight: 700,
      }}>
        02 — Describe your problem{' '}
        <span style={{ color: 'var(--text-muted)', textTransform: 'none', letterSpacing: 0 }}>
          (no code, just the idea)
        </span>
      </label>

      <textarea
        value={problem}
        onChange={handleChange}
        placeholder="e.g. I need to merge two sorted lists into one sorted list efficiently..."
        rows={5}
        style={{
          width: '100%',
          background: 'var(--surface2)',
          border: '1px solid var(--border)',
          color: 'var(--text-bright)',
          fontFamily: 'var(--mono)',
          fontSize: '0.88rem',
          lineHeight: 1.75,
          padding: '14px 18px',
          borderRadius: 'var(--r)',
          resize: 'vertical',
          outline: 'none',
          transition: 'border-color 0.2s, box-shadow 0.2s',
          minHeight: 120,
        }}
        onFocus={e => {
          e.target.style.borderColor = 'var(--accent)'
          e.target.style.boxShadow = '0 0 0 3px var(--accent-dim)'
        }}
        onBlur={e => {
          e.target.style.borderColor = 'var(--border)'
          e.target.style.boxShadow = 'none'
        }}
      />
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: 6,
      }}>
        <span style={{
          fontSize: '0.68rem',
          color: problem.trim().length > 10 ? 'var(--green)' : 'var(--text-muted)',
        }}>
          {problem.trim().length > 10 ? '✓ Ready' : 'Min 10 characters'}
        </span>
        <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
          {problem.length} / {MAX}
        </span>
      </div>

      <button
        disabled={!canSubmit}
        onClick={() => canSubmit && onSubmit(problem.trim())}
        style={{
          marginTop: 20,
          width: '100%',
          padding: '15px 24px',
          background: canSubmit ? 'var(--accent)' : 'var(--surface3)',
          color: canSubmit ? '#000' : 'var(--text-muted)',
          fontFamily: 'var(--display)',
          fontSize: '0.95rem',
          fontWeight: 700,
          letterSpacing: '0.05em',
          border: `1px solid ${canSubmit ? 'var(--accent)' : 'var(--border)'}`,
          borderRadius: 'var(--r)',
          cursor: canSubmit ? 'pointer' : 'not-allowed',
          transition: 'all 0.2s ease',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 10,
          boxShadow: canSubmit ? '0 0 20px var(--accent-glow)' : 'none',
        }}
        onMouseEnter={e => {
          if (canSubmit) (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-1px)'
        }}
        onMouseLeave={e => {
          (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(0)'
        }}
      >
        {loading ? (
          <>
            <span style={{
              width: 16, height: 16,
              border: '2px solid rgba(0,0,0,0.3)',
              borderTopColor: '#000',
              borderRadius: '50%',
              animation: 'spin 0.7s linear infinite',
              display: 'inline-block',
            }} />
            Analyzing...
          </>
        ) : (
          <>⚡ Get Best Practices</>
        )}
      </button>
    </div>
  )
}
