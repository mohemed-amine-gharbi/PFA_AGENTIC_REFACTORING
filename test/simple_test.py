#!/usr/bin/env python3
"""
Script de test simple et rapide
Parfait pour tester rapidement quelques configurations
"""

import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_batch_test import AdvancedBatchTester

# Configuration simple directement dans le code
SIMPLE_CONFIG = {
    "description": "Configuration de test simple",
    "input_directory": "bad_codes",
    "output_directory": "test_results",
    "model": "mistral:latest",
    
    "test_configurations": [
        # Test 1: RenameAgent avec température basse
        {
            "id": "T1-Rename-Low",
            "name": "RenameAgent (Temp 0.1)",
            "description": "Test conservateur du RenameAgent",
            "agents": [
                {"name": "RenameAgent", "temperature": 0.1},
      
            ]
        },
        
        # Test 2: RenameAgent avec température moyenne
        {
            "id": "T2-Rename-Med",
            "name": "RenameAgent (Temp 0.3)",
            "description": "Test équilibré du RenameAgent",
            "agents": [
                {"name": "RenameAgent", "temperature": 0.3},
 
            ]
        },
        
        # Test 3: ImportAgent
        {
            "id": "T3-Import",
            "name": "ImportAgent (Temp 0.3)",
            "description": "Test de l'ImportAgent",
            "agents": [
                {"name": "ImportAgent", "temperature": 0.3},
       
            ]
        },
        
        # Test 4: Combinaison Rename + Import
        {
            "id": "T4-Combo",
            "name": "Rename + Import",
            "description": "Combinaison de deux agents",
            "agents": [
                {"name": "RenameAgent", "temperature": 0.3},
                {"name": "ImportAgent", "temperature": 0.3},
              
            ]
        }
    ],
    
    "output_options": {
        "save_refactored_code": True,
        "save_error_logs": True,
        "generate_excel_report": True,
        "generate_json_report": False
    }
}


def save_config(config, filename="simple_test_config.json"):
    """Sauvegarde la configuration dans un fichier JSON"""
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"💾 Configuration sauvegardée: {filename}")
    return filename


def main():
    """Fonction principale"""
    
    print("=" * 70)
    print("🧪 Script de Test Simple")
    print("=" * 70)
    print()
    
    # Vérifier que le répertoire bad_codes existe et contient des fichiers
    bad_codes_dir = Path("bad_codes")
    if not bad_codes_dir.exists():
        print("❌ Le répertoire 'bad_codes' n'existe pas!")
        print("   Créez-le et placez-y vos fichiers bad_code*.py")
        print()
        print("   Ou utilisez le générateur:")
        print("   python3 generate_test_files.py --count 50")
        return
    
    files = list(bad_codes_dir.glob("bad_code*.py"))
    if not files:
        print("❌ Aucun fichier bad_code*.py trouvé dans 'bad_codes/'")
        print()
        print("   Utilisez le générateur:")
        print("   python3 generate_test_files.py --count 50")
        return
    
    print(f"📁 {len(files)} fichiers trouvés dans 'bad_codes/'")
    print()
    
    # Afficher la configuration
    print("⚙️  Configuration des tests:")
    for i, config in enumerate(SIMPLE_CONFIG['test_configurations'], 1):
        agents_str = ", ".join([f"{a['name']}(T={a['temperature']})" for a in config['agents']])
        print(f"   {i}. {config['name']}: {agents_str}")
    print()
    
    # Calculer le nombre total de tests
    total_tests = len(files) * len(SIMPLE_CONFIG['test_configurations'])
    print(f"📊 Total de tests à exécuter: {total_tests}")
    print(f"   ({len(files)} fichiers × {len(SIMPLE_CONFIG['test_configurations'])} configurations)")
    print()
    
    # Demander confirmation
    response = input("🚀 Voulez-vous lancer les tests ? (o/n): ")
    if not response.lower().startswith('o'):
        print("❌ Tests annulés")
        return
    
    print()
    print("=" * 70)
    print()
    
    # Sauvegarder la configuration
    config_file = save_config(SIMPLE_CONFIG)
    print()
    
    # Créer le testeur et lancer les tests
    try:
        tester = AdvancedBatchTester(config_file=config_file)
        tester.run_all_tests()
        
        # Exporter les résultats
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = f"simple_test_results_{timestamp}.xlsx"
        tester.export_to_excel(filename=excel_file)
        
        print()
        print("=" * 70)
        print("✅ Tests terminés avec succès!")
        print()
        print(f"📊 Résultats disponibles dans:")
        print(f"   - test_results/{excel_file}")
        print()
        print("📁 Code refactoré disponible dans:")
        print(f"   - test_results/")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Tests interrompus par l'utilisateur")
    except Exception as e:
        print()
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
