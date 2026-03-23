# Project Conventions (PFE Agentic Refactoring) - Shared

## Objectif
Décrire les conventions de ce projet multi-agents de refactoring afin que les agents produisent des résultats compatibles avec l’architecture existante.

---

## 1. Architecture globale
Le projet est organisé autour de :
- plusieurs agents de refactoring spécialisés (Rename, Complexity, Duplication, Import, LongFunction)
- un orchestrateur (linéaire ou LangGraph)
- des agents de post-traitement/validation (PatchAgent, TestAgent)
- une configuration de température par agent (`TemperatureConfig`)

Les agents retournent un format standardisé de résultat.

---

## 2. Contrat de sortie standard des agents
Un agent doit retourner un dictionnaire avec au minimum :
- `name`
- `analysis`
- `proposal`

Optionnel :
- `temperature_used`
- autres métadonnées spécifiques (`warnings`, `metrics`, etc.)

### Exemple minimal
```python
{
    "name": "ComplexityAgent",
    "analysis": [...],
    "proposal": "...refactored code..."
}