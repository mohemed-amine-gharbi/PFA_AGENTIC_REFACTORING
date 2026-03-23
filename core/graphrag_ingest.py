from __future__ import annotations
from pathlib import Path
from typing import List, Set
import ast
import re
import hashlib
import sys
import os

# ⭐ Correction : import absolu depuis la racine du projet
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from core.graphrag_store import GraphRAGStore, Chunk


# -------------------- Filtres d'ingest --------------------

EXCLUDED_DIR_TOKENS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "test_results",
    "graphrag",
}

EXCLUDED_FILE_NAMES = {
    "base_agent.py",
    "merge_agent.py",
    "langgraph_orchestrator.py",
    "workflow_graph.py",
    "workflow_nodes.py",
    "workflow_state.py",
}

EXCLUDED_EXTENSIONS = {
    ".pyc", ".xlsx", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".log"
}


def should_index_file(file: Path) -> bool:
    try:
        parts = set(file.parts)
        if any(tok in parts for tok in EXCLUDED_DIR_TOKENS):
            return False
        if file.name.lower() in EXCLUDED_FILE_NAMES:
            return False
        if file.suffix.lower() in EXCLUDED_EXTENSIONS:
            return False
        return True
    except Exception:
        return False


# -------------------- Chunking / symbols --------------------

def chunk_text(text: str, max_chars: int = 1200, overlap: int = 150) -> List[str]:
    chunks = []
    i = 0
    step = max_chars - overlap
    if step <= 0:
        step = max_chars
    while i < len(text):
        chunks.append(text[i:i + max_chars])
        i += step
    return chunks


def stable_id(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()[:16]


def extract_symbols_python(code: str) -> Set[str]:
    symbols: Set[str] = set()
    try:
        tree = ast.parse(code)
    except Exception:
        return symbols
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            symbols.add(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                symbols.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                symbols.add(node.module.split(".")[0])
            for alias in node.names:
                symbols.add(alias.name)
    return symbols


def extract_mentions_symbols(text: str) -> Set[str]:
    camel = set(re.findall(r"\b[A-Z][a-zA-Z0-9_]{2,}\b", text))
    snake = set(re.findall(r"\b[a-z_][a-z0-9_]{2,}\b", text))
    bad = {"return", "import", "from", "class", "def", "self", "True", "False", "None"}
    return {t for t in (camel | snake) if t not in bad and 2 < len(t) <= 60}


# -------------------- Ingest principal --------------------

def ingest(
    paths: List[str],
    patterns=("**/*.py", "**/*.md", "**/*.txt", "**/*.jsonl"),
):
    """
    Construit l'index GraphRAG depuis les chemins donnés.
    Les fichiers d'index sont sauvegardés dans graphrag/.

    Usage recommandé :
        ingest(["knowledge"])
    """
    # ⭐ Toujours travailler depuis la racine du projet
    os.chdir(_ROOT)

    store = GraphRAGStore()
    all_chunks: List[Chunk] = []
    indexed_files = 0
    skipped_files = 0

    for base in paths:
        base_path = Path(base)
        if not base_path.exists():
            print(f"⚠️  Chemin introuvable, ignoré : {base_path.resolve()}")
            continue

        print(f"📂 Indexation de : {base_path.resolve()}")

        for pat in patterns:
            for file in base_path.glob(pat):
                if not file.is_file():
                    continue

                if not should_index_file(file):
                    skipped_files += 1
                    continue

                try:
                    text = file.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    skipped_files += 1
                    continue

                if not text or not text.strip():
                    skipped_files += 1
                    continue

                indexed_files += 1
                file_posix = file.as_posix()
                file_node  = f"file:{file_posix}"
                store.g.add_node(file_node, type="file", path=file_posix)

                symbols: Set[str] = set()
                if file.suffix.lower() == ".py":
                    symbols |= extract_symbols_python(text)

                for sym in symbols:
                    sym_node = f"symbol:{sym}"
                    store.g.add_node(sym_node, type="symbol", name=sym)
                    store.g.add_edge(sym_node, file_node, rel="defined_in")

                for part in chunk_text(text):
                    if not part.strip():
                        continue
                    cid        = stable_id(file_posix + ":" + part[:250])
                    chunk_node = f"chunk:{cid}"

                    all_chunks.append(Chunk(id=cid, text=part, source=file_posix))
                    store.g.add_node(chunk_node, type="chunk", id=cid, source=file_posix)
                    store.g.add_edge(chunk_node, file_node, rel="in_file")

                    for m in extract_mentions_symbols(part):
                        m_node = f"symbol:{m}"
                        store.g.add_node(m_node, type="symbol", name=m)
                        store.g.add_edge(chunk_node, m_node, rel="mentions")

    store.build_vectors(all_chunks)
    store.save()

    print(f"\n✅ GraphRAG indexé : {len(all_chunks)} chunks depuis {indexed_files} fichiers")
    print(f"   Sauvegardé dans : {(_ROOT / 'graphrag').resolve()}")
    print(f"ℹ️  Fichiers ignorés : {skipped_files}")


if __name__ == "__main__":
    ingest(["knowledge"])