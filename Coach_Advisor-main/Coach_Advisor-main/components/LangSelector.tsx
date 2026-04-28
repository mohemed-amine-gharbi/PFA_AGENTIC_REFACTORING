'use client'
import { LANGUAGES, type Language } from '@/lib/types'

interface Props {
  selected: Language | null
  onSelect: (lang: Language) => void
}

export default function LangSelector({ selected, onSelect }: Props) {
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
        01 — Select Language
      </label>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 8,
      }}>
        {LANGUAGES.map(({ key, emoji }) => {
          const isActive = selected === key
          return (
            <button
              key={key}
              onClick={() => onSelect(key as Language)}
              style={{
                background: isActive ? 'var(--accent-dim)' : 'var(--surface2)',
                border: `1px solid ${isActive ? 'var(--accent)' : 'var(--border)'}`,
                color: isActive ? 'var(--accent)' : 'var(--text)',
                fontFamily: 'var(--mono)',
                fontSize: '0.76rem',
                padding: '7px 14px',
                borderRadius: 8,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                boxShadow: isActive ? '0 0 14px var(--accent-glow)' : 'none',
                transform: isActive ? 'scale(1.04)' : 'scale(1)',
              }}
              onMouseEnter={e => {
                if (!isActive) {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border2)'
                  ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--text-bright)'
                }
              }}
              onMouseLeave={e => {
                if (!isActive) {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border)'
                  ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--text)'
                }
              }}
            >
              {emoji} {key}
            </button>
          )
        })}
      </div>
    </div>
  )
}
