# JavaScript Import Cleanup Patterns

## Goal
Clean JavaScript imports safely.

## Typical Tasks
- remove unused imports
- remove duplicate imports
- normalize import grouping/order (if project style requires it)
- keep side-effect imports that are required

## Safe Rules
- do not remove side-effect imports (e.g. `import "./setup";`) unless confirmed unused
- preserve runtime-required imports even if statically hard to detect
- preserve import order if side effects depend on order
- do not rewrite module format (ESM/CommonJS) unless explicitly requested

## JavaScript-Specific Cases

### 1. Side-Effect Imports
These may appear unused but are required:
- polyfills
- global setup
- CSS imports in frontend apps
- monkey patches / instrumentation

### 2. Named vs Default Imports
Be careful when changing syntax:
- `import x from "m"`
- `import { x } from "m"`

### 3. Type-Only Imports (TS projects nearby)
In mixed JS/TS repos, avoid assumptions when files interact.

## Style (Project-Dependent)
Common grouping:
1. built-in / platform modules
2. third-party packages
3. internal absolute imports
4. relative imports

## Expected Agent Output
- list unused/duplicate imports
- return full code with cleaned imports
- preserve functionality and side effects