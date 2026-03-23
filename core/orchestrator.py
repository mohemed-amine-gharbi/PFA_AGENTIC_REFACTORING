# ==================== core/orchestrator.py ====================
# Orchestrator unifié avec support de température et nouveaux agents

from agents.rename_agent import RenameAgent
from agents.complexity_agent import ComplexityAgent
from agents.duplication_agent import DuplicationAgent
from agents.import_agent import ImportAgent
from agents.long_function_agent import LongFunctionAgent
from agents.merge_agent import MergeAgent
from agents.test_agent import TestAgent
from agents.patch_agent import PatchAgent
from core.temperature_config import TemperatureConfig

class Orchestrator:
    def __init__(self, llm):
        # Instanciation de tous les agents
        self.agent_instances = {
            "RenameAgent": RenameAgent(llm),
            "ComplexityAgent": ComplexityAgent(llm),
            "DuplicationAgent": DuplicationAgent(llm),
            "ImportAgent": ImportAgent(llm),
            "LongFunctionAgent": LongFunctionAgent(llm),
            "TestAgent": TestAgent(llm),
            "PatchAgent": PatchAgent(llm),
        }
        self.merge_agent = MergeAgent(llm)
        self.temperature_config = TemperatureConfig()

    def run_parallel(self, code, selected_agent_names, language, temperature_override=None):
        """
        Exécute les agents de refactoring en parallèle.
        
        Args:
            code: Code source
            selected_agent_names: Liste des noms d'agents
            language: Langage de programmation
            temperature_override: Température à utiliser pour tous les agents (optionnel)
        """
        results = []

        for name in selected_agent_names:
            agent = self.agent_instances.get(name)
            if agent and name not in ["TestAgent", "PatchAgent", "MergeAgent"]:
                # Déterminer la température à utiliser
                if temperature_override is not None:
                    temp_to_use = temperature_override
                else:
                    # Utiliser la température optimale de l'agent
                    temp_to_use = self.temperature_config.get_temperature(name)
                
                # Appeler apply() avec le paramètre temperature
                result = agent.apply(code, language=language, temperature=temp_to_use)
                results.append(result)

        return results

    def merge_results(self, original_code, selected_results):
        """
        Fusionne le code original avec les propositions sélectionnées.
        """
        if not selected_results:
            return original_code
        
        # Extraire les propositions
        proposals = []
        merge_temperature = 0.2  # Température basse pour la fusion (précision)
        
        for res in selected_results:
            proposal = res.get("proposal", "")
            if proposal and proposal != original_code:
                proposals.append(proposal)
        
        # Utiliser la température pour le merge
        return self.merge_agent.merge(
            original_code, 
            proposals, 
            temperature=merge_temperature
        )
    
    def run_patch_and_test(self, code, language, patch=True, test=True):
        """
        Applique PatchAgent et TestAgent.
        
        Returns:
            tuple: (code_final, patch_result, test_result)
        """
        patch_result = None
        test_result = None

        # Appliquer le patch si demandé
        if patch:
            patch_agent = self.agent_instances.get("PatchAgent")
            if patch_agent:
                patch_result = patch_agent.apply(code, language=language)
                code = patch_result["proposal"]

        # Exécuter les tests si demandé
        if test:
            test_agent = self.agent_instances.get("TestAgent")
            if test_agent:
                test_result = test_agent.apply(code, language=language)

        return code, patch_result, test_result
    
    def get_available_agents(self):
        """Retourne la liste de tous les agents disponibles"""
        return list(self.agent_instances.keys())
    
    def get_refactoring_agents(self):
        """Retourne uniquement les agents de refactoring (sans Test et Patch)"""
        return [name for name in self.agent_instances.keys() 
                if name not in ["TestAgent", "PatchAgent", "MergeAgent"]]