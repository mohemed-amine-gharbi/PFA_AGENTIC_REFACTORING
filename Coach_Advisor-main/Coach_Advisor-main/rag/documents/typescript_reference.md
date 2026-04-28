# TypeScript — Best Practices & Algorithms Reference

## Type System

### Basic Types
- string, number, boolean, null, undefined, void, never, unknown, any
- Prefer unknown over any — forces type checking before use
- never for functions that always throw or infinite loops
- void for functions that return nothing

### Type vs Interface
- interface: for object shapes, supports declaration merging, use for APIs
- type: for unions, intersections, mapped types, primitives aliases
- Prefer interface for object types, type for everything else

### Union & Intersection
- Union: type Result = Success | Error
- Intersection: type Admin = User & { role: 'admin' }
- Discriminated union: type Shape = Circle | Square with shared literal field

### Generics
- function identity<T>(x: T): T { return x }
- Constrained: function max<T extends number>(a: T, b: T): T
- Default type: type List<T = string> = T[]
- Conditional: type IsArray<T> = T extends any[] ? true : false

### Utility Types
- Partial<T> — all fields optional
- Required<T> — all fields required
- Readonly<T> — immutable
- Pick<T, 'a'|'b'> — subset of fields
- Omit<T, 'a'|'b'> — exclude fields
- Record<K, V> — map type
- ReturnType<typeof fn> — extract return type
- Parameters<typeof fn> — extract param types
- NonNullable<T> — removes null and undefined

### Type Guards
- typeof x === 'string'
- instanceof MyClass
- Custom: function isUser(x: any): x is User { return 'name' in x }
- Narrowing with discriminated unions

## Data Structures with Types

### Typed Arrays
- number[], string[] or Array<number>
- ReadonlyArray<T> for immutable arrays
- Tuple: [string, number] — fixed length and types
- Sorting with typed comparator: (a: User, b: User) => a.age - b.age

### Typed Maps & Sets
- Map<string, User> — typed key-value
- Set<number> — typed set
- Record<string, User> — typed object map

### Interfaces for Data Models
interface User {
  id: number;
  name: string;
  email?: string; // optional
  readonly createdAt: Date; // immutable
}

## Algorithms in TypeScript

### Generic Sort Function
function sortBy<T>(arr: T[], key: keyof T): T[] {
  return [...arr].sort((a, b) => {
    if (a[key] < b[key]) return -1;
    if (a[key] > b[key]) return 1;
    return 0;
  });
}

### Generic Binary Search
function binarySearch<T>(arr: T[], target: T, compare: (a: T, b: T) => number): number {
  let lo = 0, hi = arr.length - 1;
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2);
    const cmp = compare(arr[mid], target);
    if (cmp === 0) return mid;
    else if (cmp < 0) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}

### Generic Stack
class Stack<T> {
  private items: T[] = [];
  push(item: T): void { this.items.push(item); }
  pop(): T | undefined { return this.items.pop(); }
  peek(): T | undefined { return this.items[this.items.length - 1]; }
  isEmpty(): boolean { return this.items.length === 0; }
}

## Patterns

### Enum vs Union
- Prefer union type over enum: type Direction = 'north' | 'south'
- const enum for performance when you need numeric values
- Avoid plain enum — generates runtime code

### Null Safety
- Use strict null checks: "strictNullChecks": true in tsconfig
- Non-null assertion: value! — only when you're certain
- Optional chaining: obj?.nested?.value
- Nullish coalescing: value ?? defaultValue

### Type Narrowing
function processInput(input: string | number) {
  if (typeof input === 'string') {
    return input.toUpperCase(); // TypeScript knows it's string here
  }
  return input.toFixed(2); // number here
}

### Mapped Types
type Optional<T> = {
  [K in keyof T]?: T[K];
};

### Template Literal Types
type EventName = `on${Capitalize<string>}`;
type CSSProperty = `${string}-${string}`;

## Error Handling

### Result Type Pattern
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

function parseJSON(input: string): Result<unknown> {
  try {
    return { success: true, data: JSON.parse(input) };
  } catch (e) {
    return { success: false, error: e as Error };
  }
}

## tsconfig Best Practices
- "strict": true — enables all strict checks
- "noUncheckedIndexedAccess": true — array access returns T | undefined
- "exactOptionalPropertyTypes": true — stricter optional handling
- "noImplicitReturns": true — all code paths must return

## Common Pitfalls
- any disables type checking — use unknown instead
- Type assertions (as Type) can hide bugs — prefer type guards
- Enums have unexpected behavior with reverse mapping
- Object spread loses type information in some cases
- Array.sort() mutates — use [...arr].sort() to preserve original
- keyof T includes symbol keys — use keyof T & string if needed
