# C# Import (Using) Cleanup Patterns

## Goal
Clean `using` directives in C# files safely.

## Typical Tasks
- Remove unused `using` directives
- Remove duplicate `using` directives
- Sort `using` directives per project conventions
- Convert to `global using` when applicable (C# 10+)

## Safe Rules
- do not remove a `using` that provides extension methods used implicitly
- do not remove a `using` required for implicit type conversions
- preserve `using static` directives that provide static members
- preserve `using` aliases (`using Alias = Some.Long.Namespace`)

## C#-Specific Cases

### 1. Extension Methods
A `using` may appear unused but provides extension methods:
```csharp
using System.Linq; // required for .Where(), .Select(), etc.
```

### 2. Implicit Usings (.NET 6+)
With `<ImplicitUsings>enable</ImplicitUsings>`, many System.* usings are auto-included — safe to remove explicit ones.

### 3. Using Aliases
```csharp
using Dict = System.Collections.Generic.Dictionary<string, int>;
```
Keep unless the alias is provably unused.

## Standard Sort Order (StyleCop / ReSharper)
1. `System.*` namespaces
2. Other namespaces alphabetically
3. `using static`
4. `using` aliases

## Expected Agent Output
- list unused/duplicate using directives
- return full file with cleaned usings
- preserve all functionality
