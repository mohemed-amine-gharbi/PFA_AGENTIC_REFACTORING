from agents.base_agent import BaseAgent
import ast
import re
import keyword
import builtins
from typing import Optional, Dict, Any, List, Set


class RenameAgent(BaseAgent):
    """
    Agent spécialisé dans le renommage des identifiants via AST.
    Détecte les noms non expressifs et propose un renommage via LLM + RAG.
    """

    # Longueur minimale d'un bon nom (hors cas acceptables)
    MIN_NAME_LENGTH = 3

    # Noms courts acceptables (conventions Python standard)
    ACCEPTABLE_SHORT_NAMES = {
        "i", "j", "k", "n", "x", "y", "z",  # itérateurs classiques
        "e", "ex",                              # exceptions
        "f", "fp",                              # fichiers
        "df",                                   # dataframe
        "ok", "id",                             # booléens/ids
        "db", "ui", "io",                       # abréviations reconnues
        "fn", "cb",                             # function/callback
        "_",                                    # throwaway
    }

    def __init__(self, llm):
        super().__init__(llm, name="RenameAgent")
        self._python_builtins = set(dir(builtins))
        self._python_keywords = set(keyword.kwlist)

    # ──────────────────────────────────────────
    # Détection AST
    # ──────────────────────────────────────────

    def analyze(self, code: str, language: str = "python") -> List[str]:
        """
        Détecte via AST :
        - Variables à nom trop court ou non expressif
        - Variables à noms génériques (tmp, data, result, val...)
        - Paramètres non expressifs
        - Noms en camelCase dans du Python (convention snake_case)
        - Noms de classes en snake_case (devraient être PascalCase)
        - Constantes en minuscules (devraient être UPPER_CASE)
        Retourne toujours au moins un élément.
        """
        issues = []
        lang = language.lower()

        if lang == "python":
            issues += self._analyze_python(code)
        elif lang in ("javascript", "typescript"):
            issues += self._analyze_js(code)
        else:
            issues.append(
                f"Analyse des noms {language} — renommage expressif via LLM"
            )

        if not issues:
            issues.append(
                "Noms analysés — vérification de l'expressivité et des conventions"
            )

        return issues

    def _analyze_python(self, code: str) -> List[str]:
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [f"Erreur de syntaxe — analyse impossible : {e}"]

        short_names:   List[str] = []
        generic_names: List[str] = []
        camel_names:   List[str] = []
        bad_classes:   List[str] = []
        bad_constants: List[str] = []
        bad_params:    List[str] = []

        generic_patterns = {
            "tmp", "temp", "data", "result", "res", "val", "value",
            "obj", "item", "elem", "element", "thing", "stuff",
            "foo", "bar", "baz", "test", "var", "info", "flag",
            "lst", "arr", "dict", "num", "cnt", "count", "ret",
        }

        # --- Variables et paramètres ---
        for node in ast.walk(tree):

            # Assignations
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    for name in self._extract_names(target):
                        self._check_variable_name(
                            name, short_names, generic_names,
                            camel_names, bad_constants, generic_patterns
                        )

            # Assignations annotées
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    self._check_variable_name(
                        node.target.id, short_names, generic_names,
                        camel_names, bad_constants, generic_patterns
                    )

            # Paramètres de fonctions
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for arg in (node.args.args
                            + node.args.posonlyargs
                            + node.args.kwonlyargs):
                    name = arg.arg
                    if name == "self" or name == "cls":
                        continue
                    if (len(name) < self.MIN_NAME_LENGTH
                            and name not in self.ACCEPTABLE_SHORT_NAMES):
                        bad_params.append(f"{name} (dans '{node.name}')")
                    elif name.lower() in generic_patterns:
                        bad_params.append(f"{name} (dans '{node.name}') — nom générique")

            # Noms de classes
            elif isinstance(node, ast.ClassDef):
                name = node.name
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
                    bad_classes.append(name)

            # Boucles for
            elif isinstance(node, ast.For):
                for name in self._extract_names(node.target):
                    if (len(name) < self.MIN_NAME_LENGTH
                            and name not in self.ACCEPTABLE_SHORT_NAMES
                            and name != "_"):
                        short_names.append(f"{name} (itérateur de boucle)")

        # --- Rapport ---
        if short_names:
            issues.append(
                f"Noms trop courts ({len(short_names)}) : "
                + ", ".join(short_names[:5])
                + (" ..." if len(short_names) > 5 else "")
            )
        if generic_names:
            issues.append(
                f"Noms génériques non expressifs ({len(generic_names)}) : "
                + ", ".join(generic_names[:5])
                + (" ..." if len(generic_names) > 5 else "")
            )
        if camel_names:
            issues.append(
                f"camelCase détecté dans du Python ({len(camel_names)}) "
                f"— utiliser snake_case : "
                + ", ".join(camel_names[:5])
            )
        if bad_classes:
            issues.append(
                f"Classes non PascalCase ({len(bad_classes)}) : "
                + ", ".join(bad_classes[:5])
            )
        if bad_constants:
            issues.append(
                f"Constantes non UPPER_CASE ({len(bad_constants)}) : "
                + ", ".join(bad_constants[:5])
            )
        if bad_params:
            issues.append(
                f"Paramètres non expressifs ({len(bad_params)}) : "
                + ", ".join(bad_params[:5])
            )

        return issues

    def _check_variable_name(
        self,
        name: str,
        short_names: List,
        generic_names: List,
        camel_names: List,
        bad_constants: List,
        generic_patterns: Set,
    ) -> None:
        """Applique toutes les heuristiques sur un nom de variable."""
        if name.startswith("_") or name in self._python_keywords or name in self._python_builtins:
            return

        # Trop court
        if len(name) < self.MIN_NAME_LENGTH and name not in self.ACCEPTABLE_SHORT_NAMES:
            short_names.append(name)
            return

        # Générique
        if name.lower() in generic_patterns:
            generic_names.append(name)
            return

        # camelCase dans du Python
        if re.search(r'[a-z][A-Z]', name) and not name.isupper():
            camel_names.append(name)
            return

        # Constante en minuscules (toutes majuscules dans le nom suggère une constante)
        if name.isupper() is False and re.match(r'^[A-Z_]{2,}$', name):
            bad_constants.append(name)

    def _extract_names(self, node) -> List[str]:
        """Extrait les noms depuis un nœud cible (Name, Tuple, List)."""
        names = []
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for elt in node.elts:
                names.extend(self._extract_names(elt))
        return names

    def _analyze_js(self, code: str) -> List[str]:
        """Analyse heuristique pour JS/TS."""
        issues = []
        generic_patterns = {
            "tmp", "temp", "data", "result", "res", "val", "value",
            "obj", "item", "foo", "bar", "baz", "test", "var",
        }

        tokens = set(re.findall(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\b', code))
        js_keywords = {
            "const", "let", "var", "function", "return", "if", "else",
            "for", "while", "class", "import", "export", "from", "async",
            "await", "new", "this", "true", "false", "null", "undefined",
        }
        tokens -= js_keywords

        short = [t for t in tokens
                 if len(t) < self.MIN_NAME_LENGTH
                 and t not in self.ACCEPTABLE_SHORT_NAMES
                 and not t.startswith("$")]
        generic = [t for t in tokens if t.lower() in generic_patterns]

        if short:
            issues.append(f"Noms JS trop courts : {', '.join(sorted(short)[:5])}")
        if generic:
            issues.append(f"Noms JS génériques : {', '.join(sorted(generic)[:5])}")
        if not short and not generic:
            issues.append("Noms JS/TS analysés — renommage expressif recommandé")

        return issues

    # ──────────────────────────────────────────
    # Prompt
    # ──────────────────────────────────────────

    def build_prompt(self, code: str, language: str) -> str:
        return f"""You are an expert code refactoring agent specialized in improving naming in {language} code.

### Naming smells to fix
- Variables with non-descriptive single or double-letter names (except accepted conventions: i, j, k, e, f, df, _)
- Generic names that convey no meaning: tmp, temp, data, result, res, val, obj, item, foo, bar
- camelCase variable names in Python code (use snake_case instead)
- Class names not in PascalCase
- Constants not in UPPER_CASE
- Function parameters with non-expressive names
- Loop variables that don't reflect the iterated concept

### Renaming principles
- Name variables by WHAT they represent, not HOW they are used
- Use domain-specific vocabulary from the context of the code
- Prefer concrete nouns for objects: user_record, invoice_total, retry_count
- Prefer verb phrases for booleans: is_valid, has_permission, should_retry
- Prefer verb phrases for functions: calculate_total, fetch_user, validate_input
- Keep names proportional to scope: short scope = shorter name is acceptable
- Follow {language} conventions strictly (snake_case for Python, camelCase for JS)

### Strict constraints
- Preserve EXACT behavior — rename consistently across ALL usages
- Do not change logic, structure, or control flow
- Do not rename: self, cls, magic methods (__init__, __str__...), public API names
- Do not rename well-named identifiers that already follow conventions
- Rename every occurrence of a changed name (definition + all references)

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

        analysis      = self.analyze(code, language)
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