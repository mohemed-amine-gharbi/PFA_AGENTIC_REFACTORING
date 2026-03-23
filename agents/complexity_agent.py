from agents.base_agent import BaseAgent
import ast
from typing import Optional, Dict, Any


class ComplexityAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, name="ComplexityAgent")

    # ──────────────────────────────────────────
    # Détection AST
    # ──────────────────────────────────────────

    def analyze(self, code: str, language: str = "python") -> list:
        """
        Détecte les problèmes de complexité via AST.
        Retourne toujours une liste non vide pour forcer le refactoring.
        """
        issues = []

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

                    # Complexité cyclomatique
                    cc = self._cyclomatic_complexity(node)
                    if cc > 4:
                        issues.append(
                            f"Fonction '{node.name}' : complexité cyclomatique élevée ({cc})"
                        )

                    # Profondeur d'imbrication
                    depth = self._nesting_depth(node)
                    if depth > 2:
                        issues.append(
                            f"Fonction '{node.name}' : imbrication profonde (niveau {depth})"
                        )

                    # Longueur de fonction
                    length = (getattr(node, "end_lineno", node.lineno) or 0) - node.lineno
                    if length > 20:
                        issues.append(
                            f"Fonction '{node.name}' : trop longue ({length} lignes)"
                        )

                    # Trop de branches if
                    branches = sum(
                        1 for n in ast.walk(node)
                        if isinstance(n, ast.If)
                    )
                    if branches > 3:
                        issues.append(
                            f"Fonction '{node.name}' : trop de branches ({branches} if/elif)"
                        )

        except SyntaxError:
            pass

        # Analyse textuelle fallback
        lines = code.splitlines()

        nested = sum(
            1 for line in lines
            if line.strip().startswith(("for ", "while "))
            and _indentation(line) > 4
        )
        if nested:
            issues.append(f"Boucles imbriquées détectées ({nested} occurrence(s))")

        long_lines = [i + 1 for i, l in enumerate(lines) if len(l) > 100]
        if long_lines:
            issues.append(f"Lignes trop longues (>100 chars) : {long_lines[:3]}")

        # Toujours retourner au moins un élément
        if not issues:
            issues.append("Analyse de complexité générale — refactoring préventif")

        return issues

    def _cyclomatic_complexity(self, func_node) -> int:
        """Complexité cyclomatique = 1 + nombre de branchements."""
        count = 1
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler,
                                  ast.With, ast.Assert, ast.comprehension)):
                count += 1
            elif isinstance(node, ast.BoolOp):
                count += len(node.values) - 1
        return count

    def _nesting_depth(self, node, current: int = 0) -> int:
        """Profondeur max d'imbrication des blocs."""
        max_depth = current
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While,
                                   ast.With, ast.Try, ast.FunctionDef)):
                max_depth = max(max_depth, self._nesting_depth(child, current + 1))
        return max_depth

    # ──────────────────────────────────────────
    # Prompt
    # ──────────────────────────────────────────

    def build_prompt(self, code: str, language: str) -> str:
        return f"""You are an expert code refactoring agent specialized in reducing complexity in {language} code.

### Complexity smells to fix
- High cyclomatic or cognitive complexity
- Deep nesting (more than 2 levels)
- Long functions (more than 20 lines)
- Mixed responsibilities in a single function
- Repeated conditional logic and boolean expressions
- Implicit or hidden control flow

### Strict constraints
- Preserve EXACT behavior for all inputs and edge cases
- Do not change return values, side effects, raised exceptions, or execution order
- Do not change public APIs or function signatures
- Preserve logging, I/O, randomness, and global state

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


# ──────────────────────────────────────────
# Utilitaire
# ──────────────────────────────────────────

def _indentation(line: str) -> int:
    return len(line) - len(line.lstrip())