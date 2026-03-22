from agents.base_agent import BaseAgent
import ast
import re
from typing import Optional, Dict, Any, List, Set


class ImportAgent(BaseAgent):
    """
    Agent qui détecte et optimise les imports via AST.
    Supprime les imports inutilisés, dupliqués et mal ordonnés.
    """

    def __init__(self, llm):
        super().__init__(llm, name="ImportAgent")

    # ──────────────────────────────────────────
    # Détection AST
    # ──────────────────────────────────────────

    def analyze(self, code: str, language: str = "python") -> List[str]:
        """
        Détecte via AST :
        - Imports inutilisés
        - Imports dupliqués
        - Imports mal ordonnés (non PEP8)
        - Imports dans le corps de fonctions (à déplacer)
        - Imports avec alias inutiles
        Retourne toujours au moins un élément.
        """
        issues = []
        lang = language.lower()

        if lang == "python":
            issues += self._analyze_python(code)
        elif lang in ("javascript", "typescript"):
            issues += self._analyze_js(code)
        else:
            issues.append(f"Analyse des imports {language} — optimisation via LLM")

        if not issues:
            issues.append("Imports analysés — réorganisation PEP8 préventive")

        return issues

    def _analyze_python(self, code: str) -> List[str]:
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [f"Erreur de syntaxe — analyse impossible : {e}"]

        # --- Collecter tous les imports ---
        imports: List[Dict] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type":   "import",
                        "module": alias.name,
                        "asname": alias.asname,
                        "line":   node.lineno,
                        "node":   node,
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        "type":   "from",
                        "module": node.module or "",
                        "name":   alias.name,
                        "asname": alias.asname,
                        "line":   node.lineno,
                        "node":   node,
                    })

        # --- Collecter tous les noms utilisés dans le code (hors imports) ---
        used_names = self._collect_used_names(tree)

        # --- Imports inutilisés ---
        for imp in imports:
            effective_name = imp.get("asname") or imp.get("name") or imp["module"].split(".")[0]
            if effective_name and effective_name != "*" and effective_name not in used_names:
                if imp["type"] == "import":
                    issues.append(f"Import inutilisé ligne {imp['line']} : import {imp['module']}")
                else:
                    issues.append(
                        f"Import inutilisé ligne {imp['line']} : "
                        f"from {imp['module']} import {imp.get('name', '')}"
                    )

        # --- Imports dupliqués ---
        seen_imports: Set[str] = set()
        for imp in imports:
            key = f"{imp['type']}:{imp['module']}:{imp.get('name', '')}"
            if key in seen_imports:
                issues.append(
                    f"Import dupliqué ligne {imp['line']} : {imp['module']}"
                )
            seen_imports.add(key)

        # --- Imports dans des fonctions/classes (pas au top-level) ---
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for child in ast.walk(node):
                    if isinstance(child, (ast.Import, ast.ImportFrom)) and child.lineno != node.lineno:
                        issues.append(
                            f"Import dans le corps d'une fonction/classe ligne {child.lineno} "
                            f"— à déplacer en haut du fichier"
                        )

        # --- Ordre PEP8 : stdlib → third-party → local ---
        order_issues = self._check_import_order(imports)
        issues.extend(order_issues)

        # --- Alias inutiles (import os as os) ---
        for imp in imports:
            if imp.get("asname") and imp["asname"] == imp["module"].split(".")[-1]:
                issues.append(
                    f"Alias inutile ligne {imp['line']} : "
                    f"import {imp['module']} as {imp['asname']}"
                )

        return issues

    def _collect_used_names(self, tree) -> Set[str]:
        """Collecte tous les noms utilisés dans le code (hors nœuds import)."""
        used: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                # os.path → collecter "os"
                root = node
                while isinstance(root, ast.Attribute):
                    root = root.value
                if isinstance(root, ast.Name):
                    used.add(root.id)
        return used

    def _check_import_order(self, imports: List[Dict]) -> List[str]:
        """Vérifie l'ordre PEP8 : stdlib → third-party → local."""
        import sys
        stdlib_modules = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()

        groups = []
        for imp in imports:
            module = imp["module"].split(".")[0]
            if module in stdlib_modules:
                groups.append(("stdlib", imp["line"]))
            elif module.startswith(".") or imp["type"] == "from" and imp["module"].startswith("."):
                groups.append(("local", imp["line"]))
            else:
                groups.append(("third_party", imp["line"]))

        order = {"stdlib": 0, "third_party": 1, "local": 2}
        issues = []
        for i in range(1, len(groups)):
            prev_group, prev_line = groups[i - 1]
            curr_group, curr_line = groups[i]
            if order.get(curr_group, 1) < order.get(prev_group, 1):
                issues.append(
                    f"Ordre d'import incorrect ligne {curr_line} : "
                    f"'{curr_group}' devrait être avant '{prev_group}' (PEP8)"
                )
        return issues

    def _analyze_js(self, code: str) -> List[str]:
        """Analyse textuelle basique pour JS/TS."""
        issues = []
        lines = code.splitlines()

        import_lines = [
            (i + 1, l.strip())
            for i, l in enumerate(lines)
            if re.match(r"^import\s+", l.strip())
        ]

        # Dupliqués
        seen: Set[str] = set()
        for lineno, imp in import_lines:
            if imp in seen:
                issues.append(f"Import JS dupliqué ligne {lineno} : {imp[:60]}")
            seen.add(imp)

        # Imports inutilisés (heuristique)
        for lineno, imp in import_lines:
            names = re.findall(r'\{([^}]+)\}', imp)
            for group in names:
                for name in group.split(","):
                    name = name.strip().split(" as ")[-1].strip()
                    if name and code.count(name) <= 1:
                        issues.append(
                            f"Import JS potentiellement inutilisé ligne {lineno} : '{name}'"
                        )

        if not issues:
            issues.append("Imports JS/TS analysés — réorganisation recommandée")

        return issues

    # ──────────────────────────────────────────
    # Prompt
    # ──────────────────────────────────────────

    def build_prompt(self, code: str, language: str) -> str:
        return f"""You are an expert code refactoring agent specialized in optimizing imports in {language} code.

### Import smells to fix
- Unused imports (imported but never referenced in the code)
- Duplicate imports (same module imported more than once)
- Imports inside functions or class bodies (move to top of file)
- Wrong import order (PEP8: stdlib → third-party → local)
- Unnecessary aliases (import os as os)
- Wildcard imports (from module import *) — replace with explicit names
- Missing __future__ imports when needed

### Refactoring strategies
- Remove all unused imports entirely
- Merge duplicate imports into a single statement
- Sort imports following PEP8 / isort conventions
- Move function-level imports to the top of the file (unless truly conditional)
- Replace aliases that match the module name with the direct name
- Add a blank line between stdlib, third-party, and local import groups

### Strict constraints
- Preserve EXACT behavior — do not remove an import that is used
- Do not change any logic, function bodies, or class definitions
- Do not change public APIs or function signatures
- If an import is used via __all__ or dynamic access, keep it

### Output format
Return ONLY the refactored {language} code.
No explanation, no markdown, no comments.
First line must be code ({language} import, def, or class).
"""

    # ──────────────────────────────────────────
    # Apply avec RAG
    # ──────────────────────────────────────────

    def apply(
        self,
        code: str,
        language: str,
        temperature: Optional[float] = None,
        rag_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        analysis = self.analyze(code, language)
        system_prompt = self.build_prompt(code, language)

        # ⭐ _call_llm injecte rag_context automatiquement
        proposal = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=code,
            temperature=temperature,
            rag_context=rag_context,
        )

        if not proposal or proposal.strip() == code.strip():
            proposal = code

        return {
            "name":             self.name,
            "analysis":         analysis,
            "proposal":         proposal,
            "temperature_used": temperature,
        }