# Refactoring General Patterns (Shared)

## Objectif
Fournir des patterns généraux de refactoring utilisables par plusieurs agents.

---

## 1. Small Safe Steps
- Préférer plusieurs petites modifications sûres à une grosse transformation risquée.
- Après chaque étape : vérifier la cohérence du code.

### Exemple
- Rename variable
- Extract helper function
- Simplify conditional
- Re-run tests

---

## 2. Extract Function / Method
### Quand utiliser
- Bloc de code long
- Responsabilité mélangée
- Logique répétée
- Noms de variables difficiles à comprendre

### Bonnes pratiques
- Choisir un nom explicite
- Passer uniquement les paramètres nécessaires
- Retourner uniquement les résultats nécessaires
- Préserver l’ordre des effets de bord

---

## 3. Guard Clauses
### But
Réduire l’imbrication inutile (nested if/else) pour améliorer lisibilité/complexité cognitive.

### Bonnes pratiques
- Vérifier les cas d’erreur / early exit au début
- Garder le “happy path” visible
- Ne pas modifier la logique de retour

---

## 4. Replace Magic Numbers / Strings
### But
Améliorer la lisibilité via des constantes nommées.

### Attention
- Ne pas extraire si la valeur est purement locale et évidente
- Conserver le bon scope (local/module/class)

---

## 5. Consolidate Duplicate Logic
### But
Factoriser du code dupliqué dans une fonction/helper commun(e).

### Attention
- Ne pas sur-abstraire
- Vérifier que les blocs sont réellement équivalents
- Préserver les différences de comportement subtiles

---

## 6. Simplify Conditionals (Safe)
### Exemples
- Fusionner conditions identiques
- Supprimer `else` après `return` (si sûr)
- Extraire sous-condition complexe dans variable booléenne nommée

### Attention
- Respecter short-circuit
- Respecter ordre d’évaluation
- Ne pas déplacer des appels avec effets de bord

---

## 7. Improve Naming (Local & Safe)
### Cible
- Variables locales
- paramètres internes
- helpers privés

### Bonnes pratiques
- Noms explicites selon rôle métier/technique
- Booléens commencent par `is_`, `has_`, `can_`, `should_` (langage/style dépendant)
- Éviter noms trop courts (`x`, `tmp`, `data`) sauf cas local trivial

### Attention
- Ne pas renommer API publique sans plan
- Ne pas casser reflection/serialization/framework bindings

---

## 8. Imports Cleanup
### But
- Supprimer imports inutilisés
- Dédupliquer
- Organiser l’ordre des imports (si convention)

### Attention
- Effets de bord d’import
- Imports dynamiques
- Imports seulement utilisés dans type hints / runtime conditionnel

---

## 9. Long Function Decomposition
### Techniques
- Extract helpers par responsabilité
- Isoler validation
- Isoler transformation de données
- Isoler I/O

### Attention
- Préserver variables mutées / closures / state partagé
- Préserver ordre exact des étapes

---

## 10. Refactoring Output Rules (pour LLM agents)
Quand un agent propose une modification :
1. Mentionner brièvement les problèmes détectés
2. Fournir le code refactoré complet (ou patch clair)
3. Expliquer pourquoi la sémantique est préservée
4. Mentionner les limites / risques éventuels

---

## Anti-patterns à éviter
- “Big rewrite” sans nécessité
- Changement de style + logique en même temps
- Optimisations prématurées
- Abstractions inutiles
- Renommages massifs non maîtrisés