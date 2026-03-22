# C++ Long Function Refactoring Patterns

## Goal
Split overly long C++ functions into smaller readable/testable units.

## Smells
- Function > 30–50 lines
- Validation + parsing + computation + I/O in one function
- Too many local variables with unclear lifetimes
- Deeply nested loops or conditionals
- Repeated cleanup paths

## Safe Patterns

### 1. Split by Responsibility
- `validate(...)` → `bool` or error code
- `parse(...)` → returns parsed struct
- `compute(...)` → pure computation
- `persist(...)` → side effects

### 2. Extract Loop Body
```cpp
for (size_t i = 0; i < items.size(); ++i) {
    processItem(items[i], context);
}
```

### 3. Use RAII to Simplify Cleanup
Replace repeated cleanup paths with RAII guards.

### 4. Extract Large Conditional Blocks
Move long `if` branches to named private methods.

## C++ Precautions
- preserve RAII resource lifetimes and destruction order
- preserve move semantics — do not copy where move was intended
- preserve `noexcept` guarantees
- preserve `const` correctness of extracted functions
- do not split across lock scopes inadvertently
- preserve iterator invalidation assumptions

## Heuristic
Extract only when the extracted block has a single clear responsibility and ownership is obvious.
