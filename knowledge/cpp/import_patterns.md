# C++ Include Cleanup Patterns

## Goal
Clean `#include` directives in C++ files safely.

## Typical Tasks
- Remove unused `#include`
- Remove duplicate includes
- Prefer forward declarations over full includes in headers
- Follow include order conventions

## Safe Rules
- do not remove a header required for a type used in the file
- do not remove a header that provides required macros or inline functions
- prefer forward declarations in `.h` files for pointer/reference types
- keep `#include` guards or `#pragma once`

## C++-Specific Cases

### 1. Forward Declarations vs Full Include
In headers, prefer:
```cpp
class User; // forward declaration — no #include "user.h" needed
```
Only when the type is used as pointer or reference.

### 2. Template Definitions
Template implementations must be in headers — do not split includes.

### 3. Standard Library Headers
Each STL component has its own header:
- `<vector>`, `<string>`, `<map>`, `<algorithm>`, `<memory>`...
- Do not rely on transitive includes.

## Standard Include Order (Google / LLVM style)
1. Related `.h` file (for `.cpp` files)
2. C system headers (`<cstdio>`)
3. C++ standard library headers (`<vector>`)
4. Third-party headers
5. Project headers

## Expected Agent Output
- list unused/duplicate includes
- suggest forward declarations where applicable
- return full file with cleaned includes
