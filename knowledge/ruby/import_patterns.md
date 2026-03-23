# Ruby Require Cleanup Patterns

## Goal
Clean `require` and `require_relative` statements in Ruby files safely.

## Typical Tasks
- Remove unused `require` statements
- Remove duplicate requires
- Prefer `require_relative` for project-local files
- Keep stdlib and gem requires in correct order

## Safe Rules
- do not remove a `require` that provides constants, modules, or monkey-patches used in the file
- do not remove a `require` that triggers necessary side effects (e.g. registering hooks)
- preserve `autoload` declarations
- keep `require 'bundler/setup'` and `require 'rails_helper'` in test files

## Ruby-Specific Cases

### 1. Implicit Requires via Rails Autoload
In Rails apps, most requires are unnecessary — autoload handles them.
Only explicit `require` for non-autoloaded gems or stdlib.

### 2. Monkey-Patching Side Effects
Some requires add methods to core classes:
```ruby
require 'active_support/core_ext/string/inflections'
```
Keep these even if no direct constant is used.

### 3. `require_relative` vs `require`
Prefer `require_relative` for files within the same project:
```ruby
require_relative 'models/user'  # project file
require 'json'                  # stdlib / gem
```

## Standard Order
1. stdlib requires
2. gem requires
3. project requires (`require_relative`)

## Expected Agent Output
- list unused/duplicate requires
- return full file with cleaned requires
- preserve all functionality
