# Java Duplication Refactoring Patterns

## Goal
Reduce duplicated Java code without over-abstraction.

## Common Duplication in Java
- repeated validation blocks across methods
- repeated DTO <-> Entity mapping
- repeated `try/catch` blocks
- repeated object construction
- repeated filtering/formatting loops
- repeated repository/service calls with minor variations

## Safe Patterns

### 1. Extract Private Method
Factor repeated blocks into a private method if:
- inputs/outputs are clear
- no hidden implicit dependencies

### 2. Local Template (No Over-Engineering)
If two methods share the same structure with small variations:
- extract common flow
- pass variation via parameter/helper method

### 3. Centralize Validation
Create methods like:
- `validateProduct(...)`
- `validateRequest(...)`

### 4. Mapping Utilities (If Duplication Is Real)
Examples:
- `toDto(entity)`
- `updateEntityFromDto(dto, entity)`

Be careful:
- do not break JPA/framework annotations
- do not move logic that depends on transaction/session context

### 5. Extract Repeated Messages to Constants
Centralize repeated strings/error messages.

## Anti-Patterns
- creating a complex class hierarchy to remove a few lines
- introducing reflection/generics unnecessarily
- merging code that looks similar but is not semantically identical

## Safety Checks Before Refactoring
- same exceptions?
- same side effects?
- same execution order?
- same transaction/session context assumptions?