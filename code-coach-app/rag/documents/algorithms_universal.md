# Algorithms & Data Structures — Universal Reference

## Sorting Algorithms

### Merge Sort
- Time: O(n log n) all cases
- Space: O(n) auxiliary
- Stable: yes
- Best for: linked lists, external sorting, when stability required
- Divide array in half, sort each half, merge sorted halves
- Merge two sorted: two-pointer, compare heads, append smaller

### Quick Sort
- Time: O(n log n) avg, O(n²) worst case
- Space: O(log n) stack
- Stable: no (standard), yes (stable variant)
- Best for: in-place sorting, cache-friendly
- Pivot selection: random, median-of-three to avoid O(n²)
- Partition: elements < pivot left, > pivot right

### Heap Sort
- Time: O(n log n) all cases
- Space: O(1)
- Stable: no
- Best for: guaranteed O(n log n), limited memory
- Build max-heap, repeatedly extract max

### Tim Sort (Python, Java, JavaScript built-in)
- Hybrid: insertion sort for small runs + merge sort
- Time: O(n log n), O(n) best case (nearly sorted)
- Stable: yes

### Counting Sort
- Time: O(n+k) where k is range
- Space: O(k)
- Best for: integers in known bounded range
- Not comparison-based

### Radix Sort
- Time: O(nk) where k is number of digits
- Space: O(n+k)
- Best for: large integers, fixed-length strings

## Searching Algorithms

### Binary Search
- Requires sorted array
- Time: O(log n), Space: O(1)
- Find target: compare with mid, go left or right
- Variants: leftmost, rightmost, first >= target, last <= target
- Template:
  lo=0, hi=n-1
  while lo <= hi:
    mid = lo + (hi-lo) // 2
    if arr[mid] == target: return mid
    elif arr[mid] < target: lo = mid+1
    else: hi = mid-1

### Linear Search
- Time: O(n), Space: O(1)
- No requirement on order
- Best for: small arrays, or when array changes frequently

## Graph Algorithms

### BFS (Breadth-First Search)
- Uses queue
- Time: O(V+E), Space: O(V)
- Applications: shortest path (unweighted), level-order, connected components
- Always use visited set to avoid cycles

### DFS (Depth-First Search)
- Uses stack (recursive or explicit)
- Time: O(V+E), Space: O(V)
- Applications: topological sort, cycle detection, connected components, maze

### Dijkstra's Algorithm
- Shortest path in weighted graph (non-negative weights)
- Uses min-heap (priority queue)
- Time: O((V+E) log V)
- Initialize distances to infinity, source to 0
- Relax edges: if dist[u] + weight < dist[v], update

### Bellman-Ford
- Shortest path with negative weights
- Detects negative cycles
- Time: O(VE), Space: O(V)
- Relax all edges V-1 times

### Floyd-Warshall
- All pairs shortest paths
- Time: O(V³), Space: O(V²)
- DP: dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

### Topological Sort
- For DAG (directed acyclic graph)
- DFS-based: finish time ordering
- Kahn's: BFS with in-degree tracking

### Union-Find (Disjoint Set)
- Find root with path compression
- Union by rank
- Nearly O(1) per operation (amortized)
- Applications: MST (Kruskal), connected components

## Dynamic Programming

### Patterns
- Overlapping subproblems + optimal substructure = DP
- Top-down: recursion + memoization
- Bottom-up: iterative tabulation
- State: what varies between subproblems
- Transition: how to compute state from smaller states

### Classic Problems
- Fibonacci: dp[n] = dp[n-1] + dp[n-2]
- Coin change: dp[amount] = min(dp[amount - coin] + 1)
- Longest Common Subsequence: dp[i][j] = dp[i-1][j-1]+1 or max(dp[i-1][j], dp[i][j-1])
- 0/1 Knapsack: dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt[i]] + val[i])
- Longest Increasing Subsequence: O(n log n) with binary search

## Common Algorithm Patterns

### Two Pointers
- Sorted array problems: sum, triplets, container with most water
- Fast/slow pointers: cycle detection (Floyd), middle of linked list
- Left/right pointers: palindrome check, merge

### Sliding Window
- Fixed size: track sum/state as window moves
- Variable size: expand right, shrink left when condition violated
- Use for: max subarray, longest substring, min window

### Divide and Conquer
- Divide: split problem into smaller subproblems
- Conquer: solve recursively
- Combine: merge solutions
- Examples: merge sort, binary search, matrix multiply

### Greedy
- Make locally optimal choice at each step
- Works when greedy choice property + optimal substructure hold
- Examples: activity selection, Huffman coding, Dijkstra

### Backtracking
- Try all possibilities, undo when stuck
- Base case: solution found or space exhausted
- Prune: skip invalid branches early
- Examples: N-Queens, Sudoku, permutations, subsets

## Complexity Reference

### Time Complexity
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(n³) < O(2^n) < O(n!)

### Common Operations
- Array access: O(1)
- Array insert/delete middle: O(n)
- Hash table get/set: O(1) avg, O(n) worst
- BST search/insert: O(log n) balanced, O(n) worst
- Heap insert/delete: O(log n)
- Sort: O(n log n) comparison-based lower bound

### Space Complexity
- Iterative: usually O(1) extra
- Recursive: O(depth) for call stack
- DP table: O(n) to O(n²) depending on states

## Data Structure Selection Guide
- Need O(1) access by index → Array
- Need O(1) access by key → Hash Map
- Need sorted order + O(log n) → BST / Sorted Set
- Need FIFO → Queue
- Need LIFO → Stack
- Need min/max efficiently → Heap
- Need set operations → Hash Set
- Need union/find → Union-Find
- Need prefix sums → Segment Tree / Fenwick Tree
