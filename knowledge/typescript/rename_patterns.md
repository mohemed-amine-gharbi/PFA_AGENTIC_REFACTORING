# TypeScript Rename Patterns (Safe Renaming)

## Goal
Improve readability through safe renaming in TypeScript code.

## Safe Targets
- local variables (`x`, `tmp`, `res`, `obj`, `val`)
- private class members (`_x`, `#x`)
- private/unexported function names
- unclear parameter names in private functions
- generic type parameters (`T` → `TEntity` when context is clear)

## Sensitive Targets (Avoid)
- exported function/class/interface names (breaking change)
- interface member names (affects all implementations)
- names used in decorators (`@Column('name')`)
- names referenced in `keyof`, `typeof`, or template literals
- names used in JSON serialization or API contracts
- React component names (affects JSX and DevTools)

## TypeScript Naming Conventions
- variables/functions: `camelCase`
- classes/interfaces/types: `PascalCase`
- private members: `_camelCase` or `#camelCase`
- constants: `UPPER_SNAKE_CASE` or `camelCase` (project-consistent)
- booleans: `isValid`, `hasPermission`, `shouldRetry`
- async functions: suffix `Async` optional but consistent
- generics: `T`, `TEntity`, `TResult` (descriptive when used in complex contexts)

## Examples
- `x` → `itemCount`
- `tmp` → `tempBuffer`
- `res` → `processingResult`
- `u` → `currentUser`
- `o` → `pendingOrder`
- `e` → `validationError` (in catch blocks)
- `cb` → `onSuccess`

## Safety Rules
- rename consistently across ALL usages in scope
- do not rename exported symbols without updating all callers
- preserve `keyof` / `typeof` references
- preserve decorator metadata names
- preserve React component display names
