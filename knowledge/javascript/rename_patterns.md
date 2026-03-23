# JavaScript Rename Patterns (Safe Renaming)

## Goal
Improve readability through safe renaming in JavaScript code.

## Safe Targets (Priority)
- local variables (`x`, `tmp`, `res`, `data`)
- loop variables when ambiguous
- internal/private helper function names
- unclear parameters in internal functions
- callback parameters (`e`, `d`, `r`) when context is unclear

## Sensitive Targets (Avoid Without Strong Context)
- exported/public API names
- object keys used externally (API/contracts)
- framework lifecycle method names
- event names / route names
- global variables used across files
- destructured property names tied to external payloads

## JavaScript Naming Best Practices
- variables/functions: `camelCase`
- constants: `UPPER_SNAKE_CASE` (project-dependent)
- booleans: `isValid`, `hasError`, `shouldRetry`
- collections: plural names (`users`, `items`)
- callbacks: semantic names (`onSuccess`, `handleSubmit`)

## Examples
- `x` -> `itemCount`
- `tmp` -> `temporaryBuffer`
- `res` -> `apiResponse`
- `d` -> `userData`
- `arr` -> `filteredItems`

## Safety Rules
- do not rename public/exported symbols unless explicitly requested
- do not rename object keys that are part of API payloads/contracts
- preserve semantics and scope
- keep naming consistent with project conventions

## Expected Agent Output
- identify unclear names and explain why
- propose safer, meaningful renamings
- avoid renaming public/external symbols unless requested
- return full refactored code with naming consistency