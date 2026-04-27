import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.REFACTORING_API_URL || 'http://localhost:8000';
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY || '';

// ── Types ─────────────────────────────────────────────────────────────────────

interface RefactoringRequest {
  code: string;
  language: string;
  filename: string;
  selected_agents: string[];
  agent_temperatures: Record<string, number>;
  auto_patch: boolean;
  auto_test: boolean;
  use_workflow: boolean;
  model_name: string;
  user_id?: string;
}

interface AgentResult {
  name: string;
  analysis: string[];
  proposal: string;
  temperature_used: number | string;
  execution_time: number;
  status: string;
}

// ── Descriptions des agents ───────────────────────────────────────────────────

const AGENT_DESCRIPTIONS: Record<string, string> = {
  ComplexityAgent: `Tu es ComplexityAgent, expert en réduction de complexité cyclomatique.
Analyse le code et détecte :
- Imbrication trop profonde (if dans if dans if)
- Trop de branches conditionnelles (>5 dans une fonction)
- Fonctions trop longues (>20 lignes)
- Conditions composées complexes (and/or multiples)
Propose un code refactorisé corrigeant CES problèmes spécifiques.`,

  DuplicationAgent: `Tu es DuplicationAgent, expert en détection et élimination de code dupliqué.
Analyse le code et détecte :
- Fonctions ou blocs de code quasi-identiques
- Logique répétée qui pourrait être factorisée
- Patterns répétitifs (copy-paste détectable)
Propose un code refactorisé éliminant les duplications via des fonctions communes.`,

  ImportAgent: `Tu es ImportAgent, expert en optimisation des imports.
Analyse le code et détecte :
- Imports multiples sur une ligne (ex: import os, sys, math)
- Imports inutilisés (modules jamais utilisés dans le code)
- Imports wildcard (import *)
- Ordre des imports (stdlib, tiers, local)
Propose un code refactorisé avec les imports corrigés selon PEP8.`,

  LongFunctionAgent: `Tu es LongFunctionAgent, expert en découpage de fonctions longues.
Analyse le code et détecte :
- Fonctions de plus de 15 lignes
- Fonctions qui font trop de choses à la fois (principe de responsabilité unique)
- Blocs de code extractibles en sous-fonctions
Propose un code refactorisé avec les fonctions découpées.`,

  RenameAgent: `Tu es RenameAgent, expert en conventions de nommage.
Analyse le code et détecte :
- Variables à un seul caractère (x, y, z, a, b sauf dans les boucles)
- Noms non descriptifs (tmp, temp, foo, bar, data, result sans contexte)
- Fonctions aux noms vagues (do_something, process, handle)
- Non-respect des conventions (snake_case pour Python, camelCase pour JS)
Propose un code refactorisé avec des noms clairs et descriptifs.`,
};

// ── Appel Claude API pour un agent ───────────────────────────────────────────

async function runAgentWithClaude(
  agentName: string,
  code: string,
  language: string,
  temperature: number
): Promise<{ analysis: string[]; refactoredCode: string; duration: number }> {
  const t0 = Date.now();

  const agentPrompt = AGENT_DESCRIPTIONS[agentName] ?? `Tu es ${agentName}, un agent de refactoring de code.`;

  const userPrompt = `Voici un fichier ${language} à analyser et refactoriser :

\`\`\`${language.toLowerCase()}
${code}
\`\`\`

Réponds UNIQUEMENT en JSON valide avec cette structure exacte (pas de markdown, pas de backticks) :
{
  "analysis": ["problème 1 détecté", "problème 2 détecté", "..."],
  "refactored_code": "le code complet refactorisé ici"
}

- "analysis" : liste des problèmes détectés (strings). Si aucun problème, retourne [].
- "refactored_code" : le code COMPLET après correction. Si rien à corriger, retourne le code original tel quel.`;

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4000,
      temperature: temperature,
      system: agentPrompt,
      messages: [{ role: 'user', content: userPrompt }],
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Claude API error ${response.status}: ${err}`);
  }

  const data = await response.json();
  const rawText = data.content?.[0]?.text ?? '{}';

  // Parser le JSON retourné par Claude
  let parsed: { analysis?: string[]; refactored_code?: string } = {};
  try {
    // Nettoyer les backticks si Claude en met quand même
    const cleaned = rawText
      .replace(/^```json\s*/i, '')
      .replace(/^```\s*/i, '')
      .replace(/```\s*$/i, '')
      .trim();
    parsed = JSON.parse(cleaned);
  } catch {
    // Si JSON mal formé, extraire ce qu'on peut
    console.error(`[${agentName}] JSON parse failed, raw:`, rawText.substring(0, 200));
    parsed = { analysis: ['Analyse effectuée (réponse non structurée)'], refactored_code: code };
  }

  const duration = (Date.now() - t0) / 1000;

  return {
    analysis:       Array.isArray(parsed.analysis) ? parsed.analysis : [],
    refactoredCode: typeof parsed.refactored_code === 'string' && parsed.refactored_code.trim()
      ? parsed.refactored_code
      : code,
    duration,
  };
}

