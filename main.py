# ==================== main.py ====================
# Version CLI unifiée

#from core.orchestrator import Orchestrator
from core.langgraph_orchestrator import Orchestrator
from core.ollama_llm_client import OllamaLLMClient
from core.temperature_config import TemperatureConfig
import os
import sys

def main():
    """Point d'entrée CLI unifié"""
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <fichier> [--agents=agent1,agent2] [--temperature=0.3]")
        print("\nAgents disponibles:")
        for agent, config in TemperatureConfig.get_all_configs().items():
            print(f"  - {agent}: {config['description']} (temp: {config['default']})")
        print("  - PatchAgent: Nettoyage avancé du code")
        print("  - TestAgent: Validation automatique")
        return
    
    input_file = sys.argv[1]
    
    # Options par défaut
    selected_agents = None
    temperature = 0.3
    auto_patch = True
    auto_test = True
    
    # Analyser les arguments
    for arg in sys.argv[2:]:
        if arg.startswith("--agents="):
            selected_agents = arg.split("=")[1].split(",")
        elif arg.startswith("--temperature="):
            temperature = float(arg.split("=")[1])
        elif arg == "--no-patch":
            auto_patch = False
        elif arg == "--no-test":
            auto_test = False
        elif arg in ["-h", "--help"]:
            print("\nOptions:")
            print("  --agents=agent1,agent2    Agents à exécuter")
            print("  --temperature=0.3         Température globale")
            print("  --no-patch                Désactiver PatchAgent")
            print("  --no-test                 Désactiver TestAgent")
            print("  -h, --help                Afficher cette aide")
            return
    
    # Vérifier le fichier
    if not os.path.exists(input_file):
        print(f"❌ Fichier introuvable: {input_file}")
        return
    
    # Lire le code
    with open(input_file, "r", encoding="utf-8") as f:
        code = f.read()
    
    # Détecter le langage
    ext = os.path.splitext(input_file)[1].lower()
    language_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".cs": "C#",
        ".go": "Go",
        ".rb": "Ruby",
    }
    language = language_map.get(ext, "Python")
    
    # Initialiser
    print("🔄 Initialisation du système...")
    llm_client = OllamaLLMClient(model_name="mistral:latest")
    orchestrator = Orchestrator(llm_client)
    
    # Si pas d'agents spécifiés, utiliser tous sauf Test et Patch
    if not selected_agents:
        available = orchestrator.get_available_agents()
        selected_agents = [a for a in available if a not in ["TestAgent", "PatchAgent", "MergeAgent"]]
    
    print(f"🔧 Configuration:")
    print(f"  Agents: {', '.join(selected_agents)}")
    print(f"  Langage: {language}")
    print(f"  Température: {temperature}")
    print(f"  Auto-patch: {auto_patch}")
    print(f"  Auto-test: {auto_test}")
    
    # Étape 1: Agents de refactoring
    print("\n🚀 Exécution des agents de refactoring...")
    results = []
    
    for agent_name in selected_agents:
        if agent_name not in ["TestAgent", "PatchAgent", "MergeAgent"]:
            print(f"  ⚡ {agent_name}...")
            agent = orchestrator.agent_instances.get(agent_name)
            if agent:
                # Utiliser la température spécifiée ou celle par défaut
                agent_temp = temperature
                result = agent.apply(code, language, temperature=agent_temp)
                results.append(result)
                print(f"    → {len(result.get('analysis', []))} problèmes détectés")
    
    # Étape 2: Merge
    print("\n🔄 Fusion des résultats...")
    if results:
        merged_code = orchestrator.merge_results(code, results)
    else:
        merged_code = code
    
    # Étape 3: Patch (optionnel)
    patch_result = None
    if auto_patch:
        print("🩹 Application de PatchAgent...")
        patch_agent = orchestrator.agent_instances.get("PatchAgent")
        if patch_agent:
            patch_result = patch_agent.apply(merged_code, language)
            merged_code = patch_result["proposal"]
            print(f"    → {len(patch_result.get('analysis', []))} problèmes corrigés")
    
    # Étape 4: Test (optionnel)
    test_result = None
    if auto_test:
        print("🧪 Exécution de TestAgent...")
        test_agent = orchestrator.agent_instances.get("TestAgent")
        if test_agent:
            test_result = test_agent.apply(merged_code, language)
            status = test_result.get("status", "N/A")
            print(f"    → Statut: {status}")
    
    # Sauvegarder le résultat
    output_file = f"refactored_{os.path.basename(input_file)}"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# ===== Code refactoré par Agentic IA =====\n")
        f.write(f"# Langage: {language}\n")
        f.write(f"# Agents utilisés: {', '.join(selected_agents)}\n")
        if patch_result:
            f.write(f"# PatchAgent: Appliqué\n")
        if test_result:
            f.write(f"# TestAgent: {test_result.get('status', 'N/A')}\n")
        f.write("\n")
        f.write(merged_code)
    
    # Afficher le rapport
    print("\n" + "="*60)
    print("📊 RAPPORT FINAL")
    print("="*60)
    
    for result in results:
        agent_name = result.get("name", "Inconnu")
        analysis = result.get("analysis", [])
        temp_used = result.get("temperature_used", "N/A")
        
        print(f"\n[{agent_name}] (🌡️ {temp_used})")
        if analysis:
            for i, issue in enumerate(analysis[:3], 1):  # Afficher seulement les 3 premiers
                print(f"  {i}. {issue}")
            if len(analysis) > 3:
                print(f"  ... et {len(analysis) - 3} autres")
        else:
            print("  Aucun problème détecté")
    
    if patch_result:
        print("\n[PatchAgent]")
        analysis = patch_result.get("analysis", [])
        for note in analysis:
            if isinstance(note, dict):
                print(f"  - {note.get('note', '')}")
            else:
                print(f"  - {str(note)}")
    
    if test_result:
        print("\n[TestAgent]")
        status = test_result.get("status", "N/A")
        summary = test_result.get("summary", [])
        print(f"  Statut: {status}")
        for line in summary:
            print(f"  - {line}")
    
    print(f"\n✅ Code sauvegardé dans: {output_file}")
    print(f"📝 Taille originale: {len(code)} caractères")
    print(f"📝 Taille finale: {len(merged_code)} caractères")

if __name__ == "__main__":
    main()