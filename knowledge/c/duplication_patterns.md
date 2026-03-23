# C Duplication Refactoring Patterns

## Goal
Reduce duplicated C code safely without introducing unnecessary abstraction.

## Common Duplication in C
- repeated input validation
- repeated error handling / cleanup
- repeated struct initialization
- repeated loops over arrays
- repeated parsing logic
- repeated logging / error messages

## Safe Patterns

### 1. Extract Static Helper Function
Factor repeated logic into a `static` helper when:
- inputs/outputs are explicit
- side effects are clear
- memory ownership remains unchanged

### 2. Consolidate Repeated Cleanup
Centralize cleanup using:
- helper function
- or a controlled `goto cleanup` pattern

### 3. Reuse Validation Functions
Examples:
- `validate_input(...)`
- `validate_config(...)`

### 4. Shared Initialization Functions
For repeated initialization of structs:
- `init_request(...)`
- `reset_buffer(...)`

### 5. Extract Repeated Constants/Messages
Move repeated literals to constants/macros only if it improves clarity.

## Anti-Patterns
- over-generalizing with complex macros
- introducing function pointers just to remove a few lines
- merging blocks that look similar but differ in resource ownership or side effects

## Safety Checks Before Refactoring
- same return code?
- same errno / error state?
- same memory allocation/free behavior?
- same execution order?
- same pointer writes?