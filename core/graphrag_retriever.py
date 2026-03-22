from __future__ import annotations
from typing import List, Dict, Any, Set, Tuple
from pathlib import Path
import sys

# ⭐ Import absolu depuis la racine — évite conflit avec graphrag/graphrag_store.py
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

# Nettoyer le cache si une ancienne version du store est chargée
for _key in list(sys.modules.keys()):
    if "graphrag_store" in _key and "core" not in _key:
        del sys.modules[_key]

from core.graphrag_store import GraphRAGStore


class GraphRAGRetriever:
    """
    Retriever GraphRAG.
    Priorité : knowledge/{language}/ > knowledge/shared/ > autres sources.
    Déduplication par id ET par source pour éviter les doublons.
    """

    EXCLUDED_DIR_TOKENS = {
        "__pycache__", ".git", ".venv", "venv",
        "node_modules", "test_results", "graphrag",
    }

    EXCLUDED_FILE_NAMES = {
        "base_agent.py", "merge_agent.py", "langgraph_orchestrator.py",
        "workflow_graph.py", "workflow_nodes.py", "workflow_state.py",
    }

    EXCLUDED_PATH_SUBSTRINGS = {
        "agents/", "core/langgraph_orchestrator.py",
        "core/workflow_graph.py", "core/workflow_nodes.py",
        "core/workflow_state.py",
    }

    EXCLUDED_EXTENSIONS = {
        ".pyc", ".xlsx", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".log"
    }

    def __init__(self):
        self.store = GraphRAGStore.load_existing()

    # ──────────────────────────────────────────
    # Filtrage / priorité
    # ──────────────────────────────────────────

    def _normalize(self, p: str) -> str:
        return str(p).replace("\\", "/").strip().lower()

    def _infer_language(self, query: str) -> str | None:
        q = query.lower()
        mapping = {
            "python":     "python",
            "javascript": "javascript",
            "typescript": "typescript",
            "java":       "java",
            "c++":        "cpp",
            "cpp":        "cpp",
            "c#":         "csharp",
            "csharp":     "csharp",
            "go":         "go",
            "ruby":       "ruby",
        }
        for key, val in mapping.items():
            if key in q:
                return val
        return None

    def _is_allowed(self, source: str) -> bool:
        if not source:
            return False
        src = self._normalize(source)
        p   = Path(src)

        if p.suffix.lower() in self.EXCLUDED_EXTENSIONS:
            return False
        if p.name.lower() in self.EXCLUDED_FILE_NAMES:
            return False
        if any(tok in set(p.parts) for tok in self.EXCLUDED_DIR_TOKENS):
            return False
        if any(sub in src for sub in self.EXCLUDED_PATH_SUBSTRINGS):
            return False
        return True

    def _priority(self, source: str, query: str) -> int:
        """
        Score de priorité — plus petit = meilleur.
        0 = knowledge/{language}/
        1 = knowledge/shared/
        2 = autre source autorisée
        9 = source rejetée
        """
        if not self._is_allowed(source):
            return 9
        src  = self._normalize(source)
        lang = self._infer_language(query)
        if lang and f"knowledge/{lang}/" in src:
            return 0
        if "knowledge/shared/" in src:
            return 1
        return 2

    def _prioritize(
        self, items: List[dict], query: str, max_items: int
    ) -> List[dict]:
        """
        Déduplique par id ET par source, filtre les sources interdites,
        puis trie par priorité.
        """
        seen_ids:     Set[str] = set()
        seen_sources: Set[str] = set()  # ⭐ déduplication par source
        unique: List[dict]     = []

        for m in items:
            mid    = m.get("id")
            source = m.get("source", "")

            if mid in seen_ids:
                continue
            if not self._is_allowed(source):
                continue
            if source in seen_sources:  # ⭐ ignorer même fichier source deux fois
                continue

            unique.append(m)
            seen_ids.add(mid)
            seen_sources.add(source)

        unique.sort(key=lambda m: (
            self._priority(m.get("source", ""), query),
            m.get("source", ""),
        ))
        return unique[:max_items]

    # ──────────────────────────────────────────
    # Extraction de symboles
    # ──────────────────────────────────────────

    def _symbols_in_text(self, text: str) -> Set[str]:
        """Retourne les symboles du graphe qui apparaissent dans le texte."""
        symbols: Set[str] = set()
        for n, data in self.store.g.nodes(data=True):
            if data.get("type") == "symbol":
                name = data.get("name")
                if name and name in text:
                    symbols.add(name)
        return symbols

    def _expand_graph(self, start_nodes: List[str], hops: int = 2) -> Set[str]:
        """Expand le voisinage du graphe depuis les nœuds de départ."""
        visited  = set(start_nodes)
        frontier = set(start_nodes)
        for _ in range(hops):
            nxt: Set[str] = set()
            for node in frontier:
                try:
                    nxt |= set(self.store.g.neighbors(node))
                except Exception:
                    continue
            nxt     -= visited
            visited |= nxt
            frontier  = nxt
        return visited

    # ──────────────────────────────────────────
    # Retrieve principal
    # ──────────────────────────────────────────

    def retrieve(
        self,
        query:      str,
        k_seeds:    int = 4,
        hops:       int = 2,
        max_chunks: int = 8,
    ) -> Dict[str, Any]:
        """
        Retourne un pack RAG {seeds, symbols, chunks, facts}.

        Étapes :
        1. Recherche vectorielle (sur-échantillonnage × 4)
        2. Filtrage + priorisation des seeds
        3. Expansion graphe depuis les seeds + symboles
        4. Construction du lot de chunks finaux dédupliqués
        """

        # ── 1. Recherche vectorielle ──────────────────────────
        raw_k    = max(k_seeds * 4, 12)
        raw_hits = self.store.vector_search(query, k=raw_k)

        filtered:    List[dict]       = []
        score_by_id: Dict[str, float] = {}

        for m, sc in raw_hits:
            if self._is_allowed(m.get("source", "")):
                filtered.append(m)
                score_by_id[m["id"]] = float(sc)

        seed_items = self._prioritize(filtered, query, max_items=k_seeds)
        seeds: List[Tuple[dict, float]] = [
            (m, score_by_id.get(m["id"], 0.0)) for m in seed_items
        ]

        # ── 2. Expansion graphe ───────────────────────────────
        seed_nodes = [
            f"chunk:{m['id']}" for m, _ in seeds
            if f"chunk:{m['id']}" in self.store.g
        ]
        seed_text = "\n".join(m.get("text", "") for m, _ in seeds)
        symbols   = self._symbols_in_text(query + "\n" + seed_text)
        sym_nodes = [
            f"symbol:{s}" for s in symbols
            if f"symbol:{s}" in self.store.g
        ]

        expanded    = self._expand_graph(seed_nodes + sym_nodes, hops=hops)
        chunk_nodes = [n for n in expanded if n.startswith("chunk:")]

        # ── 3. Construire les chunks de sortie ────────────────
        ordered    = seed_nodes + [c for c in chunk_nodes if c not in seed_nodes]
        candidates: List[dict] = []
        for cn in ordered:
            cid  = cn.split("chunk:")[1]
            item = next((x for x in self.store.meta if x["id"] == cid), None)
            if item:
                candidates.append(item)

        # Fallback : si expansion vide, utiliser les seeds directement
        if not candidates:
            candidates = [m for m, _ in seeds]

        chunks_out = self._prioritize(candidates, query, max_items=max_chunks)

        # ── 4. Facts graphe ───────────────────────────────────
        facts: List[dict] = []
        for s in list(symbols)[:12]:
            sn = f"symbol:{s}"
            if sn in self.store.g:
                try:
                    neigh = list(self.store.g.neighbors(sn))[:8]
                except Exception:
                    neigh = []
                facts.append({"symbol": s, "neighbors": neigh})

        # ── Log ───────────────────────────────────────────────
        lang = self._infer_language(query)
        print(f"[RAG] language : {lang} | seeds : {len(seeds)} | chunks : {len(chunks_out)}")
        for c in chunks_out[:4]:
            print(f"   ↳ {c.get('source', '')}")

        return {
            "seeds":   [{"source": m["source"], "score": sc} for m, sc in seeds],
            "symbols": sorted(list(symbols))[:50],
            "chunks":  chunks_out,
            "facts":   facts,
        }

    # ──────────────────────────────────────────
    # Formatage du contexte pour les agents
    # ──────────────────────────────────────────

    @staticmethod
    def format_context(pack: Dict[str, Any]) -> str:
        """Formate le pack RAG en texte injecteable dans les prompts LLM."""
        parts = ["### GraphRAG Context"]

        if pack.get("symbols"):
            parts.append("**Symbols:** " + ", ".join(pack["symbols"][:20]))

        parts.append("\n### Retrieved Chunks")
        for c in pack.get("chunks", []):
            parts.append(f"\n[SOURCE: {c['source']}]\n{c['text']}")

        return "\n".join(parts)