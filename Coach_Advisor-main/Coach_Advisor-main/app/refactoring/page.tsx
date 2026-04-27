'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { getCurrentUser } from '@/lib/auth';

// ── Types ─────────────────────────────────────────────────────────────────────

interface AgentResult {
  name: string;
  analysis: string[];
  proposal?: string;
  temperature_used: number | string;
  execution_time: number;
  status?: string;
}

interface PatchResult {
  analysis: Array<{ note: string } | string>;
  changes_applied: string[];
  execution_time: number;
}

interface TestResult {
  status: 'SUCCESS' | 'FAILED' | 'WARNING' | string;
  summary: string[];
  details: Array<{ tool: string; status: string; output: string }>;
  execution_time: number;
}

interface Report {
  rr: AgentResult[];
  pr: PatchResult | null;
  tr: TestResult | null;
  merd: number;
  totd: number;
  mode: string;
}

interface RefactoringResult {
  success: boolean;
  refactored_code: string;
  original_code: string;
  report: Report;
  error?: string;
  execution_time: number;
}

// ── Constantes ────────────────────────────────────────────────────────────────

const LANGUAGE_MAP: Record<string, [string, string]> = {
  '.py':   ['Python',     'python'],
  '.js':   ['JavaScript', 'javascript'],
  '.ts':   ['TypeScript', 'typescript'],
  '.java': ['Java',       'java'],
  '.cpp':  ['C++',        'cpp'],
  '.c':    ['C',          'c'],
  '.cs':   ['C#',         'csharp'],
  '.go':   ['Go',         'go'],
  '.rb':   ['Ruby',       'ruby'],
  '.rs':   ['Rust',       'rust'],
  '.php':  ['PHP',        'php'],
};

const MODELS = [
  'mistral:latest',
  'llama2:latest',
  'codellama:latest',
  'phi:latest',
  'qwen2.5-coder:latest',
];

const EXAMPLE_CODE = `# Exemple Python avec problèmes typiques
import os, sys, math, datetime

x = 10
y = 20

def calc(a, b):
    result = a + b
    if result > 10:
        if result < 20:
            if result % 2 == 0:
                return result * 2
            else:
                return result * 3
        else:
            return result
    return result

def process_items(items):
    output = []
    for item in items:
        if item > 0:
            output.append(item * 2)
    return output

def transform_data(data):
    result = []
    for d in data:
        if d > 0:
            result.append(d * 2)
    return result
`;

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatDuration(s: number): string {
  if (s < 1)  return `${(s * 1000).toFixed(0)}ms`;
  if (s < 60) return `${s.toFixed(2)}s`;
  return `${Math.floor(s / 60)}m ${(s % 60).toFixed(2)}s`;
}

function detectLanguage(filename: string): [string, string] {
  const ext = '.' + filename.split('.').pop()?.toLowerCase();
  return LANGUAGE_MAP[ext] ?? ['Python', 'python'];
}

function buildDiff(original: string, refactored: string): string {
  const origLines = original.split('\n');
  const refLines  = refactored.split('\n');
  const result: string[] = [];

  const maxLen = Math.max(origLines.length, refLines.length);
  for (let i = 0; i < maxLen; i++) {
    const o = origLines[i];
    const r = refLines[i];
    if (o === undefined) {
      result.push(`+ ${r}`);
    } else if (r === undefined) {
      result.push(`- ${o}`);
    } else if (o !== r) {
      result.push(`- ${o}`);
      result.push(`+ ${r}`);
    } else {
      result.push(`  ${o}`);
    }
  }
  return result.join('\n');
}

// ── Composant principal ───────────────────────────────────────────────────────

