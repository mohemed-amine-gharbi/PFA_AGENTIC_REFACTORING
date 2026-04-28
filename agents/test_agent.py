# ==================== agents/test_agent.py ====================

from .base_agent import BaseAgent
from pathlib import Path
import subprocess
import tempfile
import os
import sys
import re


class StaticTools:
    """
    Outils d'analyse statique avec gestion des erreurs d'installation.
    """
    def __init__(self, repo_path: Path, language: str):
        self.repo_path = repo_path
        self.language = language.lower()
        self.available_tools = self._detect_available_tools()

    def _detect_available_tools(self):
        """Détecte les outils disponibles sur le système"""
        available = {}
        tools = [
            "python", "ruff", "black", "mypy", "coverage",
            "npm", "npx", "node",
            "javac", "mvn", "gradle",
            "gcc", "g++", "make",
            "go",
            "ruby", "rspec"
        ]

        for tool in tools:
            try:
                subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    check=False,
                    timeout=5
                )
                available[tool] = True
            except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
                available[tool] = False

        return available

    def run(self, cmd, tool_name=None):
        """
        Exécute une commande avec gestion d'erreur améliorée.

        Returns:
            tuple: (status_code, output, error_message)
        """
        if tool_name and not self.available_tools.get(tool_name, False):
            return -1, "", f"Outil '{tool_name}' non disponible. Installez-le d'abord."

        try:
            p = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=30
            )
            output = (p.stdout or "") + "\n" + (p.stderr or "")
            return p.returncode, output.strip(), ""
        except FileNotFoundError:
            return -1, "", f"Commande introuvable : {cmd[0]}"
        except subprocess.TimeoutExpired:
            return -1, "", f"Timeout : commande {cmd[0]} trop longue"
        except Exception as e:
            return -1, "", f"Erreur d'exécution : {str(e)}"

    def python_syntax(self, filename):
        return self.run(["python", "-m", "py_compile", filename], "python")

    def ruff(self):
        return self.run(["ruff", "check", ".", "--exit-zero"], "ruff")

    def black_check(self):
        return self.run(["black", "--check", "."], "black")

    def mypy(self):
        return self.run(["mypy", "."], "mypy")


    def jest(self):
        return self.run(["npx", "jest", "--passWithNoTests"], "npx")

    def maven_test(self):
        return self.run(["mvn", "test"], "mvn")

    def go_test(self):
        return self.run(["go", "test", "./..."], "go")

    def rspec(self):
        return self.run(["rspec"], "rspec")


