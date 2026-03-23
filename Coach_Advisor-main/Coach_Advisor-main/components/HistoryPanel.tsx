'use client'
import type { HistoryEntry } from '@/lib/types'

interface Props {
  history: HistoryEntry[]
  onSelect: (entry: HistoryEntry) => void
  onClear: () => void
}

function timeAgo(date: Date): string {
  const sec = Math.floor((Date.now() - date.getTime()) / 1000)
  if (sec < 60) return 'just now'
  if (sec < 3600) return `${Math.floor(sec / 60)}m ago`
  return `${Math.floor(sec / 3600)}h ago`
}

export default function HistoryPanel({ history, onSelect, onClear }: Props) {
  if (history.length === 0) return null

  return (
    <aside style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--r-lg)',
      overflow: 'hidden',
      animation: 'slideIn 0.4s ease both',
      position: 'relative',
      zIndex: 1,
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '13px 20px',
        background: 'var(--surface2)',
        borderBottom: '1px solid var(--border)',
      }}>
        <span style={{
          fontFamily: 'var(--display)',
          fontSize: '0.78rem',
          fontWeight: 700,
          color: 'var(--text-bright)',
          letterSpacing: '0.05em',
        }}>
          🕓 History
          <span style={{
            marginLeft: 8,
            background: 'var(--surface3)',
            border: '1px solid var(--border2)',
            color: 'var(--text-muted)',
            fontSize: '0.65rem',
            padding: '1px 8px',
            borderRadius: 10,
          }}>
            {history.length}
          </span>
        </span>
        <button
          onClick={onClear}
          style={{
            background: 'none',
            border: '1px solid var(--border)',
            color: 'var(--text-muted)',
            fontFamily: 'var(--mono)',
            fontSize: '0.65rem',
            padding: '3px 10px',
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
          Clear all
        </button>
      </div>

      {/* Entries */}
      <div style={{ maxHeight: 320, overflowY: 'auto' }}>
        {history.map((entry, i) => (
          <button
            key={entry.id}
            onClick={() => onSelect(entry)}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'flex-start',
              gap: 12,
              padding: '12px 20px',
              background: 'none',
              border: 'none',
              borderBottom: i < history.length - 1 ? '1px solid var(--border)' : 'none',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'background 0.15s',
              animation: `slideIn 0.3s ${i * 0.05}s ease both`,
            }}
            onMouseEnter={e => (e.currentTarget as HTMLButtonElement).style.background = 'var(--surface2)'}
            onMouseLeave={e => (e.currentTarget as HTMLButtonElement).style.background = 'none'}
          >
            {/* Lang badge */}
            <span style={{
              flexShrink: 0,
              marginTop: 2,
              background: 'var(--accent-dim)',
              border: '1px solid rgba(240,165,0,0.25)',
              color: 'var(--accent)',
              fontSize: '0.62rem',
              fontFamily: 'var(--display)',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: 6,
              letterSpacing: '0.05em',
              whiteSpace: 'nowrap',
            }}>
              {entry.language}
            </span>

            {/* Problem text */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{
                fontSize: '0.78rem',
                color: 'var(--text)',
                lineHeight: 1.5,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {entry.problem}
              </p>
              <p style={{
                fontSize: '0.65rem',
                color: 'var(--text-muted)',
                marginTop: 3,
              }}>
                {timeAgo(entry.timestamp)}
              </p>
            </div>

            {/* Arrow */}
            <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 2 }}>›</span>
          </button>
        ))}
      </div>
    </aside>
  )
}
