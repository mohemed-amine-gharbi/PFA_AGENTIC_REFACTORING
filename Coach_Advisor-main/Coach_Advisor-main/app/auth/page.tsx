'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signIn, signUp } from '@/lib/auth';

export default function AuthPage() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await signIn(email, password);
      } else {
        await signUp(email, password, name);
      }
      router.push('/');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg)',
      padding: '20px',
      position: 'relative',
      zIndex: 1,
    }}>
      <div style={{
        maxWidth: 450,
        width: '100%',
        background: 'var(--surface)',
        borderRadius: 'var(--r-lg)',
        padding: '40px 32px',
        border: '1px solid var(--border)',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
      }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <h1 style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, var(--accent), var(--cyan))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: 8,
            fontFamily: 'var(--display)',
          }}>
            {isLogin ? 'Connexion' : 'Inscription'}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontFamily: 'var(--mono)', fontSize: '0.85rem' }}>
            {isLogin ? 'Accédez à votre compte' : 'Créez un nouveau compte'}
          </p>
        </div>

        {error && (
          <div style={{
            background: 'rgba(255, 71, 87, 0.1)',
            border: '1px solid rgba(255, 71, 87, 0.3)',
            borderRadius: 8,
            padding: '12px 16px',
            marginBottom: 24,
            color: 'var(--danger)',
            fontSize: '0.85rem',
            fontFamily: 'var(--mono)',
          }}>
            ⚠ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {!isLogin && (
            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: 8, 
                color: 'var(--text)', 
                fontSize: '0.85rem',
                fontFamily: 'var(--mono)',
              }}>
                Nom
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'var(--surface2)',
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  color: 'var(--text-bright)',
                  fontSize: '0.9rem',
                  outline: 'none',
                  transition: 'border-color 0.2s',
                  fontFamily: 'var(--mono)',
                }}
                placeholder="Votre nom"
              />
            </div>
          )}

          <div>
            <label style={{ 
              display: 'block', 
              marginBottom: 8, 
              color: 'var(--text)', 
              fontSize: '0.85rem',
              fontFamily: 'var(--mono)',
            }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'var(--surface2)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                color: 'var(--text-bright)',
                fontSize: '0.9rem',
                outline: 'none',
                fontFamily: 'var(--mono)',
              }}
              placeholder="exemple@email.com"
              required
            />
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              marginBottom: 8, 
              color: 'var(--text)', 
              fontSize: '0.85rem',
              fontFamily: 'var(--mono)',
            }}>
              Mot de passe
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'var(--surface2)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                color: 'var(--text-bright)',
                fontSize: '0.9rem',
                outline: 'none',
                fontFamily: 'var(--mono)',
              }}
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              background: 'linear-gradient(135deg, var(--accent), var(--cyan))',
              color: '#07090c',
              padding: '12px 24px',
              borderRadius: 8,
              border: 'none',
              fontSize: '0.9rem',
              fontWeight: 500,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              transition: 'opacity 0.2s',
              marginTop: 8,
              fontFamily: 'var(--mono)',
            }}
          >
            {loading ? 'Chargement...' : (isLogin ? 'Se connecter' : "S'inscrire")}
          </button>
        </form>

        <div style={{ marginTop: 24, textAlign: 'center' }}>
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
            }}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--accent)',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontFamily: 'var(--mono)',
            }}
          >
            {isLogin ? "Pas encore de compte ? S'inscrire" : 'Déjà un compte ? Se connecter'}
          </button>
        </div>
      </div>
    </div>
  );
}