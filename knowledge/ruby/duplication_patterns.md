# Ruby Duplication Refactoring Patterns

## Goal
Eliminate code duplication in Ruby safely using idiomatic patterns.

## Common Duplication in Ruby
- Repeated nil/validity checks across methods
- Identical rescue/log blocks
- Repeated ActiveRecord query patterns
- Copy-pasted attribute assignment in initializers
- Repeated before_action-style guard code

## Safe Patterns

### 1. Extract Private Helper Method
Factor repeated logic into a `private` method.

```ruby
private

def validate_product!(product)
  raise ArgumentError, 'product required' if product.nil?
  raise ArgumentError, 'name required' if product.name.blank?
end
```

### 2. Use Modules for Cross-Cutting Concerns
Extract shared validation or logging into a module only when ownership is clear.

### 3. Consolidate Repeated Query Patterns
```ruby
# Before (repeated everywhere)
User.where(active: true).where(verified: true)

# After (named scope)
scope :verified_active, -> { where(active: true, verified: true) }
```

### 4. Replace Repeated Initialization with Factory Method
```ruby
def self.build_default
  new(id: 0, count: 0, flag: false)
end
```

### 5. Use `Struct` or `Data` for Repeated Value Objects (Ruby 3.2+)

## Anti-Patterns
- using `method_missing` to remove duplication
- over-using `send` / `define_method` for trivial duplication
- merging methods that look similar but differ in exception handling

## Safety Checks
- same return value (last expression)?
- same exceptions raised?
- same ActiveRecord callbacks triggered?
- same `yield` / block behavior?