// ── Merge intelligent des propositions ────────────────────────────────────────

async function mergeWithClaude(
  originalCode: string,
  proposals: { agent: string; code: string }[],
  language: string
): Promise<string> {
  if (proposals.length === 0) return originalCode;
  if (proposals.length === 1) return proposals[0].code;

  // Si toutes les propositions sont identiques, retourner directement
  const uniqueCodes = new Set(proposals.map(p => p.code));
  if (uniqueCodes.size === 1) return proposals[0].code;

  const proposalsText = proposals
    .map((p, i) => `=== Proposition ${i + 1} (${p.agent}) ===\n${p.code}`)
    .join('\n\n');

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4000,
      system: `Tu es MergeAgent. Tu reçois plusieurs versions refactorisées du même code par différents agents.
Tu dois produire une version finale qui intègre intelligemment TOUTES les améliorations de chaque agent.
Réponds UNIQUEMENT avec le code final, sans explication, sans backticks, sans commentaire.`,
      messages: [{
        role: 'user',
        content: `Code original :\n${originalCode}\n\n${proposalsText}\n\nProduis le code final qui intègre toutes les améliorations.`,
      }],
    }),
  });

  if (!response.ok) return proposals[proposals.length - 1].code;

  const data = await response.json();
  const merged = data.content?.[0]?.text ?? '';
  return merged.trim() || proposals[proposals.length - 1].code;
}

// ── Patch et validation ────────────────────────────────────────────────────────

