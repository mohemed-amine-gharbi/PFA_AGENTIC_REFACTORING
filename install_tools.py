# ==================== install_tools.py ====================

import subprocess
import sys

def install_python_tools():
    """Installe les outils Python requis"""
    tools = ["ruff", "black", "mypy", "pylint"]
    
    print("🔧 Installation des outils Python...")
    for tool in tools:
        print(f"  Installing {tool}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", tool])
            print(f"    ✅ {tool} installé")
        except subprocess.CalledProcessError as e:
            print(f"    ❌ Erreur installation {tool}: {e}")

def check_installations():
    """Vérifie les installations"""
    print("🔍 Vérification des installations...")
    
    import importlib.util
    
    tools_to_check = {
        "ruff": "ruff",
        "black": "black",
        "mypy": "mypy",
        "pylint": "pylint",
    }
    
    for tool_name, module_name in tools_to_check.items():
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            print(f"  ✅ {tool_name}: Installé")
        else:
            print(f"  ❌ {tool_name}: Non installé")
            print(f"     Installez avec: pip install {tool_name}")

if __name__ == "__main__":
    print("🛠️ Installation des outils pour Agentic IA Refactoring")
    print("=" * 50)
    
    install_python_tools()
    print("\n" + "=" * 50)
    check_installations()