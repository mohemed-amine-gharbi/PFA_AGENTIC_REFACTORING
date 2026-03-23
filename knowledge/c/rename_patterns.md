# C Rename Patterns (Safe Renaming)

## Goal
Improve readability through safe renaming in C code.

## Safe Targets (Priority)
- local variables (`x`, `tmp`, `res`, `buf`)
- loop counters when ambiguous (`i`, `j`) in complex loops
- private/static helper function names
- unclear parameters in internal functions

## Sensitive Targets (Avoid Without Strong Context)
- public API function names
- struct fields used across many modules
- macro names used externally
- symbols referenced in linker scripts/build scripts
- callback names tied to frameworks/libraries

## C Naming Best Practices
- functions/variables: `snake_case`
- macros/constants: `UPPER_SNAKE_CASE`
- booleans: `is_valid`, `has_error`, `should_retry`
- pointers may use suffixes/prefixes only if project style uses them (`out_buf`, `input_ptr`)

## Examples
- `x` -> `item_count`
- `tmp` -> `temp_buffer`
- `res` -> `status_code`
- `p` -> `user_ptr`
- `n` -> `buffer_length`

## Safety Rules
- do not rename public API symbols unless explicitly requested
- preserve semantics and storage duration meaning
- keep consistency with project naming conventions
- avoid renaming macros unless usage is fully controlled

## Expected Agent Output
- identify unclear names and explain why they reduce readability
- propose safer, meaningful renamings
- avoid renaming public/external symbols unless explicitly requested
- return full refactored code with naming consistency