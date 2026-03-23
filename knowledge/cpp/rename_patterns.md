# C++ Rename Patterns (Safe Renaming)

## Goal
Improve readability through safe renaming in C++ code.

## Safe Targets
- local variables (`x`, `tmp`, `res`, `p`, `n`)
- private member variables (`m_x`, `_x`)
- private/static helper function names
- unclear parameter names in non-public functions
- loop counters in complex loops

## Sensitive Targets (Avoid)
- public API function/method names
- virtual method names (affects all overrides)
- names used in `typeid`, `decltype`, or reflection
- names tied to serialization (`nlohmann::json`, `cereal`)
- names exported in shared libraries

## C++ Naming Conventions
- functions/methods: `camelCase` or `snake_case` (project-consistent)
- classes: `PascalCase`
- member variables: `m_name` or `name_` (project-consistent)
- constants/macros: `UPPER_SNAKE_CASE`
- booleans: `isValid`, `hasError`, `shouldRetry`

## Examples
- `x` → `itemCount`
- `tmp` → `tempBuffer`
- `p` → `userPtr`
- `n` → `bufferLength`
- `res` → `statusCode`

## Safety Rules
- rename consistently across ALL usages
- do not rename virtual methods without renaming all overrides
- preserve `const` correctness after renaming
- do not rename names used in macros
