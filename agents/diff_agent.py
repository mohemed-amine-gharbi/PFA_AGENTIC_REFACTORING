"""
DiffAgent — Agent de comparaison de code.
Génère un diff unifié coloré entre le code original et le code refactoré.
"""

import difflib
from typing import Optional


class DiffAgent:
    """
    Agent léger qui calcule et formate les différences entre deux versions de code.
    Pas de LLM requis — traitement purement local.
    """

    name = "DiffAgent"

    # ──────────────────────────────────────────
    # Diff brut
    # ──────────────────────────────────────────

    @staticmethod
    def make_unified_diff(
        original: str,
        refactored: str,
        filename: str = "file",
        context_lines: int = 3,
    ) -> str:
        """
        Génère un diff unifié standard (format patch).

        Args:
            original:      Code source original.
            refactored:    Code source refactoré.
            filename:      Nom du fichier pour l'en-tête du diff.
            context_lines: Nombre de lignes de contexte autour des changements.

        Returns:
            Texte du diff au format unifié.
        """
        lines = list(
            difflib.unified_diff(
                original.splitlines(),
                refactored.splitlines(),
                fromfile=f"original/{filename}",
                tofile=f"refactoré/{filename}",
                lineterm="",
                n=context_lines,
            )
        )
        return "\n".join(lines)

    # ──────────────────────────────────────────
    # Statistiques
    # ──────────────────────────────────────────

    @staticmethod
    def stats(diff_text: str) -> dict:
        """
        Calcule les statistiques d'un diff.

        Returns:
            dict avec added, removed, delta, changed_blocks
        """
        added   = 0
        removed = 0
        blocks  = 0

        for line in diff_text.splitlines():
            if line.startswith("@@"):
                blocks += 1
            elif line.startswith("+") and not line.startswith("+++"):
                added += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed += 1

        return {
            "added":          added,
            "removed":        removed,
            "delta":          added - removed,
            "changed_blocks": blocks,
        }

    # ──────────────────────────────────────────
    # HTML coloré (rouge / vert)
    # ──────────────────────────────────────────

    @staticmethod
    def to_html(diff_text: str) -> str:
        """
        Convertit un diff unifié en HTML coloré.
        - Lignes supprimées : fond rouge clair
        - Lignes ajoutées   : fond vert clair
        - En-têtes @@       : fond bleu ardoise
        - En-têtes ---/+++  : gras grisé
        """
        if not diff_text.strip():
            return "<p style='color:#64748b;font-style:italic;'>Aucune différence.</p>"

        lines_html = []
        for line in diff_text.splitlines():
            escaped = (
                line
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            if line.startswith("+++") or line.startswith("---"):
                style = (
                    "background:#1e293b;color:#94a3b8;"
                    "font-weight:bold;padding:2px 8px;"
                    "display:block;font-family:monospace;font-size:13px;"
                )
            elif line.startswith("@@"):
                style = (
                    "background:#1e3a5f;color:#7dd3fc;"
                    "padding:2px 8px;display:block;"
                    "font-family:monospace;font-size:13px;"
                )
            elif line.startswith("+"):
                style = (
                    "background:#14532d;color:#86efac;"
                    "padding:2px 8px;display:block;"
                    "font-family:monospace;font-size:13px;"
                )
            elif line.startswith("-"):
                style = (
                    "background:#7f1d1d;color:#fca5a5;"
                    "padding:2px 8px;display:block;"
                    "font-family:monospace;font-size:13px;"
                )
            else:
                style = (
                    "background:#0f172a;color:#cbd5e1;"
                    "padding:2px 8px;display:block;"
                    "font-family:monospace;font-size:13px;"
                )

            lines_html.append(f'<span style="{style}">{escaped}</span>')

        inner = "\n".join(lines_html)
        return f"""
<div style="
    border-radius:8px;
    overflow:hidden;
    border:1px solid #1e293b;
    background:#0f172a;
    overflow-x:auto;
    max-height:600px;
    overflow-y:auto;
    font-size:13px;
    line-height:1.6;
">
{inner}
</div>
"""

    # ──────────────────────────────────────────
    # Point d'entrée principal
    # ──────────────────────────────────────────

    def apply(
        self,
        original: str,
        refactored: str,
        filename: str = "file",
        context_lines: int = 3,
    ) -> dict:
        """
        Calcule le diff complet et retourne un dict structuré.

        Returns:
            {
                name, diff_text, diff_html, stats,
                has_changes, original, refactored
            }
        """
        diff_text = self.make_unified_diff(original, refactored, filename, context_lines)
        diff_html = self.to_html(diff_text)
        statistics = self.stats(diff_text)
        has_changes = bool(diff_text.strip())

        return {
            "name":       self.name,
            "diff_text":  diff_text,
            "diff_html":  diff_html,
            "stats":      statistics,
            "has_changes": has_changes,
            "original":   original,
            "refactored": refactored,
        }
