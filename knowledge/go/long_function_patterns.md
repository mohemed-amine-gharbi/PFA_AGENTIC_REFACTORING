# Go Long Function Refactoring Patterns

## Goal
Split overly long Go functions into smaller readable/testable units.

## Smells
- Function > 30–40 lines
- Validation + business logic + persistence in one function
- Too many local variables
- Deeply nested `if err != nil` chains
- Multiple `defer` calls with complex interactions

## Safe Patterns

### 1. Split by Responsibility
```go
func validateRequest(req *Request) error { ... }
func buildEntity(req *Request) (*Entity, error) { ... }
func persistEntity(ctx context.Context, e *Entity) error { ... }
```

### 2. Extract Loop Body
```go
for _, item := range items {
    if err := processItem(ctx, item); err != nil {
        return err
    }
}
```

### 3. Use Named Results Sparingly
Named returns can simplify error handling but avoid naked returns in long functions.

### 4. Extract `defer` Setup into Helper
When defer setup is repeated or complex.

## Go Precautions
- preserve `defer` order (LIFO)
- preserve `context.Context` passing to all helpers
- preserve goroutine/channel interactions
- preserve named return variable mutations
- do not split across `sync.Mutex` lock/unlock boundaries
- preserve `recover()` behavior in defer

## Heuristic
Extract only when the block has one clear responsibility and `ctx` / error propagation remains clean.
