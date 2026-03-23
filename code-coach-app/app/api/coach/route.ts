import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

const OLLAMA_URL = process.env.OLLAMA_URL ?? 'http://localhost:11434'
const OLLAMA_MODEL = process.env.OLLAMA_MODEL ?? 'qwen2.5-coder:latest'

const SYSTEM_PROMPT = (lang: string) => `You are CodeCoach, a senior ${lang} engineer and tutor.

The developer gives you a problem in plain text.
Your job is to produce a helpful, concrete, and pedagogical answer based FIRST on the user's specific problem.

You must:
- understand the exact problem described by the user
- infer the most suitable approach for that specific case
- explain the reasoning clearly
- give useful ${lang} syntax patterns when relevant
- explain the logic step by step
- mention complexity when relevant
- warn about common mistakes
- stay practical, not generic

Do NOT just name a concept.
Do NOT give a vague answer.
Do NOT give a full copy-paste final solution unless explicitly required.

Adapt to the problem type:
- algorithm / data structure
- debugging
- backend / API
- frontend / UI
- database / SQL
- architecture / design
- language-specific implementation

Respond ONLY in this markdown structure:

## Best approach
State the most appropriate solution for the user's exact problem and why it fits.

## Explanation
Explain clearly how it works.
Focus on the mechanism, not only the name.

## Useful ${lang} syntax and patterns
Give 3-5 short syntax hints, idioms, or implementation patterns relevant to this exact problem.
Do not give a full solution.

## Step-by-step logic
Explain the implementation flow in 4-6 concrete steps.

## Example or mental model
Give a very small example, scenario, or mental model to make the idea easy to understand.

## Complexity / tradeoffs
If relevant, give time and space complexity.
Otherwise, explain performance or design tradeoffs.

## Pitfalls to avoid
Give 2-4 common mistakes specific to this problem or to ${lang}.

Rules:
- Answer in the SAME language the user wrote in
- Be direct, concrete, and pedagogical
- Base the answer on the user's problem, not on generic theory
- No full final code
- Short syntax snippets are allowed
- Prefer explanation + implementation guidance over abstract discussion
- Total response: around 220-350 words`

function runPythonRag(problem: string, language: string): Promise<any> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(process.cwd(), 'rag', 'run_query.py')
    const py = spawn('python', [scriptPath, problem, language], {
      cwd: process.cwd(),
    })

    let stdout = ''
    let stderr = ''

    py.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    py.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    py.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(stderr || `Python exited with code ${code}`))
        return
      }

      try {
        const parsed = JSON.parse(stdout)
        resolve(parsed)
      } catch (err) {
        reject(new Error(`Invalid JSON from Python: ${stdout}`))
      }
    })
  })
}

export async function POST(req: NextRequest) {
  try {
    const { language, problem } = await req.json()

    if (!language || !problem) {
      return NextResponse.json(
        { error: 'Missing language or problem' },
        { status: 400 }
      )
    }

    // 1) Query RAG
    const ragResult = await runPythonRag(problem, language)

    const context = ragResult?.context ?? ''
    const sources = ragResult?.sources ?? []
    const hasContext = ragResult?.has_context ?? false

    // 2) Build final user message with RAG context
    const userPrompt = `Language: ${language}
Problem: ${problem}

Retrieved context:
${context || 'No relevant context found.'}`

    // 3) Ask Ollama
    const response = await fetch(`${OLLAMA_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: OLLAMA_MODEL,
        stream: false,
        options: {
          num_predict: 400,
          temperature: 0.3,
          top_p: 0.9,
          repeat_penalty: 1.1,
          num_ctx: 4096,
        },
        messages: [
          {
            role: 'system',
            content: SYSTEM_PROMPT(language),
          },
          {
            role: 'user',
            content: userPrompt,
          },
        ],
      }),
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      return NextResponse.json(
        {
          error:
            (err as any)?.error?.message ??
            `Ollama error ${response.status} — is Ollama running?`,
        },
        { status: 500 }
      )
    }

    const data = await response.json()
    const text: string = data?.choices?.[0]?.message?.content ?? ''

    if (!text) {
      return NextResponse.json(
        { error: 'Empty response from Ollama' },
        { status: 500 }
      )
    }

    return NextResponse.json({
      advice: text,
      usage: data?.usage ?? null,
      sources,
      hasContext,
    })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}