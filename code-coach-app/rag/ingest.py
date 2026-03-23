"""
╔══════════════════════════════════════════════════════════════╗
║  CodeCoach RAG — ingest.py                                   ║
║  Indexe tes documents dans ChromaDB via Ollama embeddings    ║
║                                                              ║
║  Usage:                                                      ║
║    python rag/ingest.py                    ← tous les docs   ║
║    python rag/ingest.py --file doc.pdf     ← un seul fichier ║
║    python rag/ingest.py --reset            ← vider la base   ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import argparse
import hashlib
from pathlib import Path

import chromadb
from chromadb.config import Settings

# ── Parsers de documents ──────────────────────────────────────
try:
    from pypdf import PdfReader
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("⚠  pypdf non installé — pip install pypdf")

try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    print("⚠  python-docx non installé — pip install python-docx")

# ── Configuration ─────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
DOCS_DIR      = BASE_DIR / "documents"
CHROMA_DIR    = BASE_DIR / "chroma_db"
COLLECTION    = "codecoach_docs"
EMBED_MODEL   = "nomic-embed-text"   # ollama pull nomic-embed-text
OLLAMA_URL    = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Chunking
CHUNK_SIZE    = 512    # caractères par chunk
CHUNK_OVERLAP = 64     # chevauchement pour garder le contexte

# Extensions supportées
SUPPORTED = {
    ".pdf":  "pdf",
    ".docx": "docx",
    ".txt":  "text",
    ".md":   "markdown",
    ".py":   "python",
    ".js":   "javascript",
    ".ts":   "typescript",
    ".java": "java",
    ".cpp":  "cpp",
    ".c":    "c",
    ".cs":   "csharp",
    ".go":   "go",
    ".rb":   "ruby",
    ".rs":   "rust",
    ".php":  "php",
}

# ── Couleurs terminal ──────────────────────────────────────────
GREEN  = "\033[92m"
AMBER  = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def log(msg, color=RESET):    print(f"{color}{msg}{RESET}")
def ok(msg):                  log(f"  ✓  {msg}", GREEN)
def warn(msg):                log(f"  ⚠  {msg}", AMBER)
def err(msg):                 log(f"  ✗  {msg}", RED)
def info(msg):                log(f"  →  {msg}", CYAN)

# ── Extraction de texte ────────────────────────────────────────
def extract_text(path: Path) -> str:
    ext = path.suffix.lower()

    if ext == ".pdf":
        if not HAS_PDF:
            warn(f"Ignoré (pypdf manquant) : {path.name}")
            return ""
        reader = PdfReader(path)
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        )

    if ext == ".docx":
        if not HAS_DOCX:
            warn(f"Ignoré (python-docx manquant) : {path.name}")
            return ""
        doc = DocxDocument(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    # Tous les autres : texte brut (txt, md, code)
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        err(f"Impossible de lire {path.name} : {e}")
        return ""

# ── Chunking ───────────────────────────────────────────────────
def chunk_text(text: str, source: str) -> list[dict]:
    """
    Découpe le texte en chunks avec chevauchement.
    Retourne une liste de dicts : {text, chunk_index, source}
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start  = 0
    idx    = 0

    while start < len(text):
        end   = start + CHUNK_SIZE
        chunk = text[start:end]

        # Essayer de couper sur un espace ou saut de ligne
        if end < len(text):
            last_space = max(chunk.rfind(" "), chunk.rfind("\n"))
            if last_space > CHUNK_SIZE // 2:
                chunk = chunk[:last_space]
                end   = start + last_space

        chunk = chunk.strip()
        if chunk:
            chunks.append({
                "text":        chunk,
                "chunk_index": idx,
                "source":      source,
            })
            idx += 1

        start = end - CHUNK_OVERLAP

    return chunks

# ── Embeddings via Ollama ──────────────────────────────────────
def get_embedding(text: str) -> list[float]:
    """
    Appelle Ollama pour générer un embedding du texte.
    Utilise nomic-embed-text (ollama pull nomic-embed-text).
    """
    import urllib.request
    import json

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

    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        # Ollama retourne embeddings[0] pour un seul input
        return data["embeddings"][0]

# ── ChromaDB ───────────────────────────────────────────────────
def get_collection():
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

