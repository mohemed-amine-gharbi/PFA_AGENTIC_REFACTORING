'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getCurrentUser } from '@/lib/auth';

export default function RefactoringPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      if (!isAuthenticated()) {
        router.push('/auth');
        return;
      }
      
      // Récupérer le token utilisateur
      const user = getCurrentUser();
      
      // Rediriger vers l'application Streamlit avec le token
      // Assurez-vous que Streamlit tourne sur http://localhost:8501
      const streamlitUrl = `http://localhost:8501?token=${user?.id}&email=${encodeURIComponent(user?.email || '')}`;
      
      // Ouvrir dans un nouvel onglet ou remplacer la page actuelle
      // window.location.href = streamlitUrl; // Pour remplacer
      window.open(streamlitUrl, '_blank'); // Pour ouvrir dans un nouvel onglet
      
      setLoading(false);
    };
    
    checkAuth();
  }, [router]);

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      gap: 20,
      background: 'var(--bg)',
      color: 'var(--text)',
    }}>
      <div style={{
        width: 50,
        height: 50,
        border: '3px solid var(--border)',
        borderTopColor: 'var(--accent)',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
      }} />
      <p style={{ fontFamily: 'var(--mono)' }}>
        {loading ? 'Redirection vers Refactoring Pro...' : 'Ouverture de Refactoring Pro...'}
      </p>
      <button
        onClick={() => router.push('/')}
        style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          color: 'var(--text)',
          padding: '8px 16px',
          borderRadius: 8,
          cursor: 'pointer',
          fontFamily: 'var(--mono)',
        }}
      >
        Retour au Coach Advisor
      </button>
    </div>
  );
}