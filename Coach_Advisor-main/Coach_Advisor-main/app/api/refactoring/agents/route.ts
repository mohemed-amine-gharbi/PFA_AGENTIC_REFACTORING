import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.REFACTORING_API_URL || 'http://localhost:8000';

const DEFAULT_AGENTS = [
  'ComplexityAgent',
  'DuplicationAgent',
  'ImportAgent',
  'LongFunctionAgent',
  'RenameAgent',
];

export async function GET() {
  // Essayer le backend Python
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 2000);

    const response = await fetch(`${API_BASE_URL}/api/agents`, {
      signal: controller.signal,
      cache: 'no-store',
    });
    clearTimeout(timer);

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();

    const agents: string[] = (data.agents ?? []).map((a: unknown) =>
      typeof a === 'string' ? a : typeof a === 'object' && a && 'name' in a ? String((a as { name: unknown }).name) : String(a)
    );

    return NextResponse.json({ success: true, agents, source: 'python_backend' });
  } catch {
    // Fallback statique — toujours fonctionnel
    return NextResponse.json({ success: true, agents: DEFAULT_AGENTS, source: 'static_fallback' });
  }
}