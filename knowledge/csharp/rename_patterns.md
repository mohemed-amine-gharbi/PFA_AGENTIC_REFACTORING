# C# Rename Patterns (Safe Renaming)

## Goal
Improve readability through safe renaming in C# code.

## Safe Targets (Priority)
- local variables (`x`, `tmp`, `res`, `obj`, `val`)
- private fields (`_x`, `_tmp`)
- private method names that are unclear
- unclear parameter names in private methods
- loop variables in complex loops (`i`, `j` when ambiguous)

## Sensitive Targets (Avoid Without Strong Context)
- public API method/property names (breaking change)
- interface members
- names referenced in reflection or `nameof()`
- names used in serialization attributes (`[JsonProperty("name")]`)
- names tied to EF Core conventions (navigation properties, column names)

## C# Naming Conventions
- classes/interfaces/methods/properties: `PascalCase`
- local variables/parameters: `camelCase`
- private fields: `_camelCase`
- constants: `PascalCase` or `UPPER_SNAKE_CASE` (project-dependent)
- booleans: `isValid`, `hasPermission`, `shouldRetry`
- async methods: suffix `Async` → `GetUserAsync`, `SaveOrderAsync`

## Examples
- `x` → `itemCount`
- `tmp` → `tempBuffer`
- `res` → `processingResult`
- `u` → `currentUser`
- `o` → `pendingOrder`
- `flag` → `isProcessed`

## Safety Rules
- rename consistently across ALL usages in the same scope
- do not rename public members unless explicitly requested
- preserve `nameof()` references
- preserve serialization attribute values
- preserve EF Core navigation property conventions

## Expected Agent Output
- identify unclear names with rationale
- propose consistent renamings following C# conventions
- return full refactored code with all occurrences updated
