# C# Long Method Refactoring Patterns

## Goal
Split overly long C# methods into smaller, readable, testable units.

## Smells
- Method > 20–30 lines
- Validation + business logic + persistence in one method
- Too many local variables
- Deeply nested loops or conditionals
- Multiple `return` paths with duplicated cleanup

## Safe Patterns

### 1. Split by Responsibility
Common split:
- `ValidateInput(...)`
- `BuildEntity(...)`
- `PersistResult(...)`
- `NotifyObservers(...)`

### 2. Extract Large Conditional Blocks
Move long `if` branches to private methods with descriptive names.

### 3. Extract Loop Body
Keep loop skeleton in parent method; extract heavy processing to helper.

```csharp
foreach (var item in items)
{
    ProcessSingleItem(item, context);
}
```

### 4. Use Builder Pattern for Complex Object Construction
When a method is long mainly due to object initialization.

## C# Precautions
- preserve `async/await` chains — do not make async methods sync
- preserve `IDisposable` / `using` scopes
- preserve exception propagation and `AggregateException` behavior
- preserve `ref`/`out` parameter mutation timing
- do not split across transaction boundaries inadvertently

## Heuristic
Extract only when the extracted block has a single clear responsibility and the split improves testability.
