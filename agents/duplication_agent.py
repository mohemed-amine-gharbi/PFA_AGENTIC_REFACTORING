from agents.base_agent import BaseAgent
import ast
import hashlib
from typing import Optional, Dict, Any, List


class DuplicationAgent(BaseAgent):
    """
    Agent qui détecte le code dupliqué via AST + heuristiques textuelles
    et propose une factorisation via LLM enrichi par RAG.
    """

    def __init__(self, llm):
        super().__init__(llm, name="DuplicationAgent")

    # ──────────────────────────────────────────
    # Détection AST
    # ──────────────────────────────────────────

    def analyze(self, code: str, language: str = "python") -> List[str]:
        """
        Détecte les duplications via :
        - Blocs de code identiques (hash de sous-arbres AST)
        - Séquences de lignes répétées (textuel)
        - Patterns répétitifs (appels similaires, conditions répétées)
        Retourne toujours au moins un élément.
        """
        issues = []

        # --- Analyse AST ---
        try:
            tree = ast.parse(code)

            # 1) Détecter les corps de fonctions identiques
            func_bodies: Dict[str, List[str]] = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body_hash = self._hash_node(node.body)
                    func_bodies.setdefault(body_hash, []).append(node.name)

            for body_hash, names in func_bodies.items():
                if len(names) > 1:
                    issues.append(
                        f"Corps identiques détectés dans les fonctions : {', '.join(names)}"
                    )

            # 2) Détecter les sous-arbres dupliqués (expressions, appels)
            node_hashes: Dict[str, int] = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.Call, ast.For, ast.While, ast.If)):
                    h = self._hash_node(node)
                    node_hashes[h] = node_hashes.get(h, 0) + 1

            duplicated_nodes = {h: c for h, c in node_hashes.items() if c > 1}
            if duplicated_nodes:
                count = sum(duplicated_nodes.values())
                issues.append(
                    f"Blocs dupliqués détectés : {len(duplicated_nodes)} pattern(s) "
                    f"répétés ({count} occurrences au total)"
                )

            # 3) Détecter les fonctions avec trop de paramètres similaires
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [a.arg for a in node.args.args]
                    if len(args) > 5:
                        issues.append(
                            f"Fonction '{node.name}' : {len(args)} paramètres "
                            f"— possible duplication de logique"
                        )

        except SyntaxError:
            pass

        # --- Analyse textuelle ---
        issues += self._detect_textual_duplicates(code)

        # Toujours retourner au moins un élément
        if not issues:
            issues.append("Analyse de duplication générale — refactoring DRY préventif")

        return issues

    def _hash_node(self, node) -> str:
        """Hash stable d'un nœud AST (ignore positions ligne/colonne)."""
        try:
            dump = ast.dump(node)
            return hashlib.md5(dump.encode()).hexdigest()
        except Exception:
            return ""

    def _detect_textual_duplicates(self, code: str) -> List[str]:
        """Détecte les blocs de lignes répétés par fenêtre glissante."""
        issues = []
        lines = [l.strip() for l in code.splitlines() if l.strip()]

        if len(lines) < 6:
            return issues

        # Fenêtre de 3 lignes
        window_size = 3
        seen: Dict[str, int] = {}
        for i in range(len(lines) - window_size + 1):
            block = "\n".join(lines[i:i + window_size])
            block_hash = hashlib.md5(block.encode()).hexdigest()
            seen[block_hash] = seen.get(block_hash, 0) + 1

        duplicated_blocks = {h: c for h, c in seen.items() if c > 1}
        if duplicated_blocks:
            total = sum(duplicated_blocks.values())
            issues.append(
                f"Séquences de lignes répétées : {len(duplicated_blocks)} bloc(s) "
                f"dupliqué(s) ({total} occurrences)"
            )

        # Détecter les patterns d'assignation répétitifs
        assign_patterns: Dict[str, int] = {}
        for line in lines:
            if "=" in line and not line.startswith(("#", "def", "class")):
                # Normaliser la valeur (garder seulement la structure)
                parts = line.split("=", 1)
                if len(parts) == 2:
                    pattern = f"VAR = {parts[1].strip()}"
                    assign_patterns[pattern] = assign_patterns.get(pattern, 0) + 1

        repeated_assigns = {p: c for p, c in assign_patterns.items() if c > 2}
        if repeated_assigns:
            issues.append(
                f"Patterns d'assignation répétitifs : {len(repeated_assigns)} pattern(s) "
                f"— candidats à la factorisation"
            )

        return issues

    # ──────────────────────────────────────────
    # Prompt
    # ──────────────────────────────────────────

    def build_prompt(self, code: str, language: str) -> str:
        return f"""You are an expert code refactoring agent specialized in eliminating code duplication in {language}.

### Duplication smells to fix
- Identical or near-identical code blocks repeated more than once
- Copy-pasted logic with minor variations (extract to parameterized function)
- Repeated conditionals or loops with the same structure
- Similar function bodies that differ only in variable names
- Magic values or constants repeated inline
- Repeated import patterns or boilerplate

### DRY refactoring strategies
- Extract repeated blocks into well-named helper functions
- Use parameters to handle minor variations between duplicates
- Replace repeated magic values with named constants
- Use loops or list comprehensions to replace repetitive sequential statements
- Apply template patterns when structure is identical but types differ

### Strict constraints
- Preserve EXACT behavior for all inputs and edge cases
- Do not change return values, side effects, raised exceptions, or execution order
- Do not change public APIs or function signatures
- Preserve logging, I/O, randomness, and global state
- Only refactor when the extraction genuinely reduces duplication

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