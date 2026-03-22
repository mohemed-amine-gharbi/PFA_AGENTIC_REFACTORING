# C# Complexity Refactoring Patterns

## Goal
Reduce cyclomatic/cognitive complexity in C# code without changing behavior.

## Common Smells
- Deeply nested `if/else` blocks
- Long method chains with mixed concerns
- Methods mixing validation + business logic + persistence
- Repeated conditional logic across methods
- Large `switch` statements without pattern matching
- Excessive LINQ chaining that harms readability

## Safe Complexity Reduction Patterns

### 1. Guard Clauses (Early Return)
Replace nesting with early exits.

#### Before
```csharp
public decimal Calculate(Order order) {
    if (order != null) {
        if (order.IsActive) {
            if (order.Items.Count > 0) {
                return order.Items.Sum(i => i.Price);
            }
        }
    }
    return 0;
}
```

#### After
```csharp
public decimal Calculate(Order order) {
    if (order == null) return 0;
    if (!order.IsActive) return 0;
    if (order.Items.Count == 0) return 0;
    return order.Items.Sum(i => i.Price);
}
```

### 2. Extract Private Methods by Responsibility
Split into:
- `ValidateInput(...)`
- `ParseRequest(...)`
- `ComputeResult(...)`
- `PersistResult(...)`

### 3. Replace Switch with Dictionary Dispatch
Only when branches have identical structure and no side-effect ordering dependency.

### 4. Use Pattern Matching (C# 8+)
Replace long if-else chains with `switch` expressions where semantics are preserved.

### 5. Simplify Boolean Expressions
Extract complex conditions into well-named private methods or local variables.

## Semantic Preservation Constraints
- do not change return values or thrown exceptions
- do not change side effects or their order
- do not change public API signatures
- do not change `async/await` structure
- do not change `IDisposable` / `using` patterns
- preserve null checks and null propagation behavior (`?.`, `??`)

## C#-Specific Sensitive Cases
- `async/await` and `Task` ordering
- `IDisposable` and `using` scopes
- LINQ deferred execution vs immediate execution
- nullable reference types (`string?` vs `string`)
- `ref` / `out` / `in` parameter semantics
- exception filters and `when` clauses

## Expected Agent Output
- list detected complexity smells with line references
- propose targeted refactor preserving semantics
- explain why semantics are preserved
