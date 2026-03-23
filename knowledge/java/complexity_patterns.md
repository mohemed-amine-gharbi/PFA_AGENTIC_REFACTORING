# Java Complexity Reduction Patterns

## Goal
Reduce cyclomatic/cognitive complexity in Java code without changing behavior.

## Common Smells
- Deeply nested `if/else`
- Long conditional chains
- Methods mixing validation + transformation + I/O
- Repeated conditional logic
- Excessive nested loops
- Large `try/catch` blocks mixed with business logic

## Safe Complexity Reduction Patterns

### 1. Guard Clauses (Early Return)
Replace nesting with early exits when semantics are preserved.

#### Before
```java
if (user != null) {
    if (user.isActive()) {
        process(user);
    }
}
#### After
```java
if (user == null) return;
if (!user.isActive()) return;
process(user);

private boolean isEligible(User user) {
    return user != null && user.isActive() && !user.isBlocked();
}