# Ruby Complexity Refactoring Patterns

## Goal
Reduce cyclomatic/cognitive complexity in Ruby code without changing behavior.

## Common Smells
- Deeply nested `if/elsif/else` blocks
- Methods mixing validation + business logic + persistence
- Long conditional chains on the same object
- Complex boolean expressions without named predicates
- Large `case/when` blocks with duplicated logic

## Safe Patterns

### 1. Guard Clauses (Early Return)
```ruby
# Before
def process(user, order)
  if user
    if user.active?
      if order
        if order.items.any?
          order.total
        end
      end
    end
  end
end

# After
def process(user, order)
  return unless user
  return unless user.active?
  return unless order
  return unless order.items.any?
  order.total
end
```

### 2. Extract Private Methods by Responsibility
Split into:
- `validate_input(...)` → raises or returns bool
- `build_entity(...)` → pure construction
- `persist_result(...)` → side effects
- `notify_observers(...)` → notifications

### 3. Replace Complex Conditionals with Named Predicates
```ruby
# Before
if user && user.active? && !user.blocked? && user.verified?

# After
def can_proceed?(user)
  user&.active? && !user.blocked? && user.verified?
end
```

### 4. Use `tap`, `then`, `yield_self` for Readable Pipelines
Only when it genuinely reduces nesting without obscuring logic.

## Semantic Preservation Constraints
- do not change return values (Ruby returns last expression)
- do not change raised exceptions or rescue clauses
- do not change side effects or their order
- do not change `yield` behavior in blocks
- preserve `nil` propagation with `&.` (safe navigation)

## Ruby-Specific Sensitive Cases
- implicit `nil` returns vs explicit `return nil`
- `&.` safe navigation operator
- `rescue` inline vs block form
- mutable default arguments
- `frozen_string_literal` impact
- `attr_accessor` vs direct `@var` access
