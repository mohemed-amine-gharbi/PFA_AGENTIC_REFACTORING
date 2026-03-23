# C Include Cleanup Patterns

## Goal
Clean C includes safely.

## Typical Tasks
- remove unused `#include`
- remove duplicate includes
- keep required standard/library/project headers
- preserve include order conventions if the project has one

## Safe Rules
- do not remove headers required transitively only if the file directly depends on macros/types from them
- be careful with platform-specific headers
- preserve include guards behavior (in headers)
- do not change macro definitions while cleaning includes

## C-Specific Cases

### 1. Type Definitions
A header may be required for:
- `size_t`
- `uint32_t`
- `FILE`
- `bool`
- struct declarations
- enums / typedefs

### 2. Macros and Inline Functions
An include may look unused but provides:
- macros
- static inline helpers
- compile-time constants

### 3. Conditional Compilation
Headers inside `#ifdef` / `#if` blocks may be necessary on some platforms.

## Style (Project-Dependent)
Common style:
1. local header (`"module.h"`)
2. project headers
3. standard library headers (`<stdio.h>`, `<stdlib.h>`, ...)
4. third-party headers

## Expected Agent Output
- list unused/duplicate includes
- return full code with cleaned includes
- preserve functionality and portability assumptions