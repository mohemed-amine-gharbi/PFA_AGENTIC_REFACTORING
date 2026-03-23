# TypeScript Import Cleanup Patterns

## Goal
Clean `import` statements in TypeScript files safely.

## Typical Tasks
- Remove unused imports (TypeScript compiler warns with `noUnusedLocals`)
- Remove duplicate imports
- Merge imports from the same module
- Prefer type-only imports for types (`import type`)

## Safe Rules
- do not remove an import used only as a type — use `import type` instead
- do not remove side-effect imports (`import 'reflect-metadata'`)
- preserve barrel imports that re-export needed symbols
- keep `import 'zone.js'` and similar polyfill imports

## TypeScript-Specific Cases

### 1. Type-Only Imports (TypeScript 3.8+)
```typescript
// Before
import { User, UserService } from './user';  // User used only as type

// After
import type { User } from './user';
import { UserService } from './user';
```

### 2. Side-Effect Imports
```typescript
import 'reflect-metadata';  // required for decorators — never remove
import 'zone.js';           // Angular — never remove
```

### 3. Merging Split Imports
```typescript
// Before
import { useState } from 'react';
import { useEffect } from 'react';

// After
import { useState, useEffect } from 'react';
```

### 4. Barrel Import Organization
Prefer specific imports over `import * as X` when only a few symbols are used.

## Standard Import Order (ESLint import/order)
1. External packages (`react`, `lodash`)
2. Internal absolute paths (`@/components/...`)
3. Relative imports (`./utils`, `../models`)
4. Type imports last (or first, project-consistent)

## Expected Agent Output
- list unused/duplicate imports
- suggest `import type` where applicable
- merge split imports from same module
- return full file with cleaned imports
