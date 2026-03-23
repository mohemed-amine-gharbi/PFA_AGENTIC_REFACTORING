# JavaScript Duplication Refactoring Patterns

## Goal
Reduce duplicated JavaScript code safely while preserving behavior.

## Common Duplication
- repeated validation checks
- repeated object mapping / formatting
- repeated API response handling
- repeated try/catch + logging blocks
- repeated array transformations
- repeated DOM update logic

## Safe Patterns

### 1. Extract Helper Functions
Create small pure helpers for repeated logic when possible.

### 2. Reuse Validation Utilities
Examples:
- `validateUser(user)`
- `validatePayload(payload)`

### 3. Consolidate Response Formatting
Centralize repeated object shaping / DTO mapping.

### 4. Shared Error Handling (Carefully)
Extract repeated error logging/formatting only if error propagation remains the same.

### 5. Reuse Configuration Objects
Extract repeated options/constants (timeouts, headers, flags) when stable.

## Anti-Patterns
- over-abstracting tiny differences
- creating generic helpers that reduce readability
- merging blocks with different side effects
- hiding control flow in utility functions unnecessarily

## Safety Checks Before Refactoring
- same return values?
- same thrown errors?
- same async behavior (`await` order)?
- same object mutation behavior?
- same logging and side effects?