class TestAgent(BaseAgent):
    """
    Agent de validation - teste uniquement, sans correction automatique.
    """

    def __init__(self, llm):
        super().__init__(llm, name="TestAgent")

    def analyze(self, code, language):
        """
        Analyse le code avec gestion élégante des outils manquants.
        """
        lang_key = language.lower()
        report = {
            "status": "SUCCESS",
            "summary": [],
            "details": [],
            "warnings": [],
            "metrics": {},
            "tools_available": True
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)

            extensions = {
                "python": ".py",
                "javascript": ".js",
                "typescript": ".ts",
                "java": ".java",
                "c": ".c",
                "cpp": ".cpp",
                "go": ".go",
                "ruby": ".rb"
            }

            ext = extensions.get(lang_key, ".py")
            filename = f"test_code{ext}"
            file_path = path / filename
            file_path.write_text(code, encoding="utf-8")

            tools = StaticTools(path, language)

            # ================= PYTHON =================
            if lang_key == "python":

                ret, out, err = tools.python_syntax(filename)
                status = "SUCCESS" if ret == 0 else "FAILED"
                detail = {
                    "tool": "python_syntax",
                    "status": status,
                    "return_code": ret,
                    "output": out or "Syntaxe Python valide",
                    "error": err
                }
                if err:
                    detail["suggestion"] = "Utilisez 'python -m py_compile fichier.py' pour vérifier manuellement"
                report["details"].append(detail)
                if ret != 0:
                    report["status"] = "FAILED"
                    report["summary"].append("❌ Erreur de syntaxe Python détectée")
                    if out:
                        for line in out.split("\n")[:3]:
                            if line.strip():
                                report["summary"].append(f"   → {line.strip()}")

                ret, out, err = tools.ruff()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ Ruff non installé - impossible de vérifier le style")
                    report["tools_available"] = False
                else:
                    status = "SUCCESS" if ret == 0 else "WARNING"
                    report["details"].append({
                        "tool": "ruff",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Aucun problème de style détecté",
                        "error": err
                    })
                    if ret != 0:
                        report["summary"].append("⚠️ Problèmes de style détectés (Ruff)")
                        if report["status"] == "SUCCESS":
                            report["status"] = "WARNING"

                ret, out, err = tools.black_check()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ Black non installé - impossible de vérifier le formatage")
                else:
                    status = "SUCCESS" if ret == 0 else "WARNING"
                    report["details"].append({
                        "tool": "black",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Formatage correct (Black)",
                        "error": err
                    })
                    if ret != 0:
                        report["warnings"].append("Code nécessite un reformatage avec Black")
                        if report["status"] == "SUCCESS":
                            report["status"] = "WARNING"

                ret, out, err = tools.mypy()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ mypy non installé - impossible de vérifier les types")
                else:
                    status = "SUCCESS" if ret == 0 else "WARNING"
                    report["details"].append({
                        "tool": "mypy",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Aucune erreur de type",
                        "error": err
                    })
                    if ret != 0:
                        report["warnings"].append("Problèmes de typage détectés")
                        if report["status"] == "SUCCESS":
                            report["status"] = "WARNING"


            # ================= JAVASCRIPT / TYPESCRIPT =================
            elif lang_key in ["javascript", "typescript"]:

                ret, out, err = tools.jest()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ Jest non installé - tests ignorés")
                else:
                    status = "SUCCESS" if ret == 0 else "FAILED"
                    report["details"].append({
                        "tool": "jest",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Tous les tests Jest passent",
                        "error": err
                    })
                    if ret != 0:
                        report["status"] = "FAILED"
                        report["summary"].append("❌ Tests Jest échoués")

            # ================= JAVA =================
            elif lang_key == "java":

                ret, out, err = tools.maven_test()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ Maven non installé - tests ignorés")
                else:
                    status = "SUCCESS" if ret == 0 else "FAILED"
                    report["details"].append({
                        "tool": "maven",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Tests Maven réussis",
                        "error": err
                    })
                    if ret != 0:
                        report["status"] = "FAILED"
                        report["summary"].append("❌ Tests Maven échoués")

            # ================= GO =================
            elif lang_key == "go":

                ret, out, err = tools.go_test()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ Go non installé - tests ignorés")
                else:
                    status = "SUCCESS" if ret == 0 else "FAILED"
                    report["details"].append({
                        "tool": "go test",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Tests Go réussis",
                        "error": err
                    })
                    if ret != 0:
                        report["status"] = "FAILED"
                        report["summary"].append("❌ Tests Go échoués")

            # ================= RUBY =================
            elif lang_key == "ruby":

                ret, out, err = tools.rspec()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ RSpec non installé - tests ignorés")
                else:
                    status = "SUCCESS" if ret == 0 else "FAILED"
                    report["details"].append({
                        "tool": "rspec",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Tests RSpec réussis",
                        "error": err
                    })
                    if ret != 0:
                        report["status"] = "FAILED"
                        report["summary"].append("❌ Tests RSpec échoués")

            # ================= METRICS =================
            self._calculate_basic_metrics(code, report, lang_key)

            return report

    def _calculate_basic_metrics(self, code, report, language):
        """Calcule les métriques de base sans outils externes"""
        lines = code.splitlines()
        non_empty_lines = [l for l in lines if l.strip()]

        report["metrics"] = {
            "total_lines": len(lines),
            "non_empty_lines": len(non_empty_lines),
            "characters": len(code),
            "average_line_length": sum(len(l) for l in lines) / max(1, len(lines))
        }

        warnings = []

        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            warnings.append(f"Lignes trop longues (>120 chars): {long_lines[:3]}")

        if language == "python":
            indent_sizes = set()
            for line in non_empty_lines:
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indent_sizes.add(indent)

            if len(indent_sizes) > 2:
                warnings.append("Indentation incohérente détectée")

        if warnings:
            report["warnings"].extend(warnings)

    def apply(self, code, language, temperature=None):
        """
        Applique uniquement l'analyse - aucune correction automatique.
        """
        analysis = self.analyze(code, language)

        return {
            "name": self.name,
            "status": analysis.get("status", "N/A"),
            "summary": analysis.get("summary", []),
            "details": analysis.get("details", []),
            "warnings": analysis.get("warnings", []),
            "metrics": analysis.get("metrics", {}),
            "tools_available": analysis.get("tools_available", True),
            "proposal": code,
            "temperature_used": temperature if temperature is not None else "N/A"
        }