# Python Long Function Refactoring Patterns

## Goal
Split overly long functions into smaller, understandable units while preserving behavior.

## Long Function Smells
- >20-40 lines with mixed responsibilities
- Validation + transformation + persistence + formatting in one function
- Many nested branches
- Repeated temporary variables across unrelated steps
- Hard-to-name variables due to overloaded logic

## Refactoring Patterns

### 1. Extract Validation Phase
- Move input checks into `_validate_*` helper
- Keep exact exception types/messages

### 2. Extract Transformation Phase
- Move parsing/normalization into `_normalize_*` helper
- Preserve conversion rules and fallback behavior

### 3. Extract Persistence / Side-Effect Phase
- Move DB/file/network actions into `_save_*` / `_execute_*`
- Preserve ordering relative to logs and mutations

### 4. Extract Formatting / Response Phase
- Return final dict/object via helper to reduce clutter

### 5. Introduce Orchestrator Function Shape
Keep public function as:
1. validate
2. transform
3. execute
4. format result

This makes code easier to follow while preserving the same API.

## Safety Rules
- Do not change function signature unless requested
- Preserve order of side effects (DB, logging, notifications)
- Preserve mutation timing
- Preserve exceptions and return shape
- Avoid splitting tiny functions excessively (over-fragmentation)

## LongFunctionAgent Heuristics
1. Extract only coherent blocks
2. Keep helper names descriptive
3. Prefer private helpers (`_name`) for internal refactors
4. Minimal safe split if uncertainty exists