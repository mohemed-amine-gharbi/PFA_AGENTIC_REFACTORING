# TypeScript Duplication Refactoring Patterns

## Goal
Eliminate code duplication in TypeScript safely using idiomatic patterns.

## Common Duplication in TypeScript
- Repeated null/undefined validation across functions
- Identical `try/catch/log` blocks
- Repeated DTO mapping logic
- Copy-pasted type narrowing code
- Repeated `async/await` boilerplate

## Safe Patterns

### 1. Extract Private Helper Function
Factor repeated logic into a `private` or module-level function.

```typescript
function validateProduct(product: Product | null): void {
  if (!product) throw new Error('product required');
  if (!product.name) throw new Error('name required');
}
```

### 2. Use Generic Functions for Structural Duplication
When logic is identical but types differ.

```typescript
function mapToDto<T extends Entity>(entity: T): EntityDto {
  return { id: entity.id, name: entity.name };
}
```

### 3. Consolidate Repeated Type Guards
```typescript
function isActiveUser(user: User | null): user is User {
  return user !== null && user.isActive === true;
}
```

### 4. Extract Repeated Async Patterns
```typescript
async function withErrorHandling<T>(
  operation: () => Promise<T>,
  context: string
): Promise<T> {
  try {
    return await operation();
  } catch (err) {
    logger.error(`${context} failed`, err);
    throw err;
  }
}
```

### 5. Use Mapped Types to Replace Repeated Interface Patterns
Only when structure is truly identical.

## Anti-Patterns
- over-using decorators to hide duplication
- using `any` to merge incompatible types
- merging async functions that differ in error handling

## Safety Checks
- same return type?
- same thrown error types?
- same `Promise` resolution behavior?
- same `null`/`undefined` handling?
