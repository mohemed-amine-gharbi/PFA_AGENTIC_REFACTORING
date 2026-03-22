# TypeScript Complexity Refactoring Patterns

## Goal
Reduce cyclomatic/cognitive complexity in TypeScript code without changing behavior.

## Common Smells
- Deeply nested `if/else` blocks
- Mixed async/await with complex conditionals
- Long ternary chains
- Functions mixing validation + business logic + I/O
- Complex union type narrowing spread across one function
- Large `switch` blocks with duplicated branches

## Safe Patterns

### 1. Guard Clauses (Early Return)
```typescript
// Before
function process(user: User | null, order: Order | null): number {
  if (user !== null) {
    if (user.isActive) {
      if (order !== null) {
        if (order.items.length > 0) {
          return order.items.reduce((sum, i) => sum + i.price, 0);
        }
      }
    }
  }
  return 0;
}

// After
function process(user: User | null, order: Order | null): number {
  if (!user) return 0;
  if (!user.isActive) return 0;
  if (!order) return 0;
  if (order.items.length === 0) return 0;
  return order.items.reduce((sum, i) => sum + i.price, 0);
}
```

### 2. Extract Private Functions by Responsibility
Split into:
- `validateInput(...)` → `boolean` or throws
- `buildEntity(...)` → pure construction
- `persistResult(...)` → async side effects
- `notifyObservers(...)` → notifications

### 3. Replace Long Ternaries with Named Variables
```typescript
// Before
const label = user.score > 90 ? 'A' : user.score > 80 ? 'B' : user.score > 70 ? 'C' : 'F';

// After
function classifyScore(score: number): string {
  if (score > 90) return 'A';
  if (score > 80) return 'B';
  if (score > 70) return 'C';
  return 'F';
}
```

### 4. Use Type Narrowing Helpers
Extract repeated type guard logic into named type guard functions.

```typescript
function isActiveUser(user: User | null): user is User {
  return user !== null && user.isActive;
}
```

## Semantic Preservation Constraints
- do not change return types or thrown errors
- do not change `async/await` or `Promise` chain behavior
- do not change side effects or their order
- preserve `null` vs `undefined` distinctions
- preserve union type narrowing semantics

## TypeScript-Specific Sensitive Cases
- `null` vs `undefined` (strict null checks)
- `async/await` error propagation
- type assertion (`as`) side effects
- generic type constraints
- decorator execution order
- optional chaining (`?.`) and nullish coalescing (`??`)
