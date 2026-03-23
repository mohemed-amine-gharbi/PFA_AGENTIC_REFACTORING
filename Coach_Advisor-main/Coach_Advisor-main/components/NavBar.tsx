'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { getCurrentUser, signOut, User } from '@/lib/auth';

export default function NavBar() {
  const [user, setUser] = useState<User | null>(null);
  const [showMenu, setShowMenu] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    setUser(getCurrentUser());
  }, [pathname]);

  const handleSignOut = async () => {
    await signOut();
    setUser(null);
    router.push('/auth');
  };

  // Ne pas afficher la navbar sur la page d'auth
  if (pathname === '/auth') return null;

  return (
    <nav style={{
      position: 'sticky',
      top: 0,
      zIndex: 1000,
      background: 'rgba(7, 9, 12, 0.95)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid rgba(240, 165, 0, 0.2)',
      padding: '0 24px',
    }}>
      <div style={{
        maxWidth: 1400,
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 64,
      }}>
        {/* Logo */}
        <Link href="/" style={{
          fontSize: '1.5rem',
          fontWeight: 'bold',
          background: 'linear-gradient(135deg, var(--accent), var(--cyan))',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          textDecoration: 'none',
          fontFamily: 'var(--display)',
        }}>
          AI Refactoring Suite
        </Link>

        {/* Navigation Links */}
        <div style={{ display: 'flex', gap: 32, alignItems: 'center' }}>
          <Link href="/" style={{
            color: pathname === '/' ? 'var(--accent)' : 'var(--text)',
            textDecoration: 'none',
            fontWeight: 500,
            transition: 'color 0.2s',
            padding: '8px 0',
            borderBottom: pathname === '/' ? `2px solid var(--accent)` : 'none',
            fontFamily: 'var(--mono)',
            fontSize: '0.85rem',
          }}>
            Coach Advisor
          </Link>
          
          <Link href="/refactoring" style={{
            color: pathname === '/refactoring' ? 'var(--accent)' : 'var(--text)',
            textDecoration: 'none',
            fontWeight: 500,
            transition: 'color 0.2s',
            padding: '8px 0',
            borderBottom: pathname === '/refactoring' ? `2px solid var(--accent)` : 'none',
            fontFamily: 'var(--mono)',
            fontSize: '0.85rem',
          }}>
            Refactoring Pro
          </Link>
        </div>

        {/* User Menu */}
        {user ? (
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowMenu(!showMenu)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                background: 'rgba(240, 165, 0, 0.1)',
                border: '1px solid rgba(240, 165, 0, 0.3)',
                borderRadius: 24,
                padding: '6px 12px 6px 8px',
                cursor: 'pointer',
                color: 'var(--text)',
                fontSize: '0.85rem',
                fontFamily: 'var(--mono)',
              }}
            >
              <div style={{
                width: 32,
                height: 32,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, var(--accent), var(--cyan))',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.9rem',
                color: '#07090c',
                fontWeight: 'bold',
              }}>
                {user.email?.[0]?.toUpperCase() || 'U'}
              </div>
              <span>{user.email?.split('@')[0]}</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6 9l6 6 6-6" />
              </svg>
            </button>
            
            {showMenu && (
              <div style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                marginTop: 8,
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                borderRadius: 12,
                minWidth: 200,
                boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
                zIndex: 1001,
              }}>
                <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'var(--mono)' }}>
                    Connecté en tant que
                  </div>
                  <div style={{ fontWeight: 500, marginTop: 4, color: 'var(--text-bright)' }}>
                    {user.email}
                  </div>
                  {user.name && <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{user.name}</div>}
                </div>
                <button
                  onClick={handleSignOut}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '12px 16px',
                    background: 'none',
                    border: 'none',
                    color: 'var(--danger)',
                    cursor: 'pointer',
                    fontSize: '0.85rem',
                    fontFamily: 'var(--mono)',
                  }}
                >
                  Se déconnecter
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link href="/auth" style={{
            background: 'linear-gradient(135deg, var(--accent), var(--cyan))',
            color: '#07090c',
            padding: '8px 20px',
            borderRadius: 24,
            textDecoration: 'none',
            fontSize: '0.85rem',
            fontWeight: 500,
            fontFamily: 'var(--mono)',
          }}>
            Se connecter
          </Link>
        )}
      </div>
    </nav>
  );
}