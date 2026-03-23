# Python Import Refactoring Patterns

## Goal
Improve import hygiene while preserving runtime behavior.

## Common Import Smells
- Unused imports
- Duplicate imports
- Imports inside functions without reason (or with no comment)
- Wildcard imports (`from x import *`)
- Inconsistent grouping/order
- Aliases with unclear names
- Circular import workarounds used incorrectly

## Refactoring Patterns

### 1. Remove Unused Imports
**Use when**
- Imported names are never referenced

**Safety Notes**
- Watch for imports used for side effects
- Watch for typing-only imports (`TYPE_CHECKING`)
- Watch for framework/plugin registration imports

---

### 2. Merge Duplicate Imports
**Use when**
- Same module imported multiple times

**Safety Notes**
- Preserve aliasing if actually used differently

---

### 3. Replace Wildcard Imports with Explicit Imports
**Use when**
- Readability / maintainability issue

**Safety Notes**
- Risky if many symbols implicit; apply only when used names are clear

---

### 4. Group and Order Imports
Typical order (PEP8 style):
1. Standard library
2. Third-party
3. Local application imports

**Safety Notes**
- Reordering can affect behavior in rare side-effectful imports
- Be conservative if imports trigger initialization

---

### 5. Keep Intentional Local Imports
**Use when**
- Imports are inside function for lazy loading / optional dependency / circular import fix

**Rule**
- Do not move local imports unless clearly safe and requested

## What NOT to Do
- Do not remove imports used indirectly by decorators/metaclasses/plugins if uncertain
- Do not reorder imports that may alter side effects
- Do not force style-only changes if they risk behavior

## ImportAgent Heuristics
1. Prefer removing clearly unused imports
2. Keep side-effect imports unless explicit evidence they are safe to remove
3. Be conservative around optional imports and `try/except ImportError`