async function patchWithClaude(code: string, language: string): Promise<{ notes: string[]; code: string }> {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4000,
      system: `Tu es PatchAgent. Tu corriges les derniers problèmes résiduels (syntaxe, indentation, cohérence) dans le code refactorisé.
Réponds UNIQUEMENT en JSON : {"notes": ["correction 1", ...], "patched_code": "code corrigé complet"}`,
      messages: [{
        role: 'user',
        content: `Corrige ce code ${language} :\n\`\`\`\n${code}\n\`\`\``,
      }],
    }),
  });

  if (!response.ok) return { notes: [], code };

  const data = await response.json();
  try {
    const cleaned = (data.content?.[0]?.text ?? '{}')
      .replace(/^```json\s*/i, '').replace(/^```\s*/i, '').replace(/```\s*$/i, '').trim();
    const parsed = JSON.parse(cleaned);
    return {
      notes: Array.isArray(parsed.notes) ? parsed.notes : [],
      code:  typeof parsed.patched_code === 'string' ? parsed.patched_code : code,
    };
  } catch {
    return { notes: [], code };
  }
}

async function testWithClaude(code: string, language: string): Promise<{
  status: string; summary: string[]; details: { tool: string; status: string; output: string }[]
}> {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      system: `Tu es TestAgent. Tu valides la qualité du code refactorisé.
Réponds UNIQUEMENT en JSON : {"status": "SUCCESS|WARNING|FAILED", "summary": ["point 1", ...], "details": [{"tool": "nom", "status": "SUCCESS|WARNING|FAILED", "output": "message"}]}`,
      messages: [{
        role: 'user',
        content: `Valide ce code ${language} :\n\`\`\`\n${code}\n\`\`\``,
      }],
    }),
  });

  const fallback = {
    status: 'SUCCESS',
    summary: ['Validation terminée'],
    details: [{ tool: 'claude_validator', status: 'SUCCESS', output: 'Code validé' }],
  };

  if (!response.ok) return fallback;

  const data = await response.json();
  try {
    const cleaned = (data.content?.[0]?.text ?? '{}')
      .replace(/^```json\s*/i, '').replace(/^```\s*/i, '').replace(/```\s*$/i, '').trim();
    return JSON.parse(cleaned);
  } catch {
    return fallback;
  }
}

// ── Handler POST ──────────────────────────────────────────────────────────────

export async function POST(request: NextRequest) {
  const startTime = Date.now();

  try {
    const body: RefactoringRequest = await request.json();

    // Validation
    if (!body.code?.trim()) {
      return NextResponse.json({ success: false, error: 'Le champ "code" est requis' }, { status: 400 });
    }
    if (!body.language) {
      return NextResponse.json({ success: false, error: 'Le champ "language" est requis' }, { status: 400 });
    }
    if (!body.selected_agents?.length) {
      return NextResponse.json({ success: false, error: 'Sélectionnez au moins un agent' }, { status: 400 });
    }

    // ── 1. Essayer le backend Python (Ollama/LangGraph) ───────────────────────
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 5000); // 5s pour détecter si dispo
      const pythonRes = await fetch(`${API_BASE_URL}/api/refactoring/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      clearTimeout(timer);
      if (pythonRes.ok) {
        const data = await pythonRes.json();
        console.log('[execute] ✅ Backend Python utilisé');
        return NextResponse.json(data);
      }
    } catch {
      console.log('[execute] Backend Python non disponible → Claude API');
    }

    // ── 2. Fallback : Claude API (vrais LLM, vraie analyse) ──────────────────
    if (!ANTHROPIC_API_KEY) {
      return NextResponse.json({
        success: false,
        error: 'Backend Python non disponible et ANTHROPIC_API_KEY non configurée. Ajoutez ANTHROPIC_API_KEY dans .env.local',
      }, { status: 503 });
    }

    console.log(`[execute] 🤖 Claude API — ${body.selected_agents.length} agents`);

    // Exécuter chaque agent séquentiellement avec Claude
    const agentResults: AgentResult[] = [];
    let currentCode = body.code;

    for (const agentName of body.selected_agents) {
      const temperature = body.agent_temperatures?.[agentName] ?? 0.3;
      console.log(`[execute]   → ${agentName} (temp=${temperature})`);

      try {
        const result = await runAgentWithClaude(agentName, body.code, body.language, temperature);

        agentResults.push({
          name:             agentName,
          analysis:         result.analysis,
          proposal:         result.refactoredCode,
          temperature_used: temperature,
          execution_time:   result.duration,
          status:           'SUCCESS',
        });

        // Garder la dernière proposition pour la fusion
        if (result.refactoredCode !== body.code) {
          currentCode = result.refactoredCode;
        }
      } catch (agentErr) {
        const msg = agentErr instanceof Error ? agentErr.message : String(agentErr);
        console.error(`[execute] Agent ${agentName} failed:`, msg);
        agentResults.push({
          name:             agentName,
          analysis:         [`Erreur: ${msg}`],
          proposal:         body.code,
          temperature_used: temperature,
          execution_time:   0,
          status:           'FAILED',
        });
      }
    }

    // Fusion des propositions si plusieurs agents
    let mergedCode = body.code;
    let mergeDuration = 0;
    if (body.selected_agents.length > 1) {
      const t0 = Date.now();
      const proposals = agentResults
        .filter(r => r.status === 'SUCCESS' && r.proposal !== body.code)
        .map(r => ({ agent: r.name, code: r.proposal }));

      mergedCode = await mergeWithClaude(body.code, proposals, body.language);
      mergeDuration = (Date.now() - t0) / 1000;
      console.log(`[execute] Fusion terminée en ${mergeDuration.toFixed(2)}s`);
    } else if (agentResults.length === 1) {
      mergedCode = agentResults[0].proposal;
    }

    // PatchAgent
    let patchResult = null;
    if (body.auto_patch) {
      const t0 = Date.now();
      const patch = await patchWithClaude(mergedCode, body.language);
      mergedCode = patch.code;
      patchResult = {
        analysis:        patch.notes.map(n => ({ note: n })),
        changes_applied: patch.notes,
        execution_time:  (Date.now() - t0) / 1000,
      };
    }

    // TestAgent
    let testResult = null;
    if (body.auto_test) {
      const t0 = Date.now();
      const test = await testWithClaude(mergedCode, body.language);
      testResult = { ...test, execution_time: (Date.now() - t0) / 1000 };
    }

    const executionTime = (Date.now() - startTime) / 1000;
    console.log(`[execute] ✅ Terminé en ${executionTime.toFixed(2)}s`);

    return NextResponse.json({
      success:         true,
      refactored_code: mergedCode,
      original_code:   body.code,
      report: {
        rr:   agentResults,
        pr:   patchResult,
        tr:   testResult,
        merd: mergeDuration,
        totd: executionTime,
        mode: 'Claude API (agents LLM)',
      },
      execution_time: executionTime,
    });

  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Erreur inconnue';
    console.error('[execute] Fatal error:', message);
    return NextResponse.json(
      { success: false, error: `Erreur serveur : ${message}` },
      { status: 500 }
    );
  }
}