export default function RefactoringPage() {
  const router = useRouter();

  // Auth
  const [userEmail, setUserEmail] = useState<string>('');
  useEffect(() => {
    const user = getCurrentUser();
    if (!user) { router.push('/auth'); return; }
    setUserEmail(user.email ?? '');
  }, [router]);

  // Config
  const [modelName,   setModelName]   = useState('mistral:latest');
  const [autoPatch,   setAutoPatch]   = useState(true);
  const [autoTest,    setAutoTest]    = useState(true);
  const [useWorkflow, setUseWorkflow] = useState(true);

  // Agents
  const [availableAgents,    setAvailableAgents]    = useState<string[]>([]);
  const [agentEnabled,       setAgentEnabled]       = useState<Record<string, boolean>>({});
  const [agentTemperatures,  setAgentTemperatures]  = useState<Record<string, number>>({});
  const [backendStatus,      setBackendStatus]      = useState<'unknown' | 'ok' | 'down'>('unknown');

  // Source
  const [sourceCode,   setSourceCode]   = useState('');
  const [sourceFile,   setSourceFile]   = useState('');
  const [langName,     setLangName]     = useState('Python');
  const [langCode,     setLangCode]     = useState('python');
  const [exampleShown, setExampleShown] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Résultats
  const [result,    setResult]    = useState<RefactoringResult | null>(null);
  const [showDiff,  setShowDiff]  = useState(false);
  const [copied,    setCopied]    = useState(false);
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());

  // Exécution
  const [running,   setRunning]   = useState(false);
  const [progress,  setProgress]  = useState(0);
  const [statusMsg, setStatusMsg] = useState('');

  // ── Init : agents + health ─────────────────────────────────────────────────

  useEffect(() => {
    async function init() {
      // Health
      try {
        const h = await fetch('/api/refactoring/health');
        const hd = await h.json();
        setBackendStatus(hd.backend_reachable ? 'ok' : 'down');
      } catch { setBackendStatus('down'); }

      // Agents
      try {
        const r = await fetch('/api/refactoring/agents');
        const d = await r.json();
        const agents: string[] = d.agents ?? [];
        setAvailableAgents(agents);
        const enabled: Record<string, boolean>      = {};
        const temps:   Record<string, number>       = {};
        agents.forEach(a => { enabled[a] = true; temps[a] = 0.3; });
        setAgentEnabled(enabled);
        setAgentTemperatures(temps);
      } catch {
        const fallback = ['ComplexityAgent', 'DuplicationAgent', 'ImportAgent', 'LongFunctionAgent', 'RenameAgent'];
        setAvailableAgents(fallback);
        const enabled: Record<string, boolean> = {};
        const temps:   Record<string, number>  = {};
        fallback.forEach(a => { enabled[a] = true; temps[a] = 0.3; });
        setAgentEnabled(enabled);
        setAgentTemperatures(temps);
      }
    }
    init();
  }, []);

  // ── Handlers ──────────────────────────────────────────────────────────────

  function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => {
      const code = ev.target?.result as string;
      setSourceCode(code);
      setSourceFile(file.name);
      const [ln, lc] = detectLanguage(file.name);
      setLangName(ln); setLangCode(lc);
      setResult(null);
    };
    reader.readAsText(file);
  }

  function handleUseExample() {
    setSourceCode(EXAMPLE_CODE);
    setSourceFile('example.py');
    setLangName('Python'); setLangCode('python');
    setResult(null);
    setExampleShown(false);
  }

  function toggleAgent(name: string) {
    setAgentEnabled(prev => ({ ...prev, [name]: !prev[name] }));
  }

  function setTemp(name: string, val: number) {
    setAgentTemperatures(prev => ({ ...prev, [name]: val }));
  }

  const handleCopy = useCallback(async () => {
    if (!result?.refactored_code) return;
    await navigator.clipboard.writeText(result.refactored_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [result]);

  function handleDownload() {
    if (!result?.refactored_code) return;
    const blob = new Blob([result.refactored_code], { type: 'text/plain' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `refactored_${sourceFile}`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // ── Exécution ──────────────────────────────────────────────────────────────

  async function handleRun() {
    const activeAgents = availableAgents.filter(a => agentEnabled[a]);
    if (!sourceCode)         { alert('Chargez un fichier ou utilisez l\'exemple.'); return; }
    if (!activeAgents.length) { alert('Sélectionnez au moins un agent.'); return; }

    setRunning(true); setResult(null); setProgress(10);
    setStatusMsg('🔄 Envoi du code au backend…');

    try {
      setProgress(20); setStatusMsg('⚡ Analyse par les agents…');

      const response = await fetch('/api/refactoring/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code:               sourceCode,
          language:           langName,
          filename:           sourceFile,
          selected_agents:    activeAgents,
          agent_temperatures: Object.fromEntries(activeAgents.map(a => [a, agentTemperatures[a] ?? 0.3])),
          auto_patch:         autoPatch,
          auto_test:          autoTest,
          use_workflow:       useWorkflow,
          model_name:         modelName,
        }),
      });

      setProgress(80); setStatusMsg('🔄 Assemblage des résultats…');

      const data: RefactoringResult = await response.json();

      if (!data.success) {
        throw new Error(data.error ?? 'Erreur inconnue du serveur');
      }

      setProgress(100); setStatusMsg('✅ Terminé');
      setResult(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Erreur réseau';
      alert(`❌ Erreur : ${msg}`);
    } finally {
      setRunning(false);
      setTimeout(() => { setProgress(0); setStatusMsg(''); }, 1000);
    }
  }

  // ── Rendu ──────────────────────────────────────────────────────────────────

  const tempColor = (t: number) =>
    t < 0.3 ? '#3b82f6' : t < 0.7 ? '#f59e0b' : '#ef4444';

  const activeCount = availableAgents.filter(a => agentEnabled[a]).length;

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--background)', color: 'var(--text)', fontFamily: 'var(--mono)' }}>

      {/* ── Sidebar ── */}
      <aside style={{
        width: 280, flexShrink: 0,
        background: 'var(--surface)',
        borderRight: '1px solid var(--border)',
        padding: '24px 16px',
        display: 'flex', flexDirection: 'column', gap: 20,
        position: 'sticky', top: 64, height: 'calc(100vh - 64px)',
        overflowY: 'auto',
      }}>

        {/* Utilisateur */}
        <div style={{ padding: '10px 12px', borderRadius: 8, background: 'rgba(240,165,0,0.08)', border: '1px solid rgba(240,165,0,0.2)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>✅ Connecté</div>
          <div style={{ fontWeight: 600, color: 'var(--accent)', fontSize: '0.85rem', marginTop: 2 }}>{userEmail}</div>
        </div>

        {/* Status backend */}
        <div style={{
          fontSize: '0.72rem', padding: '6px 10px', borderRadius: 6,
          background: backendStatus === 'ok' ? 'rgba(16,185,129,0.1)' : backendStatus === 'down' ? 'rgba(239,68,68,0.1)' : 'rgba(100,116,139,0.1)',
          color:      backendStatus === 'ok' ? '#10b981'             : backendStatus === 'down' ? '#ef4444'             : '#64748b',
          border: `1px solid ${backendStatus === 'ok' ? 'rgba(16,185,129,0.3)' : backendStatus === 'down' ? 'rgba(239,68,68,0.3)' : 'rgba(100,116,139,0.3)'}`,
        }}>
          {backendStatus === 'ok' ? '🟢 Backend Python connecté' : backendStatus === 'down' ? '🔴 Backend Python hors ligne' : '⚪ Vérification…'}
        </div>

        <Divider label="🤖 Modèle LLM" />

        <select
          value={modelName}
          onChange={e => setModelName(e.target.value)}
          style={selectStyle}
        >
          {MODELS.map(m => <option key={m} value={m}>{m}</option>)}
        </select>

        <Divider label="🤖 Agents actifs" />

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {availableAgents.map(agent => (
            <div key={agent}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: '0.8rem' }}>
                  <input
                    type="checkbox"
                    checked={agentEnabled[agent] ?? true}
                    onChange={() => toggleAgent(agent)}
                    style={{ accentColor: 'var(--accent)', width: 14, height: 14 }}
                  />
                  <span style={{ color: agentEnabled[agent] ? 'var(--text-bright)' : 'var(--text-muted)' }}>
                    {agent.replace('Agent', '')}
                  </span>
                </label>
                <span style={{ fontSize: '0.7rem', color: tempColor(agentTemperatures[agent] ?? 0.3) }}>
                  🌡️ {(agentTemperatures[agent] ?? 0.3).toFixed(1)}
                </span>
              </div>
              {agentEnabled[agent] && (
                <input
                  type="range" min={0} max={1} step={0.1}
                  value={agentTemperatures[agent] ?? 0.3}
                  onChange={e => setTemp(agent, parseFloat(e.target.value))}
                  style={{ width: '100%', accentColor: tempColor(agentTemperatures[agent] ?? 0.3) }}
                />
              )}
            </div>
          ))}
        </div>

        <Divider label="✅ Validation auto" />

        <label style={checkLabel}>
          <input type="checkbox" checked={autoPatch} onChange={e => setAutoPatch(e.target.checked)} style={{ accentColor: 'var(--accent)' }} />
          🩹 PatchAgent auto
        </label>
        <label style={checkLabel}>
          <input type="checkbox" checked={autoTest} onChange={e => setAutoTest(e.target.checked)} style={{ accentColor: 'var(--accent)' }} />
          🧪 TestAgent auto
        </label>

        <Divider label="🎯 Mode" />

        <label style={checkLabel}>
          <input type="checkbox" checked={useWorkflow} onChange={e => setUseWorkflow(e.target.checked)} style={{ accentColor: 'var(--accent)' }} />
          🔄 Workflow LangGraph
        </label>

        <div style={{ marginTop: 'auto', paddingTop: 16 }}>
          <button
            onClick={() => { setResult(null); setSourceCode(''); setSourceFile(''); }}
            style={{ ...btnStyle, background: 'rgba(100,116,139,0.15)', color: 'var(--text-muted)', width: '100%', fontSize: '0.8rem' }}
          >
            🔄 Réinitialiser
          </button>
        </div>
      </aside>

      {/* ── Contenu principal ── */}
      <main style={{ flex: 1, padding: '32px 40px', overflowX: 'hidden', maxWidth: 'calc(100vw - 280px)' }}>

        {/* En-tête */}
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <h1 style={{
            fontSize: '2.2rem', fontWeight: 800,
            background: 'linear-gradient(135deg, var(--accent), var(--cyan))',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            marginBottom: 8, fontFamily: 'var(--display)',
          }}>
            ⚡ Agentic IA Refactoring Pro
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Système multi-agents avec LangGraph, validation automatique et contrôle de température.
          </p>
        </div>

        {/* Upload */}
        <Section title="📂 Source du code">
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <button onClick={() => fileInputRef.current?.click()} style={{ ...btnStyle, background: 'rgba(240,165,0,0.1)', border: '1px solid rgba(240,165,0,0.3)', color: 'var(--accent)' }}>
              📁 Charger un fichier
            </button>
            <button onClick={() => setExampleShown(!exampleShown)} style={{ ...btnStyle, background: 'rgba(100,116,139,0.1)', border: '1px solid var(--border)', color: 'var(--text)' }}>
              📝 {exampleShown ? 'Masquer' : 'Voir'} l'exemple
            </button>
            <button onClick={handleUseExample} style={{ ...btnStyle, background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', color: '#10b981' }}>
              📥 Utiliser l'exemple
            </button>
            <input ref={fileInputRef} type="file" accept=".py,.js,.ts,.java,.cpp,.c,.cs,.go,.rb,.rs,.php" onChange={handleFileUpload} style={{ display: 'none' }} />
          </div>

          {exampleShown && (
            <div style={{ marginTop: 12, background: '#0f172a', borderRadius: 8, padding: 16, border: '1px solid var(--border)', overflow: 'auto', maxHeight: 280 }}>
              <pre style={{ margin: 0, fontSize: '0.8rem', color: '#e2e8f0', fontFamily: 'var(--mono)', whiteSpace: 'pre' }}>{EXAMPLE_CODE}</pre>
            </div>
          )}
        </Section>

        {/* Code source */}
        {sourceCode && (
          <Section title={`📄 Code original — ${sourceFile} (${langName})`}>
            <div style={{ display: 'flex', gap: 16, marginBottom: 12 }}>
              <MetricBadge label="Lignes"     value={sourceCode.split('\n').length} />
              <MetricBadge label="Caractères" value={sourceCode.length} />
            </div>
            <CodeBlock code={sourceCode} language={langCode} maxHeight={300} />
          </Section>
        )}

        {/* Agents */}
        {availableAgents.length > 0 && (
          <Section title="🎯 Agents sélectionnés">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
              {availableAgents.map(agent => {
                const on   = agentEnabled[agent] ?? true;
                const temp = agentTemperatures[agent] ?? 0.3;
                const emoji = temp < 0.3 ? '🟦' : temp < 0.7 ? '🟨' : '🟥';
                return (
                  <button
                    key={agent}
                    onClick={() => toggleAgent(agent)}
                    style={{
                      padding: '8px 16px', borderRadius: 20, cursor: 'pointer',
                      fontSize: '0.82rem', fontFamily: 'var(--mono)',
                      transition: 'all 0.2s',
                      background: on ? 'rgba(240,165,0,0.15)' : 'rgba(100,116,139,0.08)',
                      border:     on ? '1px solid rgba(240,165,0,0.5)' : '1px solid var(--border)',
                      color:      on ? 'var(--accent)' : 'var(--text-muted)',
                    }}
                  >
                    {on ? emoji : '⬜'} {agent} {on ? `(🌡️ ${temp.toFixed(1)})` : ''}
                  </button>
                );
              })}
            </div>
            <div style={{ marginTop: 8, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {activeCount} agent{activeCount > 1 ? 's' : ''} actif{activeCount > 1 ? 's' : ''} — cliquez pour activer/désactiver
            </div>
          </Section>
        )}

        {/* Bouton lancement */}
        <Section title="🚀 Exécution">
          <button
            onClick={handleRun}
            disabled={running || !sourceCode}
            style={{
              width: '100%', padding: '14px 24px', borderRadius: 10,
              fontSize: '1rem', fontWeight: 700, cursor: running ? 'not-allowed' : 'pointer',
              background: running ? 'rgba(240,165,0,0.3)' : 'linear-gradient(135deg, var(--accent), var(--cyan))',
              color: running ? 'var(--text-muted)' : '#07090c',
              border: 'none', transition: 'all 0.2s', fontFamily: 'var(--mono)',
              opacity: !sourceCode ? 0.5 : 1,
            }}
          >
            {running ? `⏳ ${statusMsg || 'Refactoring en cours…'}` : '⚡ LANCER LE REFACTORING COMPLET'}
          </button>

          {running && (
            <div style={{ marginTop: 12 }}>
              <div style={{ background: 'var(--border)', borderRadius: 4, height: 6, overflow: 'hidden' }}>
                <div style={{
                  height: '100%', borderRadius: 4,
                  background: 'linear-gradient(90deg, var(--accent), var(--cyan))',
                  width: `${progress}%`,
                  transition: 'width 0.5s ease',
                }} />
              </div>
              <div style={{ marginTop: 6, fontSize: '0.8rem', color: 'var(--text-muted)' }}>{statusMsg}</div>
            </div>
          )}
        </Section>

        {/* ── Résultats ── */}
        {result && (
          <>
            {/* Bannière succès */}
            <div style={{
              padding: '14px 20px', borderRadius: 10, marginBottom: 24,
              background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)',
              color: '#10b981', display: 'flex', alignItems: 'center', gap: 12,
            }}>
              <span style={{ fontSize: '1.2rem' }}>✅</span>
              <div>
                <strong>Refactoring terminé en {formatDuration(result.report.totd)}</strong>
                <span style={{ marginLeft: 12, opacity: 0.7, fontSize: '0.85rem' }}>Mode : {result.report.mode}</span>
              </div>
            </div>

            {/* Tableau performances */}
            <Section title="📊 Rapport de performances">
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border)' }}>
                      {['Agent', '🌡️ Temp', '🔍 Problèmes', '⏱️ Durée', '📝'].map(h => (
                        <th key={h} style={{ textAlign: 'left', padding: '8px 12px', color: 'var(--text-muted)', fontWeight: 500 }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.report.rr.map((r, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid rgba(100,116,139,0.1)' }}>
                        <td style={tdStyle}>{r.name}</td>
                        <td style={tdStyle}>{String(r.temperature_used)}</td>
                        <td style={tdStyle}>{r.analysis?.length ?? 0}</td>
                        <td style={tdStyle}>{formatDuration(r.execution_time ?? 0)}</td>
                        <td style={tdStyle}>{r.analysis?.length ? '✅' : '⚪'}</td>
                      </tr>
                    ))}
                    {result.report.pr && (
                      <tr style={{ borderBottom: '1px solid rgba(100,116,139,0.1)' }}>
                        <td style={tdStyle}>PatchAgent</td>
                        <td style={tdStyle}>N/A</td>
                        <td style={tdStyle}>{result.report.pr.analysis?.length ?? 0}</td>
                        <td style={tdStyle}>{formatDuration(result.report.pr.execution_time ?? 0)}</td>
                        <td style={tdStyle}>✅</td>
                      </tr>
                    )}
                    {result.report.tr && (
                      <tr>
                        <td style={tdStyle}>TestAgent</td>
                        <td style={tdStyle}>N/A</td>
                        <td style={tdStyle}>{result.report.tr.status}</td>
                        <td style={tdStyle}>{formatDuration(result.report.tr.execution_time ?? 0)}</td>
                        <td style={tdStyle}>{result.report.tr.status === 'SUCCESS' ? '✅' : '❌'}</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* Métriques résumé */}
              <div style={{ display: 'flex', gap: 16, marginTop: 16, flexWrap: 'wrap' }}>
                {[
                  { label: '⏱️ Moyen/agent', value: formatDuration(result.report.rr.reduce((s, r) => s + (r.execution_time ?? 0), 0) / Math.max(result.report.rr.length, 1)) },
                  { label: '🔄 Fusion',      value: formatDuration(result.report.merd) },
                  { label: '⏱️ Total',       value: formatDuration(result.report.totd) },
                ].map(m => (
                  <div key={m.label} style={{ flex: 1, minWidth: 120, background: 'rgba(100,116,139,0.08)', border: '1px solid var(--border)', borderRadius: 8, padding: '10px 14px' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{m.label}</div>
                    <div style={{ fontWeight: 700, color: 'var(--accent)', fontSize: '1.1rem', marginTop: 4 }}>{m.value}</div>
                  </div>
                ))}
              </div>
            </Section>

            {/* Détails agents */}
            <Section title="📈 Résultats détaillés">
              {result.report.rr.map((r, i) => {
                const key = r.name + i;
                const open = expandedAgents.has(key);
                return (
                  <div key={key} style={{ marginBottom: 8, border: '1px solid var(--border)', borderRadius: 8, overflow: 'hidden' }}>
                    <button
                      onClick={() => setExpandedAgents(prev => {
                        const next = new Set(prev);
                        open ? next.delete(key) : next.add(key);
                        return next;
                      })}
                      style={{ width: '100%', textAlign: 'left', padding: '12px 16px', background: 'var(--surface)', border: 'none', cursor: 'pointer', color: 'var(--text)', fontFamily: 'var(--mono)', fontSize: '0.85rem', display: 'flex', justifyContent: 'space-between' }}
                    >
                      <span>{r.name} — 🌡️ {String(r.temperature_used)} | ⏱️ {formatDuration(r.execution_time ?? 0)}</span>
                      <span>{open ? '▲' : '▼'}</span>
                    </button>
                    {open && (
                      <div style={{ padding: 16, background: 'rgba(15,23,42,0.5)' }}>
                        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                          <Tab label="📋 Analyse" />
                        </div>
                        {r.analysis?.length ? (
                          r.analysis.map((iss, j) => (
                            <div key={j} style={{ background: '#0f172a', padding: '8px 12px', borderRadius: 6, marginBottom: 6, fontFamily: 'var(--mono)', fontSize: '0.8rem', color: '#e2e8f0' }}>
                              {String(iss)}
                            </div>
                          ))
                        ) : (
                          <InfoBox>Aucun problème détecté</InfoBox>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}

              {/* PatchAgent */}
              {result.report.pr && (
                <div style={{ marginTop: 16, padding: 16, background: 'rgba(240,165,0,0.05)', border: '1px solid rgba(240,165,0,0.2)', borderRadius: 8 }}>
                  <h3 style={{ margin: '0 0 12px', fontSize: '0.9rem', color: 'var(--accent)' }}>
                    🩹 PatchAgent — ⏱️ {formatDuration(result.report.pr.execution_time ?? 0)}
                  </h3>
                  {result.report.pr.analysis?.map((note, i) => (
                    <div key={i} style={{ background: '#0D0E29', color: '#e2e8f0', padding: '6px 10px', borderRadius: 4, marginBottom: 4, fontSize: '0.8rem' }}>
                      {typeof note === 'object' ? note.note : String(note)}
                    </div>
                  ))}
                  {result.report.pr.changes_applied?.map((ch, i) => (
                    <div key={i} style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>• {ch}</div>
                  ))}
                </div>
              )}

              {/* TestAgent */}
              {result.report.tr && (
                <div style={{ marginTop: 16, padding: 16, background: result.report.tr.status === 'SUCCESS' ? 'rgba(16,185,129,0.05)' : 'rgba(239,68,68,0.05)', border: `1px solid ${result.report.tr.status === 'SUCCESS' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`, borderRadius: 8 }}>
                  <h3 style={{ margin: '0 0 8px', fontSize: '0.9rem', color: result.report.tr.status === 'SUCCESS' ? '#10b981' : '#ef4444' }}>
                    🧪 TestAgent — {result.report.tr.status === 'SUCCESS' ? '✅' : '❌'} {result.report.tr.status}
                  </h3>
                  {result.report.tr.summary?.map((s, i) => <div key={i} style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 2 }}>• {s}</div>)}
                </div>
              )}
            </Section>

            {/* Code final */}
            <Section title="📝 Code final refactoré">
              <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
                <button onClick={handleDownload} style={{ ...btnStyle, background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.3)', color: '#60a5fa' }}>
                  ⬇️ Télécharger
                </button>
                <button onClick={handleCopy} style={{ ...btnStyle, background: copied ? 'rgba(16,185,129,0.2)' : 'rgba(100,116,139,0.1)', border: copied ? '1px solid rgba(16,185,129,0.4)' : '1px solid var(--border)', color: copied ? '#10b981' : 'var(--text)' }}>
                  {copied ? '✅ Copié !' : '📋 Copier'}
                </button>
              </div>
              <CodeBlock code={result.refactored_code} language={langCode} maxHeight={400} />
            </Section>

            {/* Diff */}
            <Section title="🔍 Différences">
              <label style={{ ...checkLabel, marginBottom: 12 }}>
                <input
                  type="checkbox"
                  checked={showDiff}
                  onChange={e => setShowDiff(e.target.checked)}
                  style={{ accentColor: 'var(--accent)' }}
                />
                Afficher les différences (original ↔ refactoré)
              </label>

              {showDiff && (() => {
                const diffText = buildDiff(result.original_code, result.refactored_code);
                const lines    = diffText.split('\n');
                const added    = lines.filter(l => l.startsWith('+')).length;
                const removed  = lines.filter(l => l.startsWith('-')).length;

                return (
                  <>
                    <div style={{ display: 'flex', gap: 12, marginBottom: 12, flexWrap: 'wrap' }}>
                      {[
                        { label: '➕ Ajoutées',   value: added,           color: '#86efac' },
                        { label: '➖ Supprimées', value: removed,          color: '#fca5a5' },
                        { label: '📊 Delta',      value: added - removed,  color: '#7dd3fc' },
                      ].map(m => (
                        <div key={m.label} style={{ background: 'rgba(100,116,139,0.08)', border: '1px solid var(--border)', borderRadius: 6, padding: '6px 12px' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{m.label}</div>
                          <div style={{ fontWeight: 700, color: m.color }}>{m.value > 0 ? `+${m.value}` : m.value}</div>
                        </div>
                      ))}
                    </div>

                    {/* Légende */}
                    <div style={{ display: 'flex', gap: 10, marginBottom: 10, flexWrap: 'wrap' }}>
                      {[
                        { bg: '#14532d', color: '#86efac', label: '＋ Ligne ajoutée' },
                        { bg: '#7f1d1d', color: '#fca5a5', label: '－ Ligne supprimée' },
                        { bg: '#0f172a', color: '#94a3b8', label: '  Inchangée' },
                      ].map(l => (
                        <span key={l.label} style={{ background: l.bg, color: l.color, padding: '3px 12px', borderRadius: 4, fontSize: '0.75rem' }}>{l.label}</span>
                      ))}
                    </div>

                    <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, overflow: 'auto', maxHeight: 520 }}>
                      {lines.map((line, i) => {
                        const isAdd = line.startsWith('+ ');
                        const isDel = line.startsWith('- ');
                        return (
                          <div key={i} style={{
                            fontFamily: 'var(--mono)', fontSize: '0.78rem', padding: '2px 12px',
                            background: isAdd ? '#14532d' : isDel ? '#7f1d1d' : '#0f172a',
                            color:      isAdd ? '#86efac' : isDel ? '#fca5a5' : '#cbd5e1',
                            whiteSpace: 'pre',
                          }}>
                            {line}
                          </div>
                        );
                      })}
                    </div>
                  </>
                );
              })()}
            </Section>
          </>
        )}
      </main>
    </div>
  );
}

// ── Sous-composants ───────────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ marginBottom: 28 }}>
      <h2 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-bright)', marginBottom: 14, fontFamily: 'var(--mono)', display: 'flex', alignItems: 'center', gap: 8 }}>
        {title}
      </h2>
      {children}
    </section>
  );
}

function Divider({ label }: { label: string }) {
  return (
    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.05em', marginTop: 4, marginBottom: -4, paddingBottom: 4, borderBottom: '1px solid var(--border)' }}>
      {label}
    </div>
  );
}

function MetricBadge({ label, value }: { label: string; value: number }) {
  return (
    <div style={{ background: 'rgba(100,116,139,0.1)', border: '1px solid var(--border)', borderRadius: 6, padding: '4px 12px', fontSize: '0.78rem' }}>
      <span style={{ color: 'var(--text-muted)' }}>{label}: </span>
      <span style={{ color: 'var(--accent)', fontWeight: 600 }}>{value}</span>
    </div>
  );
}

function InfoBox({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ padding: '10px 14px', borderRadius: 6, background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.2)', color: '#60a5fa', fontSize: '0.82rem' }}>
      ℹ️ {children}
    </div>
  );
}

function Tab({ label }: { label: string }) {
  return (
    <span style={{ fontSize: '0.78rem', color: 'var(--accent)', background: 'rgba(240,165,0,0.1)', padding: '3px 10px', borderRadius: 4 }}>{label}</span>
  );
}

function CodeBlock({ code, language, maxHeight = 400 }: { code: string; language: string; maxHeight?: number }) {
  return (
    <div style={{ background: '#0f172a', borderRadius: 8, border: '1px solid #1e293b', overflow: 'auto', maxHeight, position: 'relative' }}>
      <div style={{ position: 'absolute', top: 8, right: 12, fontSize: '0.68rem', color: '#475569', fontFamily: 'var(--mono)' }}>{language}</div>
      <pre style={{ margin: 0, padding: '16px 16px 16px 16px', fontFamily: 'var(--mono)', fontSize: '0.8rem', color: '#e2e8f0', whiteSpace: 'pre', overflowX: 'auto', lineHeight: 1.6 }}>
        {code}
      </pre>
    </div>
  );
}

// ── Styles inline réutilisables ───────────────────────────────────────────────

const btnStyle: React.CSSProperties = {
  padding: '8px 16px', borderRadius: 8, cursor: 'pointer',
  fontSize: '0.82rem', fontFamily: 'var(--mono)',
  border: 'none', transition: 'all 0.2s', fontWeight: 500,
};

const selectStyle: React.CSSProperties = {
  width: '100%', padding: '8px 10px', borderRadius: 6,
  background: 'var(--surface)', border: '1px solid var(--border)',
  color: 'var(--text)', fontFamily: 'var(--mono)', fontSize: '0.82rem',
  cursor: 'pointer',
};

const checkLabel: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: 8,
  cursor: 'pointer', fontSize: '0.82rem', color: 'var(--text)',
};

const tdStyle: React.CSSProperties = {
  padding: '8px 12px', color: 'var(--text)', fontSize: '0.82rem',
};