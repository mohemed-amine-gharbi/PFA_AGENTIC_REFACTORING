# Python Complexity Refactoring Patterns

## Goal
Reduce cyclomatic/cognitive complexity while preserving exact behavior.

## Core Principles
- Preserve semantics exactly (outputs, exceptions, side effects, order of execution)
- Prefer small safe refactors over aggressive rewrites
- Improve readability and maintainability
- Keep public APIs unchanged unless explicitly requested

## Common Complexity Smells
- Deeply nested `if/elif/else`
- Long functions mixing multiple responsibilities
- Repeated conditional branches
- Complex boolean expressions
- Nested loops with multiple responsibilities
- Implicit control flow (flags, break/continue scattered everywhere)
- Duplicate control-flow patterns

## Refactoring Patterns

### 1. Guard Clauses / Early Return
**Use when**
- Function has nested validations or preconditions

**Before**
- `if ...: if ...: if ...: main logic`

**After**
- Return early for invalid conditions, keep main path flat

**Benefits**
- Reduces nesting
- Improves readability

**Safety Notes**
- Keep same return values and exception behavior
- Do not change evaluation order of side effects

---

### 2. Extract Helper Function
**Use when**
- A block of code performs a distinct sub-task
- Repeated logic appears in multiple places

**Benefits**
- Smaller functions
- Better testability
- Easier reasoning

**Safety Notes**
- Preserve parameters and data dependencies
- Do not accidentally capture mutable shared state differently

---

### 3. Split Function by Responsibility
**Use when**
- One function validates, transforms, persists, logs, and formats result all at once

**Approach**
- Separate validation / transformation / persistence / formatting helpers

**Safety Notes**
- Preserve execution order (especially DB writes, logs, API calls)
- Preserve raised exceptions and messages if relied upon

---

### 4. Simplify Boolean Logic
**Use when**
- Complex boolean expressions are hard to read
- Repeated negations, chained conditions, nested booleans

**Approach**
- Extract named predicates:
  - `is_valid_user(...)`
  - `has_access(...)`

**Safety Notes**
- Preserve short-circuit semantics
- Preserve laziness if condition includes function calls with side effects

---

### 5. Replace Repeated Branch Bodies with Dispatch (Carefully)
**Use when**
- Many `if/elif` branches map simple keys to handlers or values

**Approach**
- Use dictionary mapping or handler functions

**Safety Notes**
- Only if branch order does not change behavior
- Be careful with fallbacks/default behavior and exceptions

---

### 6. Flatten Nested Loops by Extracting Inner Logic
**Use when**
- Nested loops contain dense conditional logic

**Approach**
- Extract inner operation into helper
- Use clear variable names
- Optionally continue early for skipped cases

**Safety Notes**
- Preserve loop order and mutation timing
- Preserve append/update side effects exactly

---

### 7. Introduce Intermediate Variables with Meaningful Names
**Use when**
- A single line contains many chained operations or conditions

**Benefits**
- Lower cognitive load
- Easier debugging

**Safety Notes**
- Avoid changing evaluation timing when functions have side effects

---

### 8. Consolidate Duplicate Conditions
**Use when**
- Same condition repeated in multiple branches

**Approach**
- Compute once into a named predicate or normalize branching structure

**Safety Notes**
- Ensure condition is evaluated same number of times if side effects exist

---

## What NOT to Do (Unless Explicitly Safe)
- Do not change public function signatures
- Do not replace loops with comprehensions if side effects / ordering become unclear
- Do not introduce caching/memoization (behavior/performance semantics may change)
- Do not silently catch exceptions
- Do not change logging behavior
- Do not reorder validations if exceptions differ

## ComplexityAgent Decision Heuristics
1. Prefer guard clauses first
2. Then extract helpers for repeated / dense blocks
3. Then simplify boolean logic
4. Avoid structural rewrites if uncertain
5. If risk of semantic drift is high, return minimal refactor