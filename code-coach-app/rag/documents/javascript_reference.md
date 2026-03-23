# JavaScript — Best Practices & Algorithms Reference

## Data Structures

### Arrays
- Sort numbers: arr.sort((a, b) => a - b) — never arr.sort() for numbers
- Sort objects: arr.sort((a, b) => a.age - b.age)
- Merge sorted arrays: two-pointer O(n+m) or use [...a, ...b].sort()
- Filter: arr.filter(x => x > 0)
- Map: arr.map(x => x * 2)
- Reduce: arr.reduce((acc, x) => acc + x, 0)
- Find: arr.find(x => x.id === id)
- FlatMap: arr.flatMap(x => [x, x*2])
- Array.from({length: n}, (_, i) => i) — create range

### Objects & Maps
- Use Map for key-value with non-string keys or order-preservation
- Use Map for frequent add/delete — better performance than object
- Object.entries(obj) — iterate key-value pairs
- Object.fromEntries(entries) — convert back to object
- Spread merge: {...obj1, ...obj2}
- Optional chaining: obj?.nested?.value
- Nullish coalescing: value ?? defaultValue

### Sets
- new Set(arr) — deduplicate array
- Set intersection: new Set([...a].filter(x => b.has(x)))
- Set union: new Set([...a, ...b])
- Convert back: [...mySet] or Array.from(mySet)

## Algorithms

### Sorting
- Built-in sort: O(n log n), stable (V8 TimSort)
- Always provide comparator for numbers/objects
- Custom multi-key: (a, b) => a.x - b.x || a.y - b.y

### Searching
- Array.includes() — O(n) linear search
- Array.indexOf() — returns -1 if not found
- Binary search: manual implementation on sorted array
- Map.get(key) / Set.has(key) — O(1)

### Recursion
- No tail call optimization in most engines — prefer iteration for deep
- Use explicit stack array to simulate call stack
- Memoization: const cache = {}; if (cache[n]) return cache[n]

### Dynamic Programming
- Use array/object as memo table
- Bottom-up iterative preferred for JS (no stack overflow risk)
- Classic: fibonacci, knapsack, longest common subsequence

## Idiomatic JavaScript

### Async Patterns
- async/await preferred over .then() chains
- Promise.all([p1, p2]) — parallel execution
- Promise.allSettled() — wait for all regardless of failure
- try/catch around await for error handling
- Never forget to await async functions

### Destructuring
- Array: const [first, ...rest] = arr
- Object: const { name, age = 0 } = person
- Rename: const { name: username } = person
- Nested: const { address: { city } } = person

### Functions
- Arrow functions for callbacks and short expressions
- Regular functions when this binding matters
- Default params: function f(x = 0) {}
- Rest params: function f(...args) {}
- Currying: const add = a => b => a + b

### Classes & Prototypes
- class syntax preferred over prototype manipulation
- #privateField syntax for true private fields
- static methods for factory patterns
- extends for inheritance, super() in constructor

### Error Handling
- throw new Error("message") with descriptive text
- Custom errors: class ValidationError extends Error {}
- Always handle promise rejections — unhandledRejection crashes Node
- Use finally for cleanup (close connections, etc.)

## Common Patterns

### Two Pointers (sorted array)
let left = 0, right = arr.length - 1;
while (left < right) {
  const sum = arr[left] + arr[right];
  if (sum === target) return [left, right];
  else if (sum < target) left++;
  else right--;
}

### Sliding Window
let maxSum = 0, windowSum = 0;
for (let i = 0; i < k; i++) windowSum += arr[i];
maxSum = windowSum;
for (let i = k; i < arr.length; i++) {
  windowSum += arr[i] - arr[i - k];
  maxSum = Math.max(maxSum, windowSum);
}

### BFS
const queue = [start];
const visited = new Set([start]);
while (queue.length) {
  const node = queue.shift(); // use proper queue for performance
  for (const neighbor of graph[node]) {
    if (!visited.has(neighbor)) {
      visited.add(neighbor);
      queue.push(neighbor);
    }
  }
}

### Memoization
const memo = new Map();
function fib(n) {
  if (n <= 1) return n;
  if (memo.has(n)) return memo.get(n);
  const result = fib(n-1) + fib(n-2);
  memo.set(n, result);
  return result;
}

## Performance Tips
- Use Map/Set over plain objects for lookups — O(1) vs O(n)
- Avoid DOM manipulation in loops — batch updates
- Debounce/throttle expensive event handlers
- Use Web Workers for CPU-intensive tasks
- const > let > var — const is fastest
- Avoid delete operator — slows object optimization

## Common Pitfalls
- arr.sort() without comparator sorts lexicographically — [10,9,2] → [10,2,9]
- == vs === — always use strict equality ===
- this context lost in callbacks — use arrow functions or .bind()
- var hoisting — always use let/const
- Mutating function arguments — use spread to copy objects/arrays
- Floating point: 0.1 + 0.2 !== 0.3 — use toFixed() or integer math
