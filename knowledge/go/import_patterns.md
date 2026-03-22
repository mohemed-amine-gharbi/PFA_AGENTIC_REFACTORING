# Go Import Cleanup Patterns

## Goal
Clean `import` blocks in Go files safely.

## Typical Tasks
- Remove unused imports (Go compiler enforces this)
- Remove duplicate imports
- Organize imports per Go conventions
- Replace dot imports with named imports

## Safe Rules
- do not remove an import used for its side effects (`import _ "pkg"`)
- do not remove a blank identifier import that registers drivers or plugins
- preserve import aliases when they resolve naming conflicts
- keep `import _ "net/http/pprof"` and similar side-effect imports

## Go-Specific Cases

### 1. Blank Identifier Imports (Side Effects)
```go
import _ "github.com/lib/pq"  // registers PostgreSQL driver
```
Never remove — they have intentional side effects.

### 2. Import Aliases
```go
import myfmt "fmt"  // alias — keep if used as myfmt.Println
```

### 3. Dot Imports (Avoid)
```go
import . "math"  // makes all exported names directly available
```
Replace with named import when possible.

## Standard Import Order (goimports / gofmt)
1. Standard library packages
2. Third-party packages
3. Internal/project packages
Separated by blank lines.

## Expected Agent Output
- list unused imports (compiler will flag these)
- organize into standard groups
- return full file with cleaned imports
