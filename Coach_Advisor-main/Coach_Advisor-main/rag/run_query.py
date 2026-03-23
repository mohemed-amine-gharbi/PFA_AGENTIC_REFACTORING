"""
run_query.py — appelé par Next.js via spawn('python', [scriptPath, problem, language])
Retourne un JSON sur stdout que route.ts parse directement.
"""

import sys
import json
import os
from pathlib import Path

# Fix encodage Windows — force UTF-8 sur stdout
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Ajouter le dossier rag/ au path pour importer query.py
sys.path.insert(0, str(Path(__file__).parent))

from query import rag_query

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Missing arguments",
            "context": "",
            "sources": [],
            "has_context": False,
            "prompt": "",
            "chunks": []
        }))
        sys.exit(0)

    problem  = sys.argv[1] if len(sys.argv) > 1 else ""
    language = sys.argv[2] if len(sys.argv) > 2 else ""

    result = rag_query(problem, language)

    # Sortie JSON propre sur stdout — c'est tout ce que Next.js lit
    print(json.dumps(result, ensure_ascii=True))

if __name__ == "__main__":
    main()