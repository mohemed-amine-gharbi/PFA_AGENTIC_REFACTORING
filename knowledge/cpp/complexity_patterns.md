# C++ Complexity Refactoring Patterns

## Goal
Reduce cyclomatic/cognitive complexity in C++ code without changing behavior.

## Common Smells
- Deeply nested `if/else` with raw pointer checks
- Mixed resource management + business logic in one function
- Long chains of `if (ptr != nullptr)` guards
- Complex template metaprogramming in business logic
- Large `switch` blocks with duplicated code per case

## Safe Patterns

### 1. Guard Clauses with Early Return
```cpp
// Before
Result process(Request* req) {
    if (req != nullptr) {
        if (req->isValid()) {
            if (req->data != nullptr) {
                return compute(req->data);
            }
        }
    }
    return Result::error();
}

// After
Result process(Request* req) {
    if (req == nullptr) return Result::error();
    if (!req->isValid()) return Result::error();
    if (req->data == nullptr) return Result::error();
    return compute(req->data);
}
```

### 2. Replace Raw Pointer Checks with Smart Pointers
Use `std::unique_ptr` / `std::shared_ptr` to reduce explicit null checks where ownership is clear.

### 3. Split by Responsibility
- `validate(...)` → returns `bool` or `std::optional<Error>`
- `parse(...)` → returns parsed data
- `compute(...)` → pure business logic
- `persist(...)` → side effects

### 4. Use `std::optional` for Optional Returns (C++17)
Replace `nullptr` sentinel returns with `std::optional<T>`.

## Semantic Preservation Constraints
- do not change return values or thrown exceptions
- do not change RAII resource lifetimes
- do not change ownership semantics (`unique_ptr` vs `shared_ptr` vs raw)
- do not change virtual dispatch behavior
- preserve move semantics and copy semantics

## C++-Specific Sensitive Cases
- `std::move` and rvalue reference semantics
- copy/move constructor invocation order
- destructor call order (RAII)
- `noexcept` specifications
- template instantiation side effects
- `volatile` and `const` correctness
