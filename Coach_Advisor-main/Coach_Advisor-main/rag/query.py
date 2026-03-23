"""
╔══════════════════════════════════════════════════════════════╗
║  CodeCoach RAG — query.py                                    ║
║  Recherche les chunks pertinents dans ChromaDB               ║
║  et construit le contexte pour Qwen2.5-Coder                 ║
║                                                              ║
║  Usage (test rapide depuis le terminal) :                    ║
║    python rag/query.py "comment trier une liste en Python"   ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import urllib.request
from pathlib import Path

import chromadb
from chromadb.config import Settings

# ── Configuration ─────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
CHROMA_DIR  = BASE_DIR / "chroma_db"
COLLECTION  = "codecoach_docs"
EMBED_MODEL = "nomic-embed-text"
OLLAMA_URL  = os.getenv("OLLAMA_URL", "http://localhost:11434")

TOP_K            = 5      # Nombre de chunks à récupérer
MIN_SCORE        = 0.30   # Score de similarité minimum (0 à 1)
MAX_CONTEXT_CHARS = 3000  # Limite du contexte injecté dans le prompt

# ── Couleurs terminal ──────────────────────────────────────────
GREEN = "\033[92m"
AMBER = "\033[93m"
CYAN  = "\033[96m"
GRAY  = "\033[90m"
RESET = "\033[0m"
BOLD  = "\033[1m"

# ── Embedding de la question ───────────────────────────────────
def embed_query(text: str) -> list[float]:
    payload = json.dumps({
        "model": EMBED_MODEL,
        "input": text,
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        return data["embeddings"][0]

# ── Recherche dans ChromaDB ────────────────────────────────────
def search(query: str, top_k: int = TOP_K, min_score: float = MIN_SCORE) -> list[dict]:
    """
    Cherche les chunks les plus similaires à la question.
    Retourne une liste triée par pertinence.
    """
    if not CHROMA_DIR.exists():
        return []

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )

    try:
        collection = client.get_collection(COLLECTION)
    except Exception:
        return []  # Collection vide ou inexistante

    if collection.count() == 0:
        return []

    # Embedding de la question
    query_embedding = embed_query(query)

    # Recherche par similarité cosinus
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        distance = results["distances"][0][i]
        # ChromaDB avec cosine retourne une distance (0=identique, 2=opposé)
        # On convertit en score de similarité (0 à 1)
        score = 1 - (distance / 2)

        if score >= min_score:
            chunks.append({
                "text":     doc,
                "score":    round(score, 3),
                "source":   results["metadatas"][0][i].get("source", "inconnu"),
                "type":     results["metadatas"][0][i].get("file_type", "text"),
                "chunk_idx": results["metadatas"][0][i].get("chunk_index", 0),
            })

    # Trier par score décroissant
    chunks.sort(key=lambda x: x["score"], reverse=True)
    return chunks

# ── Construction du contexte ───────────────────────────────────
def build_context(chunks: list[dict], max_chars: int = MAX_CONTEXT_CHARS) -> str:
    """
    Assemble les chunks en un bloc de contexte pour le prompt.
    Respecte la limite de caractères pour ne pas surcharger le LLM.
    """
    if not chunks:
        return ""

    parts = []
    total = 0

    for chunk in chunks:
        header = f"[Source: {chunk['source']} | Score: {chunk['score']}]\n"
        block  = f"{header}{chunk['text']}\n"

        if total + len(block) > max_chars:
            break

        parts.append(block)
        total += len(block)

    return "\n---\n".join(parts)

# ── Prompt RAG complet ─────────────────────────────────────────
def build_rag_prompt(question: str, context: str, language: str = "") -> str:
    """
    Construit le prompt augmenté avec le contexte récupéré.
    """
    lang_hint = f" en {language}" if language else ""

    if not context:
        # Pas de contexte RAG — fallback sur les connaissances du LLM
        return f"""Tu es CodeCoach, un expert en développement logiciel.
Réponds à la question suivante{lang_hint} en te basant sur tes connaissances.

Question : {question}"""

    return f"""Tu es CodeCoach, un expert en développement logiciel.
Utilise les extraits de documentation ci-dessous pour répondre à la question{lang_hint}.
Si les extraits ne contiennent pas la réponse, dis-le clairement.

═══ CONTEXTE EXTRAIT DE LA DOCUMENTATION ═══
{context}
═══════════════════════════════════════════

Question : {question}

Réponds de façon précise et structurée en citant les sources si pertinent."""

# ── Fonction principale appelée par Next.js ───────────────────
def rag_query(question: str, language: str = "", top_k: int = TOP_K) -> dict:
    """
    Fonction principale : prend une question, retourne le contexte + prompt.
    Appelée par l'API Route Next.js via un sous-processus Python.
    """
    try:
        chunks  = search(question, top_k=top_k)
        context = build_context(chunks)
        prompt  = build_rag_prompt(question, context, language)

        return {
            "success":  True,
            "prompt":   prompt,
            "context":  context,
            "chunks":   chunks,
            "has_context": bool(context),
            "sources":  list({c["source"] for c in chunks}),
        }
    except Exception as e:
        return {
            "success":     False,
            "error":       str(e),
            "prompt":      question,
            "context":     "",
            "chunks":      [],
            "has_context": False,
            "sources":     [],
        }

# ── Test depuis le terminal ────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(f"\n{AMBER}Usage : python rag/query.py \"ta question\"{RESET}\n")
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    print(f"\n{BOLD}{AMBER}╔══════════════════════════════════╗")
    print(f"║  CodeCoach RAG — Recherche       ║")
    print(f"╚══════════════════════════════════╝{RESET}")
    print(f"\n{CYAN}Question :{RESET} {question}\n")

    # Vérifier que ChromaDB est initialisé
    if not CHROMA_DIR.exists():
        print(f"{AMBER}⚠  Base ChromaDB introuvable.")
        print(f"   Lance d'abord : python rag/ingest.py{RESET}\n")
        sys.exit(1)

    # Recherche
    print(f"{CYAN}Recherche dans ChromaDB...{RESET}")
    chunks = search(question)

    if not chunks:
        print(f"{AMBER}⚠  Aucun chunk pertinent trouvé (score < {MIN_SCORE}){RESET}")
        print(f"   Vérifie que des documents sont indexés : python rag/ingest.py --stats\n")
        sys.exit(0)

    # Afficher les résultats
    print(f"\n{GREEN}✓  {len(chunks)} chunk(s) trouvé(s) :{RESET}\n")
    for i, chunk in enumerate(chunks, 1):
        score_bar = "█" * int(chunk["score"] * 10) + "░" * (10 - int(chunk["score"] * 10))
        print(f"  {BOLD}#{i}{RESET}  {CYAN}{chunk['source']}{RESET}  [{score_bar}] {chunk['score']}")
        preview = chunk["text"][:120].replace("\n", " ")
        print(f"      {GRAY}{preview}...{RESET}\n")

    # Construire et afficher le contexte
    context = build_context(chunks)
    prompt  = build_rag_prompt(question, context)

    print(f"{AMBER}═══ PROMPT AUGMENTÉ ═══{RESET}")
    print(prompt[:800] + ("..." if len(prompt) > 800 else ""))
    print(f"{AMBER}═══════════════════════{RESET}\n")

    # Retourner le JSON pour l'API
    result = rag_query(question)
    print(f"{GREEN}✓  Prêt à envoyer à Qwen2.5-Coder{RESET}")
    print(f"   Sources utilisées : {', '.join(result['sources'])}\n")

if __name__ == "__main__":
    main()