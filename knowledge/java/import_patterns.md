# Java Import Cleanup Patterns

## Goal
Clean Java imports safely.

## Typical Tasks
- remove unused imports
- remove duplicate imports
- organize imports (based on project style)
- avoid wildcard imports if project conventions forbid them

## Safe Rules
- do not remove imports used indirectly by annotations/references
- be careful with name conflicts (`Date`, `List`, etc.)
- preserve static imports when used (`import static ...`)
- do not introduce wildcard imports unless explicitly allowed

## Java-Specific Cases

### 1. Annotations
Some annotations may look “invisible” but are critical:
- `@Transactional`
- `@Entity`
- `@Autowired`
- `@JsonProperty`
- etc.

### 2. Inner/Nested Classes
An import may be required for a nested type reference.

### 3. Lombok
Lombok imports (`@Data`, `@Builder`, etc.) can be essential.

### 4. Static Imports
Do not remove without verifying usage:
```java
import static java.util.Objects.requireNonNull;