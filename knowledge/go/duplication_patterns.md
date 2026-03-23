# Go Duplication Refactoring Patterns

## Goal
Eliminate code duplication in Go safely using idiomatic patterns.

## Common Duplication in Go
- Repeated `if err != nil { return err }` patterns
- Identical validation blocks across functions
- Repeated struct initialization sequences
- Copy-pasted error wrapping with `fmt.Errorf`
- Repeated HTTP handler boilerplate

## Safe Patterns

### 1. Extract Helper Function
Factor repeated logic into a package-level or unexported helper function.

```go
func validateProduct(p *Product) error {
    if p == nil { return ErrNullProduct }
    if p.Name == "" { return ErrEmptyName }
    return nil
}
```

### 2. Use Functional Options for Repeated Initialization
When the same struct fields are repeatedly set with minor variations.

### 3. Consolidate Error Wrapping
```go
// Before (repeated everywhere)
if err != nil { return fmt.Errorf("save failed: %w", err) }

// After
func wrapSaveError(err error) error {
    if err == nil { return nil }
    return fmt.Errorf("save failed: %w", err)
}
```

### 4. Use Generics (Go 1.18+) for Structural Duplication
When logic is identical but types differ — use generics only if semantics are identical.

## Anti-Patterns
- using `reflect` to remove trivial duplication
- over-using interfaces just to remove a few duplicate lines
- merging functions that differ in error handling strategy

## Safety Checks
- same return types and error values?
- same `defer` behavior?
- same goroutine/channel interactions?
- same `context.Context` propagation?
