import subprocess
import json
import time

class OllamaLLMClient:
    def __init__(self, model_name, base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
    
    def ask(self, system_prompt, user_prompt, temperature=None, max_tokens=2000):
        """
        Envoie le prompt au modèle Ollama local avec support de température.
        
        Args:
            system_prompt: Prompt système
            user_prompt: Prompt utilisateur
            temperature: Température pour la génération (0.0-1.0)
            max_tokens: Nombre maximum de tokens à générer
        
        Returns:
            str: Réponse du modèle
        """
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            # Méthode 1: Utiliser l'API REST d'Ollama (recommandée)
            return self._ask_via_api(full_prompt, temperature, max_tokens)
        except Exception as e:
            # Méthode 2: Fallback avec subprocess
            print(f"⚠️ API Ollama échouée, fallback subprocess: {e}")
            return self._ask_via_subprocess(full_prompt)
    
    def _ask_via_api(self, prompt, temperature=None, max_tokens=2000):
        """Utilise l'API REST d'Ollama"""
        import requests
        
        request_data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens
            }
        }
        
        # Ajouter la température si spécifiée
        if temperature is not None:
            request_data["options"]["temperature"] = temperature
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=request_data,
                timeout=120  # 2 minutes timeout
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur API Ollama: {e}")
    
    def _ask_via_subprocess(self, prompt):
        """Méthode de fallback avec subprocess"""
        try:
            # Préparer la commande
            cmd = ["ollama", "run", self.model_name]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            )
            
            stdout, stderr = process.communicate(prompt, timeout=60)
            
            if process.returncode != 0:
                error_msg = stderr.strip() if stderr else f"Code de retour: {process.returncode}"
                return f"Error: {error_msg}"
            
            return stdout.strip()
            
        except subprocess.TimeoutExpired:
            process.kill()
            return "Error: Timeout - le modèle a pris trop de temps à répondre"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def list_models(self):
        """Liste les modèles disponibles localement"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except:
            # Fallback avec commande
            try:
                result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Ignorer l'en-tête
                    models = []
                    for line in lines:
                        if line:
                            parts = line.split()
                            if parts:
                                models.append(parts[0])
                    return models
                return []
            except:
                return []
    
    def test_connection(self):
        """Teste la connexion à Ollama"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False