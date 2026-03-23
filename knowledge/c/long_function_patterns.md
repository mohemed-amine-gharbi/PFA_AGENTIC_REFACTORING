# C Long Function Refactoring Patterns

## Goal
Split overly long C functions into smaller readable/testable helpers.

## Smells
- function > 30–60 lines (heuristic)
- validation + parsing + business logic + I/O in one function
- too many temporary variables
- deeply nested loops/conditionals
- repeated cleanup/error paths

## Safe Patterns

### 1. Split by Responsibility
Common split:
- `validate_input(...)`
- `parse_request(...)`
- `compute_result(...)`
- `write_output(...)`
- `cleanup_resources(...)`

### 2. Extract Large Conditional Blocks
If an `if` branch is long, extract to a helper with explicit parameters.

### 3. Extract Loop Body Processing
Keep loop skeleton in parent function; move heavy work to helper.

```c
for (size_t i = 0; i < count; ++i) {
    process_item(&items[i], ctx);
}
4. Standardize Error Handling

If many error exits exist, use one cleanup path (goto cleanup) only if already idiomatic in the project.

C Precautions

preserve resource cleanup order

preserve allocation/free ownership

preserve return codes and errno behavior

preserve pointer aliasing assumptions

preserve global/static state mutations

do not hide important side effects in macros

Heuristic

Extract only when clarity improves and ownership/side-effects remain obvious.