# C++ Duplication Refactoring Patterns

## Goal
Eliminate code duplication in C++ safely using idiomatic patterns.

## Common Duplication in C++
- Repeated null/validity checks across functions
- Identical RAII setup/teardown patterns
- Repeated struct initialization sequences
- Copy-pasted loop logic with minor variations
- Duplicated error handling and logging

## Safe Patterns

### 1. Extract Static or Free Helper Function
Factor repeated logic into a `static` method or a file-local free function.

### 2. Use Templates for Structural Duplication
When logic is identical but types differ — use function templates only if semantics are identical.

### 3. Consolidate Validation
```cpp
static bool validateInput(const Request* req) {
    return req != nullptr && req->isValid() && req->data != nullptr;
}
```

### 4. Use RAII Wrappers to Consolidate Cleanup
Replace repeated `lock/unlock`, `open/close`, `malloc/free` with RAII wrappers.

### 5. Consolidate Struct Initialization
```cpp
static void resetItem(Item& item) {
    item.id = 0;
    item.count = 0;
    item.flag = false;
}
```

## Anti-Patterns
- over-generalizing with complex template metaprogramming
- using macros to hide duplication
- merging functions that look similar but differ in ownership semantics

## Safety Checks
- same return value?
- same exception safety guarantee?
- same ownership transfer?
- same `noexcept` specification?
- same move/copy behavior?