# ── Indexation d'un fichier ────────────────────────────────────
def ingest_file(path: Path, collection, force: bool = False) -> int:
    info(f"Traitement : {path.name}")

    # Hash du fichier pour éviter les doublons
    file_hash = hashlib.md5(path.read_bytes()).hexdigest()
    doc_id_prefix = f"{path.stem}_{file_hash[:8]}"

    # Vérifier si déjà indexé
    existing = collection.get(where={"source": path.name})
    if existing["ids"] and not force:
        warn(f"Déjà indexé : {path.name} ({len(existing['ids'])} chunks) — utilise --force pour réindexer")
        return 0

    # Supprimer l'ancienne version si force
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
        info(f"Ancienne version supprimée : {len(existing['ids'])} chunks")

    # Extraire le texte
    ext  = path.suffix.lower()
    text = extract_text(path)
    if not text.strip():
        warn(f"Aucun texte extrait de : {path.name}")
        return 0

    file_type = SUPPORTED.get(ext, "text")
    info(f"  Texte extrait : {len(text):,} caractères ({file_type})")

    # Découper en chunks
    chunks = chunk_text(text, path.name)
    if not chunks:
        warn(f"Aucun chunk généré pour : {path.name}")
        return 0

    info(f"  Chunks générés : {len(chunks)}")

    # Générer les embeddings et insérer dans ChromaDB
    ids        = []
    embeddings = []
    documents  = []
    metadatas  = []

    for i, chunk in enumerate(chunks):
        try:
            emb = get_embedding(chunk["text"])
        except Exception as e:
            err(f"Embedding échoué pour chunk {i} : {e}")
            continue

        chunk_id = f"{doc_id_prefix}_chunk{i}"
        ids.append(chunk_id)
        embeddings.append(emb)
        documents.append(chunk["text"])
        metadatas.append({
            "source":      path.name,
            "file_type":   file_type,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "file_hash":   file_hash,
        })

        # Affichage de progression
        if (i + 1) % 10 == 0 or (i + 1) == len(chunks):
            print(f"\r  {CYAN}  Embeddings : {i+1}/{len(chunks)}{RESET}", end="", flush=True)

    print()  # nouvelle ligne après la progression

    if ids:
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        ok(f"{path.name} → {len(ids)} chunks indexés")

    return len(ids)

# ── Main ───────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="CodeCoach RAG — Indexation de documents"
    )
    parser.add_argument("--file",  type=str, help="Indexer un seul fichier")
    parser.add_argument("--reset", action="store_true", help="Vider toute la base ChromaDB")
    parser.add_argument("--force", action="store_true", help="Réindexer même si déjà présent")
    parser.add_argument("--stats", action="store_true", help="Afficher les stats de la base")
    args = parser.parse_args()

    print(f"\n{BOLD}{AMBER}╔══════════════════════════════════╗")
    print(f"║  CodeCoach RAG — Indexation      ║")
    print(f"╚══════════════════════════════════╝{RESET}\n")

    # Créer les dossiers si nécessaire
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    collection = get_collection()

    # Reset
    if args.reset:
        client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        client.delete_collection(COLLECTION)
        ok("Base ChromaDB vidée")
        return

    # Stats
    if args.stats:
        count = collection.count()
        log(f"\n{BOLD}Base ChromaDB : {count} chunks indexés{RESET}")
        if count > 0:
            sample = collection.get(limit=5, include=["metadatas"])
            sources = set(m["source"] for m in sample["metadatas"])
            info(f"Exemples de sources : {', '.join(sources)}")
        return

    # Un seul fichier
    if args.file:
        path = Path(args.file)
        if not path.exists():
            path = DOCS_DIR / args.file
        if not path.exists():
            err(f"Fichier introuvable : {args.file}")
            sys.exit(1)
        if path.suffix.lower() not in SUPPORTED:
            err(f"Extension non supportée : {path.suffix}")
            err(f"Supportées : {', '.join(SUPPORTED.keys())}")
            sys.exit(1)
        ingest_file(path, collection, force=args.force)
        return

    # Tous les documents dans le dossier
    files = [f for f in DOCS_DIR.iterdir() if f.suffix.lower() in SUPPORTED]

    if not files:
        warn(f"Aucun document trouvé dans {DOCS_DIR}")
        warn(f"Dépose tes fichiers dans : {DOCS_DIR}")
        warn(f"Extensions supportées : {', '.join(SUPPORTED.keys())}")
        return

    log(f"Documents trouvés : {len(files)}\n")

    total = 0
    for f in sorted(files):
        total += ingest_file(f, collection, force=args.force)

    print()
    ok(f"Indexation terminée — {total} chunks au total dans ChromaDB")
    info(f"Base stockée dans : {CHROMA_DIR}")

if __name__ == "__main__":
    main()