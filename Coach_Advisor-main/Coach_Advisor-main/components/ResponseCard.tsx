'use client'
import { renderMarkdown } from '@/lib/markdown'

interface Props {
  language: string
  problem: string
  advice: string
  onReset: () => void
}

export default function ResponseCard({ language, problem, advice, onReset }: Props) {
  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--r-lg)',
      overflow: 'hidden',
      animation: 'fadeUp 0.5s ease both',
      position: 'relative',
      zIndex: 1,
    }}>
      {/* Top accent line */}
      <div style={{
        height: 2,
        background: 'linear-gradient(90deg, transparent, var(--accent), transparent)',
      }} />

      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '16px 28px',
        background: 'var(--surface2)',
        borderBottom: '1px solid var(--border)',
      }}>
        <span style={{
          background: 'var(--accent)',
          color: '#000',
          fontFamily: 'var(--display)',
          fontSize: '0.72rem',
          fontWeight: 700,
          padding: '3px 12px',
          borderRadius: 20,
          letterSpacing: '0.07em',
        }}>
          {language}
        </span>
        <span style={{
          fontFamily: 'var(--display)',
          fontSize: '0.85rem',
          fontWeight: 600,
          color: 'var(--text-bright)',
          flex: 1,
        }}>
          Coach Recommendations
        </span>
        <button
          onClick={onReset}
          title="Ask another question"
          style={{
            background: 'none',
            border: '1px solid var(--border)',
            color: 'var(--text-muted)',
            fontFamily: 'var(--mono)',
            fontSize: '0.7rem',
            padding: '5px 12px',
            borderRadius: 6,
            cursor: 'pointer',
            transition: 'all 0.15s',
          }}
          onMouseEnter={e => {
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--danger)'
            ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--danger)'
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border)'
            ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--text-muted)'
          }}
        >
          ↩ New Question
        </button>
      </div>

      {/* Problem summary */}
      <div style={{
        padding: '14px 28px',
        background: 'rgba(240,165,0,0.04)',
        borderBottom: '1px solid var(--border)',
        fontSize: '0.78rem',
        color: 'var(--text-muted)',
      }}>
        <span style={{ color: 'var(--accent)', marginRight: 8 }}>▸</span>
        <em style={{ color: 'var(--text)' }}>{problem}</em>
      </div>

      {/* Advice body */}
      <div
        className="prose"
        style={{ padding: '24px 32px', fontSize: '0.87rem' }}
        dangerouslySetInnerHTML={{ __html: renderMarkdown(advice) }}
      />
    </div>
  )
}
