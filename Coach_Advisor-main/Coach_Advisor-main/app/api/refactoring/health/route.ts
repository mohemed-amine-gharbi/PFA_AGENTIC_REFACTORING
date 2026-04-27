import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.REFACTORING_API_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 2000);

    const response = await fetch(`${API_BASE_URL}/api/health`, {
      signal: controller.signal,
      cache: 'no-store',
    });
    clearTimeout(timer);

    const data = await response.json();
    return NextResponse.json({ ...data, backend_reachable: true, mode: 'python_backend' });
  } catch {
    return NextResponse.json({
      status: 'ok',
      backend_reachable: false,
      mode: 'nextjs_standalone',
      agents_count: 5,
    });
  }
}