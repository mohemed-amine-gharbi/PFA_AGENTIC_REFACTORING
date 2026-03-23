# core/experiment_report.py

class TemperatureExperimentReport:
    """
    Génère des rapports sur l'impact de la température.
    """

    @staticmethod
    def generate_report(experiment_results):
        """Génère un rapport détaillé"""
        
        report = {
            "summary": {
                "total_experiments": len(experiment_results),
                "agents_tested": list(set(
                    agent["name"] 
                    for exp in experiment_results 
                    for agent in exp.get("results", [])
                ))
            },
            "findings": [],
            "recommendations": []
        }
        
        # Analyser l'impact sur chaque agent
        agent_performance = {}
        
        for exp in experiment_results:
            temp = exp["temperature"]
            
            for agent_result in exp.get("results", []):
                agent_name = agent_result["name"]
                
                if agent_name not in agent_performance:
                    agent_performance[agent_name] = []
                
                # Mesures de qualité (simples)
                proposal = agent_result["proposal"]
                quality_metrics = {
                    "temperature": temp,
                    "length": len(proposal),
                    "lines": len(proposal.split('\n')),
                    "unique_tokens": len(set(proposal.split())),
                    "readability_score": calculate_readability(proposal)  # À implémenter
                }
                
                agent_performance[agent_name].append(quality_metrics)
        
        # Générer des recommandations basées sur les données
        for agent, metrics_list in agent_performance.items():
            # Trouver la température optimale (longueur la plus cohérente)
            optimal_temp = TemperatureExperimentReport._find_optimal_temperature(metrics_list)
            
            report["findings"].append({
                "agent": agent,
                "optimal_temperature": optimal_temp,
                "performance_by_temperature": metrics_list
            })

            
            def calculate_readability(code: str) -> float:
                lines = code.splitlines()
                if not lines:
                    return 0.0

                avg_len = sum(len(l) for l in lines) / len(lines)
                return round(100 / (1 + avg_len), 2)
        return report
    
    
    @staticmethod
    def _find_optimal_temperature(metrics_list):
        """Trouve la température optimale basée sur les métriques"""
        # Simplifié : choisit la température avec la longueur la plus cohérente
        if not metrics_list:
            return 0.3
        
        # Calculer l'écart-type des longueurs pour chaque température
        temp_to_lengths = {}
        for metrics in metrics_list:
            temp = metrics["temperature"]
            if temp not in temp_to_lengths:
                temp_to_lengths[temp] = []
            temp_to_lengths[temp].append(metrics["length"])
        
        # Trouver la température avec le plus petit écart-type
        optimal_temp = 0.3
        min_std = float('inf')
        
        for temp, lengths in temp_to_lengths.items():
            if len(lengths) > 1:
                import statistics
                std = statistics.stdev(lengths)
                if std < min_std:
                    min_std = std
                    optimal_temp = temp
        
        return optimal_temp
