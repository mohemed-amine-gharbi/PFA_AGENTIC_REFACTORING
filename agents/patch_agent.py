# ==================== agents/patch_agent.py (version corrigée) ====================

from .base_agent import BaseAgent
import re


class PatchAgent(BaseAgent):
    """
    Agent de nettoyage avancé avec validation de syntaxe.
    """

    def __init__(self, llm):
        super().__init__(llm, name="PatchAgent")
        self.changes_applied = []

    def analyze(self, code, language):
        """Détecte les problèmes de formatage"""
        issues = []
        self.changes_applied = []  # Réinitialiser

        # Détection de markdown
        if "```" in code:
            issues.append({"type": "markdown", "note": "Blocs Markdown détectés"})

        # Détection de texte explicatif
        lines = code.splitlines()
        code_started = False
        non_code_lines = []

        for i, line in enumerate(lines[:10]):  # Vérifier les 10 premières lignes
            stripped = line.strip()
            if not stripped:
                continue
            if not code_started:
                if stripped.startswith(("import", "def", "class", "from", "function", "public", "private", "const", "let", "var")):
                    code_started = True
                else:
                    non_code_lines.append(f"Ligne {i+1}: {stripped[:50]}...")

        if non_code_lines:
            issues.append({"type": "explanatory_text", "note": f"Texte non-code détecté: {len(non_code_lines)} lignes"})

        if not issues:
            issues.append({"type": "clean", "note": "Code relativement propre"})

        return issues

    def clean_code(self, code, language):
        """
        Nettoie le code sans utiliser le LLM pour éviter les erreurs de syntaxe.
        """
        cleaned_lines = []
        in_code_block = False
        code_started = False

        # Patterns de texte explicatif à ignorer
        EXPLANATORY_PATTERNS = [
            r"^here'?s?\s+",
            r"^voici\s+",
            r"^le code",
            r"^the code",
            r"^corrected",
            r"^corrigé",
            r"^refactored",
            r"^improved",
            r"^\d+\.\s+",   # Listes numérotées : "1. ..."
            r"^[-*]\s+",    # Puces : "- ..." ou "* ..."
            r"^this\s+",
            r"^note:",
            r"^explanation",
            r"^i've",
        ]

        PYTHON_STARTERS = (
            "import ", "from ", "def ", "class ", "@",
            "if ", "elif ", "else:", "for ", "while ",
            "with ", "try:", "except", "finally:",
            "return ", "yield ", "raise ", "assert ",
            "print(", "#", '"""', "'''",
        )

        for line in code.splitlines():
            stripped = line.strip()

            # --- Gestion des blocs markdown ---
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue

            # À l'intérieur d'un bloc markdown : garder la ligne
            if in_code_block:
                if stripped:
                    code_started = True
                cleaned_lines.append(line)
                continue

            # Hors bloc markdown : filtrer le texte explicatif
            if not stripped:
                if code_started:  # Garder les lignes vides APRÈS le début du code
                    cleaned_lines.append(line)
                continue

            stripped_lower = stripped.lower()

            # Ignorer les lignes explicatives
            is_explanatory = any(re.match(p, stripped_lower) for p in EXPLANATORY_PATTERNS)
            if is_explanatory:
                continue

            # Vérifier si c'est une vraie ligne de code
            is_code = (
                stripped.startswith(PYTHON_STARTERS)
                or re.match(r'^[A-Z_][A-Z_0-9]*\s*=', stripped)   # Constantes
                or re.match(r'^[a-z_]\w*\s*[=(]', stripped)        # Variables/appels
                or re.match(r'^\s', line)                           # Ligne indentée
            )

            if is_code:
                code_started = True
                cleaned_lines.append(line)
            elif code_started:
                pass  # On drop silencieusement

        cleaned_code = "\n".join(cleaned_lines)

        # --- Nettoyage des commentaires inline Python ---
        if language.lower() == "python":
            final_lines = []
            for line in cleaned_code.splitlines():
                hash_pos = line.find("#")
                if hash_pos != -1:
                    before = line[:hash_pos]
                    if before.count('"') % 2 == 0 and before.count("'") % 2 == 0:
                        line = line[:hash_pos].rstrip()
                if line.strip():
                    final_lines.append(line)
            cleaned_code = "\n".join(final_lines)

        return cleaned_code
    
    def _validate_and_fix(self, code: str, language: str):
        """Valide la syntaxe et retourne (code, is_valid)."""
        if language.lower() != "python":
            return code, True

        try:
            import ast
            ast.parse(code)
            self.changes_applied.append("Syntaxe Python validée ✅")
            return code, True
        except SyntaxError as e:
            print(f"⚠️  Erreur de syntaxe après nettoyage : {e}")
            self.changes_applied.append(f"Erreur de syntaxe détectée : {e}")
            return code, False
        
    def _extract_from_markdown(self, code: str) -> str:
        import re
        match = re.search(r"```(?:\w+)?\n(.*?)```", code, re.DOTALL)
        if match:
            return match.group(1).strip()
        return code

    def _strip_explanatory_lines(self, code: str, language: str) -> str:
        lines = code.splitlines()
        start = 0
        for i, line in enumerate(lines):
            if self._line_is_code(line.strip(), language):
                start = i
                break
        end = len(lines)
        for i in range(len(lines) - 1, start - 1, -1):
            if lines[i].strip() and self._line_is_code(lines[i].strip(), language):
                end = i + 1
                break
        return "\n".join(lines[start:end])
    
    def _apply_black(self, code: str) -> str:
        """Applique Black directement sur le code — résultat garanti."""
        try:
            import black
            formatted = black.format_str(code, mode=black.Mode())
            self.changes_applied.append("Black appliqué ✅")
            return formatted
        except ImportError:
            print("⚠️ Black non installé — pip install black")
            return code
        except black.InvalidInput as e:
            print(f"⚠️ Black ne peut pas formater ce code : {e}")
            return code


    def _apply_ruff(self, code: str) -> str:
        """Applique Ruff directement sur le code."""
        try:
            import tempfile, subprocess, os
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                tmp_path = f.name

            subprocess.run(
                ["ruff", "check", "--fix", tmp_path],
                capture_output=True, check=False
            )

            with open(tmp_path, encoding="utf-8") as f:
                fixed = f.read()

            os.unlink(tmp_path)
            self.changes_applied.append("Ruff appliqué ✅")
            return fixed

        except Exception as e:
            print(f"⚠️ Ruff fix échoué : {e}")
            return code

    def apply(self, code, language, temperature=None, errors=None):
        self.changes_applied = []
        analysis = self.analyze(code, language)

        if language.lower() == "python":
            # ⭐ Toujours appliquer Black et Ruff directement (pas via LLM)
            code = self._apply_ruff(code)   # Ruff en premier (corrige les imports etc.)
            code = self._apply_black(code)  # Black en dernier (formatage final)

        if errors:
            # Filtrer les erreurs Black/Ruff qui sont déjà corrigées
            remaining_errors = [
                e for e in errors
                if not any(t in e for t in ["black", "ruff"])
            ]
            if remaining_errors:
                print(f"   🎯 Correction LLM ciblée : {len(remaining_errors)} erreur(s)...")
                code = self._fix_with_llm(code, language, remaining_errors)
            else:
                print("   ✅ Uniquement des erreurs Black/Ruff — corrigées sans LLM")
        else:
            cleaned = self.clean_code(code, language)
            code = cleaned
            self.changes_applied.append("Nettoyage standard appliqué")

        code, syntax_ok = self._validate_and_fix(code, language)

        if not syntax_ok:
            self.changes_applied.append("⚠️ Fallback sur code précédent")

        return {
            "name": self.name,
            "analysis": analysis,
            "proposal": code,
            "changes_applied": self.changes_applied,
            "temperature_used": temperature if temperature is not None else "N/A",
            "status": "SUCCESS" if syntax_ok else "WARNING",
        }
        

    def _fix_with_llm(self, code: str, language: str, errors: list) -> str:
        """Corrige le code en ciblant les erreurs ET warnings remontés par le TestAgent."""
        if not hasattr(self.llm, 'ask'):
            return code

        # Séparer erreurs bloquantes et warnings de style
        blocking = [e for e in errors if any(t in e for t in ["python_syntax", "mypy"])]
        style    = [e for e in errors if any(t in e for t in ["black", "ruff"])]
        other    = [e for e in errors if e not in blocking and e not in style]

        sections = []

        if blocking:
            sections.append(
                "ERREURS BLOQUANTES À CORRIGER EN PRIORITÉ (syntaxe, types) :\n"
                + "\n".join(f"  - {e}" for e in blocking[:5])
            )

        if style:
            sections.append(
                "PROBLÈMES DE STYLE À CORRIGER (formatage Black, règles Ruff) :\n"
                + "\n".join(f"  - {e}" for e in style[:5])
                + "\n  → Appliquez le formatage Black standard : 88 chars/ligne, "
                "double quotes, espaces autour des opérateurs, ligne vide entre fonctions."
            )

        if other:
            sections.append(
                "AUTRES PROBLÈMES :\n"
                + "\n".join(f"  - {e}" for e in other[:3])
            )

        errors_str = "\n\n".join(sections)

        prompt = f"""INSTRUCTIONS STRICTES :
    1. Retournez UNIQUEMENT du code {language} corrigé
    2. AUCUN texte explicatif, AUCUN markdown, AUCUN commentaire
    3. Corrigez TOUTES les erreurs et warnings listés ci-dessous
    4. Pour les problèmes Black : respectez strictement PEP8
    - Longueur max 88 caractères par ligne
    - Double quotes pour les strings
    - 2 lignes vides entre les fonctions/classes
    - 1 ligne vide entre les méthodes
    - Espaces autour des opérateurs (=, +, -, etc.)
    - Pas d'espaces superflus

    PROBLÈMES À CORRIGER :
    {errors_str}

    CODE À CORRIGER :
    {code}

    RETOURNEZ UNIQUEMENT LE CODE CORRIGÉ :"""

        try:
            result = self.llm.ask(
                system_prompt=(
                    f"Tu es un expert en code {language} et formatage PEP8/Black. "
                    "Retourne UNIQUEMENT du code propre et bien formaté. "
                    "Zéro explication, zéro markdown."
                ),
                user_prompt=prompt,
                temperature=0.05,
            )
            cleaned = self._extract_from_markdown(result)
            cleaned = self._strip_explanatory_lines(cleaned, language)
            self.changes_applied.append(
                f"Correction LLM : {len(blocking)} erreur(s) bloquante(s), "
                f"{len(style)} warning(s) de style"
            )
            return cleaned

        except Exception as e:
            print(f"⚠️ LLM correction échouée : {e}")
            return code