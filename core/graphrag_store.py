from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import json
import pickle
import os

import networkx as nx
import numpy as np

# ⭐ Supprimer les warnings HuggingFace / transformers avant tout import
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

_ROOT      = Path(__file__).parent.parent
_GRAPHRAG  = _ROOT / "graphrag"

GRAPH_FILE = _GRAPHRAG / "graph.gpickle"
FAISS_FILE = _GRAPHRAG / "faiss.index"
META_FILE  = _GRAPHRAG / "meta.json"


@dataclass
class Chunk:
    id:     str
    text:   str
    source: str


# ⭐ Cache global — l'embedder est partagé entre toutes les instances
# Évite de recharger all-MiniLM-L6-v2 à chaque GraphRAGStore()
_EMBEDDER_CACHE: Dict[str, Any] = {}


class GraphRAGStore:
    """
    Stockage GraphRAG :
    - Graphe NetworkX → graphrag/graph.gpickle
    - Index FAISS     → graphrag/faiss.index
    - Métadonnées     → graphrag/meta.json
    """

    MODEL_NAME = "all-MiniLM-L6-v2"

    def __init__(self):
        self.g:     nx.DiGraph = nx.DiGraph()
        self.index: Any        = None
        self.meta:  List[Dict] = []
        self._dim:  int        = 384

    # ──────────────────────────────────────────
    # Embeddings
    # ──────────────────────────────────────────

    def _get_embedder(self):
        """
        Charge SentenceTransformer une seule fois par processus.
        Le cache global évite tout rechargement entre instances ou appels.
        """
        if self.MODEL_NAME not in _EMBEDDER_CACHE:
            try:
                import logging
                logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
                logging.getLogger("transformers").setLevel(logging.ERROR)
                logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer(self.MODEL_NAME, local_files_only=False)
                _EMBEDDER_CACHE[self.MODEL_NAME] = model
                self._dim = model.get_sentence_embedding_dimension()
                print(f"   🤖 Embedder chargé : {self.MODEL_NAME} (dim={self._dim})")

            except ImportError:
                raise ImportError(
                    "sentence-transformers requis : pip install sentence-transformers"
                )

        return _EMBEDDER_CACHE[self.MODEL_NAME]

    def _embed(self, texts: List[str]) -> np.ndarray:
        embedder = self._get_embedder()
        vecs = embedder.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True,
            batch_size=32,
        )
        return np.array(vecs, dtype="float32")

    # ──────────────────────────────────────────
    # Construction de l'index vectoriel
    # ──────────────────────────────────────────

    def build_vectors(self, chunks: List[Chunk]) -> None:
        """Construit l'index FAISS depuis une liste de Chunk."""
        if not chunks:
            print("⚠️  Aucun chunk à indexer")
            return

        try:
            import faiss
        except ImportError:
            raise ImportError("faiss requis : pip install faiss-cpu")

        texts      = [c.text for c in chunks]
        vecs       = self._embed(texts)
        self._dim  = vecs.shape[1]

        # IndexFlatIP = produit scalaire sur vecteurs normalisés = cosine similarity
        self.index = faiss.IndexFlatIP(self._dim)
        self.index.add(vecs)

        self.meta = [
            {"id": c.id, "text": c.text, "source": c.source}
            for c in chunks
        ]

        print(f"   🔢 Index FAISS : {self.index.ntotal} vecteurs (dim={self._dim})")

    # ──────────────────────────────────────────
    # Recherche vectorielle
    # ──────────────────────────────────────────

    def vector_search(self, query: str, k: int = 8) -> List[Tuple[Dict, float]]:
        """Retourne les k chunks les plus proches de la query."""
        if self.index is None or self.index.ntotal == 0:
            return []

        q_vec           = self._embed([query])
        k_eff           = min(k, self.index.ntotal)
        scores, indices = self.index.search(q_vec, k_eff)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if 0 <= idx < len(self.meta):
                results.append((self.meta[idx], float(score)))
        return results

    # ──────────────────────────────────────────
    # Sauvegarde
    # ──────────────────────────────────────────

    def save(self) -> None:
        """Sauvegarde dans graphrag/graph.gpickle, faiss.index, meta.json."""
        _GRAPHRAG.mkdir(parents=True, exist_ok=True)

        # Graphe NetworkX
        with open(GRAPH_FILE, "wb") as f:
            pickle.dump(self.g, f, protocol=pickle.HIGHEST_PROTOCOL)

        # Index FAISS
        if self.index is not None:
            try:
                import faiss
                faiss.write_index(self.index, str(FAISS_FILE))
            except Exception as e:
                print(f"⚠️  Sauvegarde FAISS échouée : {e}")

        # Métadonnées JSON
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)

        print(f"   💾 Sauvegardé → {GRAPH_FILE.name}, {FAISS_FILE.name}, {META_FILE.name}")

    # ──────────────────────────────────────────
    # Chargement
    # ──────────────────────────────────────────

    def load(self) -> None:
        """Charge depuis graphrag/graph.gpickle, faiss.index, meta.json."""
        missing = [str(f) for f in (GRAPH_FILE, FAISS_FILE, META_FILE) if not f.exists()]
        if missing:
            raise FileNotFoundError(
                f"Fichiers GraphRAG manquants : {missing}\n"
                f"Lance d'abord : python core/graphrag_ingest.py"
            )

        # Graphe NetworkX
        with open(GRAPH_FILE, "rb") as f:
            self.g = pickle.load(f)

        # Index FAISS
        try:
            import faiss
            self.index = faiss.read_index(str(FAISS_FILE))
            self._dim  = self.index.d
        except Exception as e:
            raise RuntimeError(f"Chargement FAISS échoué : {e}")

        # Métadonnées
        with open(META_FILE, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

        print(
            f"✅ GraphRAG chargé : "
            f"{self.g.number_of_nodes()} nœuds, "
            f"{self.index.ntotal} vecteurs, "
            f"{len(self.meta)} chunks"
        )

    @classmethod
    def load_existing(cls) -> "GraphRAGStore":
        """Factory : charge un store existant depuis graphrag/."""
        store = cls()
        store.load()
        return store