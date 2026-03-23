# Ruby Long Method Refactoring Patterns

## Goal
Split overly long Ruby methods into smaller readable/testable units.

## Smells
- Method > 15–20 lines
- Validation + business logic + persistence in one method
- Too many local variables
- Deeply nested blocks or conditionals
- Multiple `rescue` clauses in one method

## Safe Patterns

### 1. Split by Responsibility
Common split:
- `validate_input(...)` → raises or returns bool
- `build_record(...)` → pure construction
- `persist_record(...)` → DB side effects
- `notify_subscribers(...)` → notifications

### 2. Extract Long Block Bodies
```ruby
# Before
items.each do |item|
  # 15 lines of logic
end

# After
items.each { |item| process_item(item) }
```

### 3. Use Method Objects for Very Complex Methods
When a method needs more than 3 helpers, consider extracting to a dedicated class.

### 4. Extract Guard Block into Predicate Method
```ruby
def valid_request?(req)
  req && req.user_id && req.items.any?
end
```

## Ruby Precautions
- preserve implicit return (last expression)
- preserve `yield` and block passing behavior
- preserve `rescue`/`ensure` scope
- preserve instance variable mutations (`@var`)
- preserve ActiveRecord transaction scope
- do not split across `transaction` blocks inadvertently

## Heuristic
Extract only when the block has one clear purpose and the split improves testability.
