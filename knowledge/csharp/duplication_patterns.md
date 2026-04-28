# C# Duplication Refactoring Patterns

## Goal
Eliminate code duplication in C# safely using idiomatic patterns.

## Common Duplication in C#
- Repeated null/argument validation across methods
- Identical try/catch/log blocks
- Repeated LINQ queries with minor variations
- Repeated DTO mapping logic
- Copy-pasted constructor initialization

## Safe Patterns

### 1. Extract Private Helper Method
Factor repeated logic into a `private` or `private static` method.

### 2. Use Generic Methods for Structural Repetition
When structure is identical but types differ — use generics only if semantics are identical.

### 3. Consolidate Validation with Guard Helpers
```csharp
private static void EnsureNotNull<T>(T value, string paramName)
    where T : class
{
    if (value == null) throw new ArgumentNullException(paramName);
}
```

### 4. Replace Repeated Mapping with AutoMapper or Manual Helper
Extract `MapToDto(entity)` helper when the same mapping appears more than twice.

### 5. Use Base Class or Extension Methods for Cross-Cutting Concerns
Only when ownership and lifecycle are clearly defined.

## Anti-Patterns
- introducing interfaces just to remove a few duplicate lines
- merging methods that look similar but differ in exception handling
- over-generalizing with reflection to remove duplication

## Safety Checks Before Refactoring
- same return type and value?
- same exceptions thrown?
- same async behavior?
- same `IDisposable` / resource lifetime?
- same null propagation behavior?
