"""
Script de diagnostic GraphRAG.
Lance : python check_rag.py
"""
import json
from pathlib import Path

ROOT      = Path(__file__).parent
GRAPHRAG  = ROOT / "graphrag"
KNOWLEDGE = ROOT / "knowledge"

print("=" * 60)
print("DIAGNOSTIC GRAPHRAG")
print("=" * 60)

# ── 1. Vérifier les fichiers d'index ──────────────────────────
print("\n📁 Fichiers d'index dans graphrag/")
required = ["graph.gpickle", "faiss.index", "meta.json"]
for fname in required:
    f = GRAPHRAG / fname
    if f.exists():
        size = f.stat().st_size
        print(f"   ✅ {fname} ({size:,} bytes)")
    else:
        print(f"   ❌ {fname} MANQUANT")

# ── 2. Vérifier meta.json ──────────────────────────────────────
meta_file = GRAPHRAG / "meta.json"
if meta_file.exists():
    print("\n📊 Contenu de meta.json")
    with open(meta_file, encoding="utf-8") as f:
        data = json.load(f)
    print(f"   Total chunks : {len(data)}")
    if data:
        sources = list(set(c["source"] for c in data))
        print(f"   Sources ({len(sources)}) :")
        for s in sources[:10]:
            print(f"     - {s}")
        print("\n   Aperçu du premier chunk :")
        print(f"     id     : {data[0]['id']}")
        print(f"     source : {data[0]['source']}")
        print(f"     text   : {data[0]['text'][:120]}...")
    else:
        print("   ⚠️  meta.json est VIDE — l'ingest n'a rien indexé")
else:
    print("\n   ❌ meta.json absent")

# ── 3. Vérifier le dossier knowledge/ ─────────────────────────
print("\n📂 Contenu de knowledge/")
if KNOWLEDGE.exists():
    files = list(KNOWLEDGE.rglob("*"))
    md_files = [f for f in files if f.is_file()]
    print(f"   {len(md_files)} fichiers trouvés")
    for f in md_files:
        size = f.stat().st_size
        status = "✅" if size > 0 else "❌ VIDE"
        print(f"   {status} {f.relative_to(ROOT)} ({size} bytes)")
    if not md_files:
        print("   ❌ knowledge/ est vide — crée des fichiers .md")
else:
    print("   ❌ Dossier knowledge/ ABSENT")
    print("   → Crée : knowledge/python/best_practices.md")

# ── 4. Recommandations ────────────────────────────────────────
print("\n" + "=" * 60)
print("RECOMMANDATIONS")
print("=" * 60)

meta_ok      = meta_file.exists() and len(data) > 0 if meta_file.exists() else False
knowledge_ok = KNOWLEDGE.exists() and any(
    f.stat().st_size > 0
    for f in KNOWLEDGE.rglob("*")
    if f.is_file()
)

if not knowledge_ok:
    print("1. Crée des fichiers dans knowledge/python/ et knowledge/shared/")
    print("   Exemple : knowledge/python/best_practices.md")

if not meta_ok:
    print("2. Lance l'ingest :")
    print("   python core/graphrag_ingest.py")

if meta_ok and knowledge_ok:
    print("✅ Tout est en ordre — le RAG devrait fonctionner")
    print("   Si 0 chunks retournés, vérifie que les embeddings sont corrects")
    print("   pip install sentence-transformers faiss-cpu")
