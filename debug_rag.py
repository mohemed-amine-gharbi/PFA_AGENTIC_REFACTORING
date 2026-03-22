"""
Debug complet de la recherche vectorielle GraphRAG.
Lance : python debug_rag.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

print("=" * 60)
print("DEBUG VECTOR SEARCH")
print("=" * 60)

# 1) Charger le store
print("\n1. Chargement du store...")
try:
    from core.graphrag_store import GraphRAGStore
    store = GraphRAGStore.load_existing()
    print(f"   ✅ Store chargé")
    print(f"   Index ntotal : {store.index.ntotal}")
    print(f"   Index dim    : {store.index.d}")
    print(f"   Meta chunks  : {len(store.meta)}")
except Exception as e:
    print(f"   ❌ Erreur : {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# 2) Test embedding direct
print("\n2. Test embedding...")
try:
    import numpy as np
    vec = store._embed(["python refactoring best practices"])
    print(f"   ✅ Embedding shape : {vec.shape}")
    print(f"   Norme             : {np.linalg.norm(vec[0]):.4f} (doit être ~1.0)")
except Exception as e:
    print(f"   ❌ Erreur embedding : {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# 3) Test recherche FAISS directe
print("\n3. Test recherche FAISS directe...")
try:
    import faiss
    import numpy as np
    q = store._embed(["python refactoring"])
    k = min(5, store.index.ntotal)
    scores, indices = store.index.search(q, k)
    print(f"   ✅ Résultats bruts FAISS :")
    for sc, idx in zip(scores[0], indices[0]):
        if idx >= 0 and idx < len(store.meta):
            src = store.meta[idx]["source"]
            txt = store.meta[idx]["text"][:60]
            print(f"     score={sc:.4f} | idx={idx} | {src}")
            print(f"       → {txt}...")
        else:
            print(f"     score={sc:.4f} | idx={idx} | INVALIDE")
except Exception as e:
    print(f"   ❌ Erreur FAISS : {e}")
    import traceback; traceback.print_exc()

# 4) Test vector_search() du store
print("\n4. Test store.vector_search()...")
try:
    results = store.vector_search("python refactoring best practices", k=5)
    print(f"   Résultats : {len(results)}")
    for meta, score in results:
        print(f"     score={score:.4f} | {meta['source']}")
except Exception as e:
    print(f"   ❌ Erreur : {e}")
    import traceback; traceback.print_exc()

# 5) Test retrieve() complet
print("\n5. Test retrieve() complet...")
try:
    from core.graphrag_retriever import GraphRAGRetriever
    retriever = GraphRAGRetriever()
    pack = retriever.retrieve("python refactoring best practices rename complexity")
    print(f"   Seeds  : {len(pack['seeds'])}")
    print(f"   Chunks : {len(pack['chunks'])}")
    print(f"   Symbols: {pack['symbols'][:5]}")
    if pack["chunks"]:
        print(f"\n   Premier chunk :")
        c = pack["chunks"][0]
        print(f"     source : {c['source']}")
        print(f"     text   : {c['text'][:100]}...")
    else:
        print("   ⚠️  Aucun chunk retourné")
except Exception as e:
    print(f"   ❌ Erreur : {e}")
    import traceback; traceback.print_exc()

# 6) Vérifier cohérence index vs meta
print("\n6. Cohérence index vs meta...")
print(f"   index.ntotal : {store.index.ntotal}")
print(f"   len(meta)    : {len(store.meta)}")
if store.index.ntotal != len(store.meta):
    print("   ⚠️  INCOHÉRENCE — relance l'ingest : python core/graphrag_ingest.py")
else:
    print("   ✅ Cohérent")

print("\n" + "=" * 60)
