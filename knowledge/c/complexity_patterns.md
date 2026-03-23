# C Complexity Reduction Patterns

## Goal
Reduce cyclomatic/cognitive complexity in C code without changing behavior.

## Common Smells
- Deeply nested `if/else`
- Long conditional chains
- Functions mixing validation + parsing + processing + I/O
- Repeated conditional logic
- Excessive nested loops
- Large `switch` blocks with duplicated branches

## Safe Complexity Reduction Patterns

### 1. Guard Clauses (Early Return)
Replace nesting with early exits when semantics are preserved.

#### Before
```c
if (user != NULL) {
    if (user->is_active) {
        process(user);
    }
}
if (user == NULL) return;
if (!user->is_active) return;
process(user);

### 3. Split Large Functions by Responsibility
Split into:
- validation
- parsing
- computation
- output / persistence

### 4. Simplify Loop Bodies
- use `continue` for guard checks
- extract heavy loop logic into helper functions

### 5. Replace Duplicated Branch Logic with Shared Helper
Only if side effects and execution order remain identical.

## Semantic Preservation Constraints
- do not change return values
- do not change side effects or their order
- do not change pointer mutation timing
- do not change memory ownership semantics
- do not change error codes / errno behavior
- do not change public function signatures unless explicitly requested

## C-Specific Sensitive Cases
- NULL checks and dereference order
- pointer aliasing
- buffer sizes and bounds
- signed/unsigned behavior
- integer overflow/underflow behavior
- `malloc/free` ownership and lifetime
- `goto cleanup` error handling patterns
- macro side effects (evaluate arguments carefully)

## Expected Agent Output
- list detected complexity smells
- propose a targeted refactor
- explain why semantics are preserved