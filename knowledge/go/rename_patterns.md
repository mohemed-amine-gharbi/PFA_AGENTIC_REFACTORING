# Go Rename Patterns (Safe Renaming)

## Goal
Improve readability through safe renaming in Go code.

## Safe Targets
- local variables (`x`, `tmp`, `res`, `v`, `n`)
- unexported function names
- unclear parameter names in unexported functions
- loop variables in complex loops (`i`, `j` when ambiguous)
- receiver names (Go convention: short, consistent)

## Sensitive Targets (Avoid)
- exported function/method names (breaking change)
- interface method names (affects all implementations)
- struct field names used in JSON/YAML tags
- names referenced in `reflect` or `encoding/json`
- names in test function names (`TestXxx`)

## Go Naming Conventions
- variables/functions: `camelCase`
- exported identifiers: `PascalCase`
- unexported identifiers: `camelCase`
- receiver: short abbreviation of type (`u` for `User`, `s` for `Service`)
- error variables: `err` (standard), `errXxx` for specific errors
- booleans: `isValid`, `hasError`, `ok`
- interfaces: single method → `Stringer`, `Reader`, `Writer`

## Examples
- `x` → `itemCount`
- `tmp` → `tempBuffer`
- `res` → `processingResult`
- `u` → `currentUser` (local var, not receiver)
- `n` → `bufferLength`
- `v` → `orderValue`

## Safety Rules
- rename consistently across ALL usages in scope
- do not rename exported identifiers without updating all callers
- preserve JSON/YAML struct tag field names
- preserve interface method signatures
