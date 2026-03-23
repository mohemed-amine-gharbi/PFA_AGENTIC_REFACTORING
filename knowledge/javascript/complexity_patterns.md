# JavaScript Complexity Reduction Patterns

## Goal
Reduce cyclomatic/cognitive complexity in JavaScript code without changing behavior.

## Common Smells
- Deeply nested `if/else`
- Long conditional chains
- Functions mixing validation + transformation + I/O
- Repeated conditional logic
- Excessive nested loops
- Large `try/catch` blocks mixed with business logic
- Callback pyramids / deeply nested async code

## Safe Complexity Reduction Patterns

### 1. Guard Clauses (Early Return)
Replace nesting with early exits when semantics are preserved.

#### Before
```javascript
if (user) {
  if (user.isActive) {
    processUser(user);
  }
}
After
if (!user) return;
if (!user.isActive) return;
processUser(user);
### 2. Extract Complex Conditions into Helper Functions

Improves readability while preserving logic
function isEligible(user) {
  return user && user.isActive && !user.isBlocked;
}
### 3. Split Large Functions by Responsibility
Split into:
- validation
- parsing / normalization
- computation
- persistence / API calls
- presentation formatting

### 4. Simplify Loop Bodies
- use `continue` for guard checks
- extract heavy loop logic into helper functions
- prefer clear iteration over nested branching

### 5. Replace Duplicated Branch Logic with Shared Helper
Only if side effects and execution order remain identical.

### 6. Flatten Async Control Flow
- prefer `async/await` over deeply nested `.then()`
- separate error handling from core logic when possible
- preserve `await` order and side effects

## Semantic Preservation Constraints
- do not change return values
- do not change side effects or their order
- do not change sync vs async behavior
- do not change thrown errors / error propagation
- do not change public function signatures unless explicitly requested
- preserve mutation timing and object reference behavior

## JavaScript-Specific Sensitive Cases
- truthy/falsy behavior
- optional chaining / nullish coalescing semantics
- async/await timing and promise resolution order
- object/array mutation by reference
- `this` binding
- closure capture behavior
- short-circuit evaluation side effects
- loose vs strict equality (`==` vs `===`)

## Expected Agent Output
- list detected complexity smells
- propose a targeted refactor
- explain why semantics are preserved