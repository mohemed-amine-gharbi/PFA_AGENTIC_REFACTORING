# Java Rename Patterns (Safe Renaming)

## Goal
Improve readability through safe renaming (local variables, parameters, private methods).

## Safe Targets (Priority)
- local variables (`x`, `tmp`, `res`)
- unclear internal parameters
- ambiguous loop variables
- private methods with vague names

## Sensitive Targets (Avoid Without Strong Context)
- public methods (API contract)
- fields exposed via frameworks/serialization
- names used by reflection
- JPA/Hibernate names with implicit mapping assumptions
- JSON/XML mapped names without explicit annotations

## Java Naming Best Practices
- classes: `PascalCase`
- methods/variables: `camelCase`
- constants: `UPPER_SNAKE_CASE`
- booleans: `isActive`, `hasAccess`, `canEdit`, `shouldRetry`

## Examples
- `x` -> `userCount`
- `tmp` -> `formattedMessage`
- `res` -> `validationResult`
- `l` -> `lineItems`
- `f` -> `inputFile`

## Safety Rules
- do not change the meaning of names
- avoid mass renaming without clear benefit
- keep consistency with existing file/project conventions
- preserve public signatures unless explicitly requested