'use client'

export default function Header() {
  return (
    <header style={{
      textAlign: 'center',
      padding: '52px 0 28px',
      animation: 'fadeDown 0.7s ease both',
      position: 'relative',
      zIndex: 1,
    }}>
      <div style={{
        fontFamily: 'var(--display)',
        fontSize: 'clamp(2rem, 5vw, 3rem)',
        fontWeight: 800,
        color: 'var(--text-bright)',
        letterSpacing: '-1px',
        lineHeight: 1,
      }}>
        <span style={{ color: 'var(--accent)', textShadow: '0 0 24px var(--accent-glow)', fontWeight: 400 }}>{`{`}</span>
        {' '}CodeCoach{' '}
        <span style={{ color: 'var(--accent)', textShadow: '0 0 24px var(--accent-glow)', fontWeight: 400 }}>{`}`}</span>
      </div>
      <p style={{
        marginTop: 12,
        fontSize: '0.7rem',
        color: 'var(--text-muted)',
        letterSpacing: '0.15em',
        textTransform: 'uppercase',
      }}>
        LLM-Powered Best Practice Advisor &nbsp;·&nbsp; Describe your problem, get expert guidance
      </p>
      <div style={{
        marginTop: 16,
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        background: 'var(--surface2)',
        border: '1px solid var(--border)',
        borderRadius: 20,
        padding: '4px 14px',
        fontSize: '0.68rem',
        color: 'var(--accent)',
        letterSpacing: '0.1em',
      }}>
        <span style={{
          width: 6, height: 6,
          borderRadius: '50%',
          background: 'var(--green)',
          boxShadow: '0 0 8px var(--green)',
          animation: 'blink 2s ease infinite',
          display: 'inline-block',
        }} />
       Powered By  Rouag Dhia - Gharbi Mohamed amine - Yassine Missaoui
      </div>
    </header>
  )
}
