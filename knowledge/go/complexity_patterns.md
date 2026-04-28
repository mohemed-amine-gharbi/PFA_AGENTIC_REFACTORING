# Go Complexity Refactoring Patterns

## Goal
Reduce cyclomatic/cognitive complexity in Go code without changing behavior.

## Common Smells
- Deeply nested `if err != nil` chains
- Functions mixing validation + business logic + I/O
- Long `switch` blocks with duplicated branches
- Complex boolean conditions without named functions
- Repeated error wrapping logic

## Safe Patterns

### 1. Guard Clauses (Early Return)
```go
// Before
func Process(req *Request) error {
    if req != nil {
        if req.IsValid() {
            if req.Data != nil {
                return compute(req.Data)
            }
        }
    }
    return ErrInvalid
}

// After
func Process(req *Request) error {
    if req == nil { return ErrInvalid }
    if !req.IsValid() { return ErrInvalid }
    if req.Data == nil { return ErrInvalid }
    return compute(req.Data)
}
```

### 2. Extract Helper Functions
Split into:
- `validateRequest(req *Request) error`
- `buildEntity(req *Request) (*Entity, error)`
- `persistEntity(e *Entity) error`

### 3. Flatten Error Handling with Named Returns
Only when it genuinely reduces nesting without obscuring error provenance.

### 4. Replace Repeated Type Switches with Interface Methods
When the same type switch appears in multiple places.

## Semantic Preservation Constraints
- do not change return values or error types
- do not change goroutine behavior or channel operations
- do not change `defer` execution order
- preserve pointer vs value receiver semantics
- preserve `context.Context` propagation

## Go-Specific Sensitive Cases
- `defer` ordering (LIFO)
- goroutine lifetimes and channel closes
- `context.Context` cancellation propagation
- named return values and naked returns
- interface satisfaction (implicit)
- `sync.Mutex` lock/unlock pairing
