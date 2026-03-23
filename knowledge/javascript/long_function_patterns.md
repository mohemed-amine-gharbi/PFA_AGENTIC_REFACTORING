# JavaScript Long Function Refactoring Patterns

## Goal
Split overly long JavaScript functions into smaller, readable, testable helpers.

## Smells
- function > 30–60 lines (heuristic)
- validation + transformation + persistence + UI updates in one function
- too many temporary variables
- deeply nested conditionals
- repeated try/catch or error handling
- mixed sync and async concerns in one block

## Safe Patterns

### 1. Split by Responsibility
Common split:
- `validateInput(...)`
- `normalizeInput(...)`
- `computeResult(...)`
- `saveResult(...)`
- `formatResponse(...)`

### 2. Extract Large Conditional Blocks
If a branch is long, extract it to a helper with explicit inputs.

### 3. Extract Loop Body Processing
Keep iteration in parent function, move heavy logic to helper.

```javascript
for (const item of items) {
  processItem(item, context);
}
### 4. Isolate Error Handling
Extract repetitive error formatting/logging, but preserve throw/return behavior.

### 5. Separate Async Steps Clearly
Break large async functions into small awaited steps while preserving order.

## JavaScript Precautions
- preserve `await` order
- preserve thrown errors and rejected promises
- preserve object mutation/reference behavior
- preserve `this` context where relevant
- preserve event handler side effects and timing

## Heuristic
Extract only when readability improves and side effects remain obvious.
