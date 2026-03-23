# Java Long Function Refactoring Patterns

## Goal
Split overly long methods into smaller, readable, testable methods.

## Smells
- method longer than ~30–50 lines (heuristic)
- validation + transformation + DB + logging + notification in one method
- too many temporary variables
- repeated conditional blocks
- comments like "Step 1 / Step 2 / Step 3" (often signals extractable methods)

## Safe Patterns

### 1. Split by Responsibility
Common sequence:
- `validateRequest(...)`
- `loadEntity(...)`
- `applyBusinessRules(...)`
- `saveEntity(...)`
- `buildResponse(...)`

### 2. Extract Long Conditional Blocks
If an `if` block is large, extract it to a dedicated method.

### 3. Reduce Loop Body Length
Extract item processing:
```java
for (Order order : orders) {
    processOrder(order);
}