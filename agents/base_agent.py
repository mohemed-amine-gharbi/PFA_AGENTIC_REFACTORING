import inspect
from typing import Optional, Dict, Any


class BaseAgent:
    """
    Classe de base pour tous les agents.
    Supporte les températures personnalisées et le contexte GraphRAG.
    """

    def __init__(self, llm, name="Agent inconnu"):
        self.llm = llm
        self.name = name

    # ──────────────────────────────────────────
    # RAG helpers
    # ──────────────────────────────────────────

    def _build_rag_prefix(self, rag_context: Optional[Dict[str, Any]]) -> str:
        """
        Construit le préfixe RAG à insérer dans le prompt utilisateur.
        Retourne une chaîne vide si pas de contexte disponible.
        """
        if not rag_context:
            return ""

        context_str = rag_context.get("context_str", "").strip()
        if not context_str:
            return ""

        symbols = rag_context.get("symbols", [])
        symbols_line = ""
        if symbols:
            symbols_line = f"**Relevant symbols:** {', '.join(symbols[:15])}\n\n"

        return (
            "### Knowledge base context (use these best practices in your refactoring)\n\n"
            + symbols_line
            + context_str
            + "\n\n---\n\n"
        )

    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float],
        rag_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Appel LLM unifié.
        Injecte le contexte RAG en tête du prompt utilisateur si disponible.
        Gère la rétrocompatibilité si le LLM ne supporte pas le paramètre temperature.
        """
        rag_prefix = self._build_rag_prefix(rag_context)
        full_user_prompt = rag_prefix + user_prompt

        try:
            if temperature is not None:
                sig = inspect.signature(self.llm.ask)
                if "temperature" in sig.parameters:
                    return self.llm.ask(
                        system_prompt=system_prompt,
                        user_prompt=full_user_prompt,
                        temperature=temperature,
                    )

            return self.llm.ask(
                system_prompt=system_prompt,
                user_prompt=full_user_prompt,
            )

        except Exception as e:
            print(f"⚠️  Erreur LLM pour {self.name}: {e}")
            return ""

    # ──────────────────────────────────────────
    # Interface publique
    # ──────────────────────────────────────────

    def analyze(self, code: str, language: str) -> list:
        """
        Analyse le code et retourne une liste de problèmes.
        Doit être surchargée par chaque agent.
        """
        return []

    def build_prompt(self, code: str, language: str) -> str:
        """Prompt système par défaut — à surcharger."""
        return f"Refactor the following {language} code to improve {self.name} quality."

    def apply(
        self,
        code: str,
        language: str,
        temperature: Optional[float] = None,
        rag_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Applique l'analyse et la refactorisation sur le code.

        Args:
            code:         Code source à traiter.
            language:     Langage de programmation.
            temperature:  Température LLM (optionnel).
            rag_context:  Contexte GraphRAG (optionnel).

        Returns:
            dict standardisé avec name, analysis, proposal, temperature_used.
        """
        analysis = self.analyze(code, language)

        if analysis:
            llm_method = getattr(self.llm, "ask", None)
            if not callable(llm_method):
                raise AttributeError(
                    f"LLM client {self.llm} n'a pas de méthode 'ask'"
                )

            system_prompt = self.build_prompt(code, language)

            proposal = self._call_llm(
                system_prompt=system_prompt,
                user_prompt=code,
                temperature=temperature,
                rag_context=rag_context,
            )

            if not proposal:
                proposal = code
        else:
            proposal = code

        result: Dict[str, Any] = {
            "name": self.name,
            "analysis": analysis,
            "proposal": proposal,
        }

        if temperature is not None:
            result["temperature_used"] = temperature

        return result