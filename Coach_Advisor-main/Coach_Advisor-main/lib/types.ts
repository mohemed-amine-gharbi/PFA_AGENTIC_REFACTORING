export interface HistoryEntry {
  id: string
  language: string
  problem: string
  advice: string
  timestamp: Date
}

export const LANGUAGES = [
  { key: 'Python',     emoji: '🐍' },
  { key: 'JavaScript', emoji: '🌐' },
  { key: 'TypeScript', emoji: '🔷' },
  { key: 'Java',       emoji: '☕' },
  { key: 'C++',        emoji: '⚙️' },
  { key: 'C',          emoji: '🔩' },
  { key: 'C#',         emoji: '🎯' },
  { key: 'Go',         emoji: '🐹' },
  { key: 'Ruby',       emoji: '💎' },
  { key: 'Rust',       emoji: '🦀' },
  { key: 'PHP',        emoji: '🐘' },
] as const

export type Language = typeof LANGUAGES[number]['key']
