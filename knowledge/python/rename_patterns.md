# Python Rename Refactoring Patterns

## Goal
Improve readability by renaming unclear identifiers while preserving behavior and compatibility.

## Naming Rules (Python)
- Use `snake_case` for variables and functions
- Use `PascalCase` for classes
- Use descriptive names over short ambiguous names
- Boolean variables should read like predicates:
  - `is_valid`, `has_items`, `can_publish`, `should_retry`

## Common Rename Smells
- Single-letter names outside tiny loops (`x`, `d`, `n`, `k`)
- Ambiguous names (`data`, `obj`, `tmp`, `res`)
- Misleading names (`users` for a single user)
- Non-domain names where domain concept is clear
- Inconsistent naming in same scope

## Safe Rename Strategy
1. Rename local variables first
2. Rename private helpers next
3. Rename loop variables only if unclear
4. Avoid renaming public API names unless explicitly allowed
5. Avoid renaming framework-required names
6. Avoid renaming imported symbols if it may break module contracts

## Good Rename Examples
- `x` -> `items`
- `n` -> `item_count`
- `res` -> `response`
- `d` -> `payload` / `data` (if domain unknown)
- `ok` -> `is_success` / `is_allowed`

## What NOT to Do
- Do not rename public methods used externally without permission
- Do not rename magic names (`__init__`, framework hooks)
- Do not rename variables if the new name is speculative and may be wrong
- Do not rename if it hurts readability more than it helps

## RenameAgent Heuristics
- Prefer high-confidence renames only
- Preserve semantics and references
- Keep changes minimal and clear
