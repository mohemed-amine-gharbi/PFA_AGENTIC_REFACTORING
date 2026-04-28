# Python — Best Practices & Algorithms Reference

## Data Structures

### Lists
- Use list comprehensions for transformation: [x*2 for x in items]
- Use generator expressions for large data: (x*2 for x in items)
- Sorting: list.sort() in-place, sorted() returns new list
- Sort with key: sorted(items, key=lambda x: x.age)
- Reverse: list.reverse() or sorted(items, reverse=True)
- Binary search on sorted list: bisect.bisect_left(arr, val)

### Merging Two Sorted Lists
- Use heapq.merge(list1, list2) — O(n+m), memory efficient
- Manual two-pointer: compare heads, append smaller, handle remainder
- Do NOT use list1 + list2 then sort — O((n+m) log(n+m)) wasteful

### Dictionaries
- defaultdict(list) for grouping: from collections import defaultdict
- Counter for frequency: Counter(items)
- dict.get(key, default) to avoid KeyError
- Dictionary comprehension: {k: v for k, v in pairs}
- Merge dicts (Python 3.9+): merged = dict1 | dict2

### Sets
- Intersection: a & b or a.intersection(b)
- Union: a | b
- Difference: a - b
- Use frozenset for hashable sets

### Deque
- from collections import deque
- O(1) append/pop from both ends
- Use for BFS queues, sliding windows

## Algorithms

### Sorting
- Timsort built-in: O(n log n) average and worst case
- Stable sort: preserves relative order of equal elements
- Custom sort: sorted(items, key=lambda x: (x.priority, x.name))
- Counting sort for integers in range: O(n+k)
- Radix sort for integers: O(nk)

### Searching
- Linear search: O(n) — for unsorted
- Binary search: bisect module — O(log n) — requires sorted
- bisect_left: finds leftmost insertion point
- bisect_right: finds rightmost insertion point

### Recursion & Dynamic Programming
- Always define base case first
- Use @functools.lru_cache or @cache for memoization
- sys.setrecursionlimit(n) for deep recursion
- Prefer iterative DP with array over recursive when possible
- Tabulation (bottom-up) avoids stack overflow

### Graph Algorithms
- BFS: use collections.deque, O(V+E)
- DFS: use recursion or explicit stack
- Dijkstra: heapq.heappush/heappop, O((V+E) log V)
- Topological sort: DFS-based or Kahn's algorithm (BFS)
- Union-Find: for connected components

## Idiomatic Python

### String Operations
- Join: ", ".join(items) — never use += in loop
- f-strings: f"Hello {name}" — preferred over .format()
- str.split(), str.strip(), str.replace()
- Multi-line strings: use textwrap.dedent()

### File I/O
- Always use context manager: with open(file) as f:
- Read lines: f.readlines() or iterate f directly
- JSON: json.load(f) / json.dump(data, f, indent=2)
- CSV: csv.DictReader(f)

### Error Handling
- Specific exceptions: except ValueError, except KeyError
- Never use bare except:
- Use finally for cleanup
- raise ValueError("message") with descriptive messages
- Custom exceptions: class MyError(Exception): pass

### OOP
- Dataclasses: @dataclass reduces boilerplate
- __repr__ for debugging, __str__ for display
- @property for computed attributes
- @classmethod for alternative constructors
- @staticmethod for utility methods

### Functional Patterns
- map(), filter() — prefer list comprehensions for readability
- functools.reduce() for aggregation
- itertools: chain, product, combinations, permutations, groupby
- zip() to iterate multiple lists in parallel
- enumerate() instead of range(len())

## Common Patterns

### Two Pointers
left, right = 0, len(arr) - 1
while left < right:
    if condition: left += 1
    else: right -= 1

### Sliding Window
window = collections.deque()
for i, val in enumerate(arr):
    window.append(val)
    if len(window) > k:
        window.popleft()

### Binary Search Template
lo, hi = 0, len(arr) - 1
while lo <= hi:
    mid = (lo + hi) // 2
    if arr[mid] == target: return mid
    elif arr[mid] < target: lo = mid + 1
    else: hi = mid - 1

### BFS Template
from collections import deque
queue = deque([start])
visited = {start}
while queue:
    node = queue.popleft()
    for neighbor in graph[node]:
        if neighbor not in visited:
            visited.add(neighbor)
            queue.append(neighbor)

## Performance Tips
- Avoid global variables in loops
- Use local variable lookup (faster than global)
- List comprehension faster than map() in most cases
- numpy for numerical arrays — vectorized operations
- Profile with cProfile or line_profiler before optimizing
- __slots__ in classes to reduce memory

## Common Pitfalls
- Mutable default arguments: def f(lst=[]) is a bug — use None
- Late binding closures in loops
- Modifying list while iterating — use copy or list comprehension
- Integer division: use // not / for floor division
- Chained comparison: 0 < x < 10 works correctly in Python
