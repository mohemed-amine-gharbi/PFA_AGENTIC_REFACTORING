import subprocess
import json
import time


class OllamaLLMClient:
    def __init__(self, model_name, base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url

    def ask(self, system_prompt, user_prompt, temperature=None, max_tokens=2000):
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        try:
            return self._ask_via_api(full_prompt, temperature, max_tokens)
        except Exception as e:
            print(f"⚠️ API Ollama échouée, fallback subprocess: {e}")

            result = self._ask_via_subprocess(full_prompt)

            if result.startswith("Error:"):
                raise Exception(result)

            return result

    def _ask_via_api(self, prompt, temperature=None, max_tokens=2000):
        import requests

        request_data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens
            }
        }

        if temperature is not None:
            request_data["options"]["temperature"] = temperature

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=request_data,
                timeout=400
            )
            response.raise_for_status()

            result = response.json()
            answer = result.get("response", "").strip()

            if not answer:
                raise Exception(f"Réponse Ollama vide: {result}")

            return answer

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur API Ollama: {e}")

    def _ask_via_subprocess(self, prompt):
        try:
            cmd = ["ollama", "run", self.model_name]

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            )

            stdout, stderr = process.communicate(prompt, timeout=400)

            if process.returncode != 0:
                error_msg = stderr.strip() if stderr else f"Code de retour: {process.returncode}"
                return f"Error: {error_msg}"

            result = stdout.strip()

            if not result:
                return "Error: Réponse vide depuis subprocess Ollama"

            return result

        except subprocess.TimeoutExpired:
            process.kill()
            return "Error: Timeout - le modèle a pris trop de temps à répondre"
        except Exception as e:
            return f"Error: {str(e)}"

    def list_models(self):
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)

            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]

            return []

        except Exception:
            try:
                result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")[1:]
                    models = []

                    for line in lines:
                        if line:
                            parts = line.split()
                            if parts:
                                models.append(parts[0])

                    return models

                return []

            except Exception:
                return []

    def test_connection(self):
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False