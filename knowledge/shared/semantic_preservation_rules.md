# Semantic Preservation Rules (Shared)

## Objectif
Toutes les transformations de refactoring doivent préserver le comportement fonctionnel du code.

## Règles obligatoires (tous agents)

### 1. Préservation du comportement
- Ne pas changer les valeurs de retour.
- Ne pas changer les effets de bord.
- Ne pas changer les exceptions levées (type/message/moment si possible).
- Ne pas changer l’ordre d’exécution des opérations sensibles.

### 2. Préservation des APIs
- Ne pas modifier les signatures publiques (noms de fonctions, paramètres, ordre des paramètres) sauf demande explicite.
- Ne pas renommer les classes/fonctions exportées publiquement sans stratégie de migration.
- Ne pas casser les points d’entrée existants.

### 3. Préservation de la logique conditionnelle
- Conserver la logique booléenne exacte.
- Respecter le short-circuit (`and`, `or`).
- Éviter les simplifications risquées qui changent les cas limites.

### 4. Préservation des mutations / état
- Ne pas modifier le timing des mutations (append, update, assignment, DB writes, file writes).
- Ne pas déplacer des effets de bord hors de leur contexte sans preuve de sécurité.
- Respecter les états globaux / partagés / caches.

### 5. Préservation I/O et environnement
- Conserver les appels I/O (fichiers, réseau, logs) et leur ordre.
- Ne pas supprimer des logs fonctionnels sans validation.
- Ne pas modifier la gestion du temps, hasard, seeds, timestamps.

### 6. Imports et dépendances
- Ne pas supprimer un import si son import déclenche un effet de bord au chargement.
- Conserver les imports nécessaires à la compatibilité runtime/type checking.

### 7. Exceptions et erreurs
- Conserver les `try/except/finally` et leur sémantique.
- Ne pas transformer silencieusement une exception en comportement différent.
- Préserver les messages critiques si utilisés par tests/monitoring.

## Règle de sécurité
Si un refactor peut améliorer la lisibilité mais risque de changer la sémantique :
- **ne pas l’appliquer**
- ou proposer le changement avec mention explicite du risque.

## Stratégie de validation recommandée
Avant d’accepter un refactor :
1. Vérification syntaxique
2. Tests unitaires / statiques
3. Comparaison comportementale sur cas critiques
4. Review des effets de bord

## Priorité
La préservation sémantique est prioritaire sur :
- style
- concision
- “élégance”
- optimisation micro-performance