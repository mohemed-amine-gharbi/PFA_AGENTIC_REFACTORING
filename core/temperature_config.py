class TemperatureConfig:
    """
    Configuration optimisée de la température pour chaque type d'agent.
    """
    
    OPTIMAL_TEMPERATURES = {
        "RenameAgent": {
            "default": 0.1,
            "description": "Renommage nécessite de la précision et de la cohérence",
            "range": (0.1, 0.3),
            "icon": "🏷️"
        },
        "ImportAgent": {
            "default": 0.2,
            "description": "Optimisation d'imports est une tâche mécanique",
            "range": (0.1, 0.4),
            "icon": "📦"
        },
        "ComplexityAgent": {
            "default": 0.4,
            "description": "Simplification algorithmique nécessite de la créativité",
            "range": (0.3, 0.6),
            "icon": "🧠"
        },
        "DuplicationAgent": {
            "default": 0.5,
            "description": "Factorisation de code nécessite de l'innovation",
            "range": (0.4, 0.7),
            "icon": "📋"
        },
        "LongFunctionAgent": {
            "default": 0.3,
            "description": "Découpage de fonctions nécessite un bon équilibre",
            "range": (0.2, 0.5),
            "icon": "✂️"
        },
        "MergeAgent": {
            "default": 0.2,
            "description": "Fusion nécessite de la précision pour éviter les conflits",
            "range": (0.1, 0.3),
            "icon": "🔄"
        },
        "PatchAgent": {
            "default": 0.1,
            "description": "Nettoyage nécessite de la rigueur",
            "range": (0.1, 0.3),
            "icon": "🩹"
        }
    }
    
    # Agents spéciaux (température non applicable ou différente)
    SPECIAL_AGENTS = {
        "TestAgent": {
            "description": "Validation automatique avec outils statiques",
            "icon": "🧪",
            "has_temperature": False,
            "note": "Utilise la température pour la correction automatique (0.1)"
        }
    }
    
    @classmethod
    def get_temperature(cls, agent_name):
        """Retourne la température optimale pour un agent"""
        if agent_name in cls.SPECIAL_AGENTS:
            special = cls.SPECIAL_AGENTS[agent_name]
            if special.get("has_temperature", True):
                return special.get("default", 0.3)
            return None  # Pas de température
        
        agent_config = cls.OPTIMAL_TEMPERATURES.get(agent_name, {})
        return agent_config.get("default", 0.3)
    
    @classmethod
    def get_all_configs(cls):
        """Retourne toutes les configurations"""
        configs = {}
        configs.update(cls.OPTIMAL_TEMPERATURES)
        configs.update(cls.SPECIAL_AGENTS)
        return configs
    
    @classmethod
    def get_agent_info(cls, agent_name):
        """Retourne toutes les informations sur un agent"""
        if agent_name in cls.OPTIMAL_TEMPERATURES:
            info = cls.OPTIMAL_TEMPERATURES[agent_name].copy()
            info["has_temperature"] = True
            return info
        elif agent_name in cls.SPECIAL_AGENTS:
            info = cls.SPECIAL_AGENTS[agent_name].copy()
            info["has_temperature"] = info.get("has_temperature", True)
            return info
        return {
            "description": "Agent inconnu", 
            "icon": "❓", 
            "has_temperature": True,
            "default": 0.3
        }