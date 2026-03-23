# Python Duplication Refactoring Patterns

## Goal
Reduce duplicated code while preserving behavior exactly.

## Types of Duplication
- Exact duplicate blocks
- Near-duplicate blocks (same structure, different literals/fields)
- Repeated loops with same processing shape
- Repeated validation/error handling
- Repeated mapping/formatting logic

## Refactoring Patterns

### 1. Extract Helper Function
**Use when**
- Same block appears 2+ times

**Benefits**
- Single source of truth
- Easier maintenance

**Safety Notes**
- Preserve parameter order and default behavior
- Preserve exceptions and side effects

---

### 2. Parameterize Differences
**Use when**
- Blocks differ only by field names, labels, constants

**Approach**
- Extract helper with parameters
- Pass field names / callbacks / formatters

**Safety Notes**
- Keep exact output format
- Preserve branch-specific behavior if any hidden differences exist

---

### 3. Extract Validation Utility
**Use when**
- Same required-field checks repeated across functions

**Safety Notes**
- Preserve exact error keys/messages if relied upon by callers/tests

---

### 4. Extract Formatter / Serializer
**Use when**
- Same dict-building / response formatting repeated

**Safety Notes**
- Preserve field names and order when important for downstream consumers

---

### 5. Consolidate Repeated Try/Except Structure
**Use when**
- Multiple functions repeat parse / convert / fallback logic

**Safety Notes**
- Preserve exception types caught and fallback return values

---

### 6. Loop Unification (Careful)
**Use when**
- Multiple loops iterate similarly over same data shape

**Safety Notes**
- Preserve mutation timing and append order
- Do not merge loops if intermediate state matters

## What NOT to Do
- Do not over-abstract tiny duplicates if readability decreases
- Do not combine code paths with subtle semantic differences
- Do not introduce generic helpers that obscure domain intent

## DuplicationAgent Heuristics
1. Confirm semantic equivalence before deduplicating
2. Prefer local helper extraction
3. Keep helper names domain-meaningful
4. If uncertain, deduplicate only exact matches