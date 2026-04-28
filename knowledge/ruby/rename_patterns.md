# Ruby Rename Patterns (Safe Renaming)

## Goal
Improve readability through safe renaming in Ruby code.

## Safe Targets
- local variables (`x`, `tmp`, `res`, `obj`, `val`)
- block parameters (`|i|`, `|e|`, `|v|` in complex blocks)
- private method names
- unclear parameter names in private methods

## Sensitive Targets (Avoid)
- public method names (breaking change for callers)
- ActiveRecord attribute names (tied to DB columns)
- names referenced in `send`, `method`, or `respond_to?`
- names used in `attr_accessor` / `attr_reader` / `attr_writer`
- names in Rails route helpers or controller actions

## Ruby Naming Conventions
- methods/variables: `snake_case`
- classes/modules: `PascalCase`
- constants: `UPPER_SNAKE_CASE`
- booleans/predicates: `active?`, `valid?`, `has_permission?`
- bang methods: `save!`, `validate!`
- private helpers: descriptive verbs `build_record`, `find_customer`

## Examples
- `x` → `item_count`
- `tmp` → `temp_buffer`
- `res` → `processing_result`
- `u` → `current_user`
- `o` → `pending_order`
- `|i|` → `|item|` in complex blocks

## Safety Rules
- rename consistently across ALL usages in scope
- do not rename public methods without updating all callers
- preserve `respond_to?` / `send` references
- preserve ActiveRecord attribute names
