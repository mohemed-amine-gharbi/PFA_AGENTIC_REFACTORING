# ==================== setup.py ====================

import subprocess
import sys
import os

def print_header(text):
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def run_command(cmd, description):
    print(f"\n🔧 {description}...")
    print(f"   Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Succès")
            return True
        else:
            print(f"   ⚠️ Avertissement: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def main():
    print_header("🛠️ SETUP - Agentic IA Refactoring System")
    
    # 1. Vérifier Python
    print(f"\n🐍 Python version: {sys.version}")
    
    # 2. Installer les dépendances principales
    print_header("1. Installation des dépendances principales")
    
    dependencies = [
        "streamlit>=1.28.0",
        "pandas>=2.0.0", 
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
    ]
    
    for dep in dependencies:
        run_command([sys.executable, "-m", "pip", "install", dep], f"Installation de {dep}")
    
    # 3. Installer les outils d'analyse
    print_header("2. Installation des outils d'analyse (optionnel)")
    
    print("\n📋 Les outils suivants sont recommandés pour TestAgent:")
    print("   - ruff: Analyse de style Python")
    print("   - black: Formateur de code")
    print("   - mypy: Vérificateur de types")
    print("   - pylint: Analyseur statique")
    
    response = input("\nInstaller ces outils ? (o/N): ").strip().lower()
    if response in ['o', 'oui', 'y', 'yes']:
        analysis_tools = ["ruff", "black", "mypy", "pylint"]
        for tool in analysis_tools:
            run_command([sys.executable, "-m", "pip", "install", tool], f"Installation de {tool}")
    
    # 4. Vérifier Ollama
    print_header("3. Vérification d'Ollama")
    
    print("\n🤖 Ollama est requis pour les modèles locaux.")
    print("   Téléchargez-le depuis: https://ollama.ai/")
    
    # Tester la connexion Ollama
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Ollama détecté: {result.stdout.strip()}")
            
            # Proposer de télécharger un modèle
            print("\n📥 Modèles disponibles:")
            models = ["mistral:latest", "llama2:latest", "codellama:latest"]
            for i, model in enumerate(models, 1):
                print(f"   {i}. {model}")
            
            response = input("\nTélécharger un modèle ? (1-3 ou Enter pour ignorer): ").strip()
            if response in ['1', '2', '3']:
                model = models[int(response)-1]
                run_command(["ollama", "pull", model], f"Téléchargement de {model}")
        else:
            print("   ❌ Ollama non trouvé. Installez-le d'abord.")
    except FileNotFoundError:
        print("   ❌ Ollama non installé. Téléchargez depuis https://ollama.ai/")
    
    # 5. Créer la structure des dossiers
    print_header("4. Structure des dossiers")
    
    folders = ["agents", "core", "diagnostics", "examples", "refactoring", "tests"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"   📁 Créé: {folder}/")
    
    # 6. Fichier de configuration
    print_header("5. Fichier de configuration")
    
    env_content = """# Configuration Agentic IA Refactoring

# OpenAI API (optionnel)
# OPENAI_API_KEY=your-openai-api-key-here

# Ollama (recommandé)
OLLAMA_MODEL=mistral:latest
OLLAMA_BASE_URL=http://localhost:11434

# Températures par défaut
DEFAULT_TEMPERATURE=0.3

# Validation
ENABLE_AUTO_PATCH=true
ENABLE_AUTO_TEST=true
"""
    
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_content)
    print("   📄 Créé: .env.example (copiez en .env et modifiez)")
    
    print_header("✅ SETUP TERMINÉ")
    
    print("\n🎯 Pour démarrer:")
    print("   1. Copiez .env.example vers .env")
    print("   2. Configurez vos clés API si nécessaire")
    print("   3. Démarrez Ollama: ollama serve")
    print("   4. Lancez l'interface: streamlit run app.py")
    print("\n   Ou en CLI: python main.py examples/bad_code.py")

if __name__ == "__main__":
    main()