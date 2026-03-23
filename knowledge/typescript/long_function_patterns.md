# TypeScript Long Function Refactoring Patterns

## Goal
Split overly long TypeScript functions into smaller readable/testable units.

## Smells
- Function > 20–30 lines
- Validation + business logic + persistence in one function
- Too many local variables
- Deeply nested `async/await` with error handling
- Multiple `try/catch` blocks in one function

## Safe Patterns

### 1. Split by Responsibility
```typescript
function validateRequest(req: OrderRequest): void { ... }
function buildOrder(customer: Customer, items: OrderItem[]): Order { ... }
async function persistOrder(order: Order): Promise<void> { ... }
async function notifyCustomer(order: Order): Promise<void> { ... }
```

### 2. Extract Loop Body
```typescript
// Before
for (const item of items) {
  // 15 lines
}

// After
for (const item of items) {
  await processItem(item, context);
}
```

### 3. Extract Complex Type Narrowing
```typescript
function assertValidOrder(order: Order | null): asserts order is Order {
  if (!order) throw new Error('order required');
}
```

### 4. Use Method Objects for Very Complex Functions
When a function needs more than 3 helpers, consider a class.

## TypeScript Precautions
- preserve `async/await` — do not make async functions sync
- preserve `Promise` rejection behavior
- preserve `null`/`undefined` narrowing after extracted calls
- preserve decorator execution order
- do not split across `transaction` or `mutex` scopes
- preserve generic type parameter flow through extracted functions

## Heuristic
Extract only when the block has one clear responsibility and types flow cleanly.
