# C# — Best Practices & Algorithms Reference

## Data Structures

### Lists & Arrays
- List<T>: dynamic array, O(1) amortized Add, O(n) Insert
- T[]: fixed array, faster than List for fixed size
- Sorting: list.Sort(), Array.Sort(arr)
- Custom sort: list.Sort((a, b) => a.Age.CompareTo(b.Age))
- LINQ sort: list.OrderBy(x => x.Age).ThenBy(x => x.Name)
- Binary search: Array.BinarySearch(arr, target)

### Merging Two Sorted Lists
- LINQ: list1.Concat(list2).OrderBy(x => x).ToList() — O((n+m)log(n+m))
- Manual two-pointer: O(n+m) — preferred for performance
- Enumerable.Merge from MoreLINQ or custom implementation

### Dictionary
- Dictionary<K,V>: O(1) avg lookup, unsorted
- SortedDictionary<K,V>: O(log n), sorted by key
- ConcurrentDictionary<K,V>: thread-safe
- TryGetValue(key, out var val): preferred over ContainsKey + indexer
- GetOrAdd, AddOrUpdate: ConcurrentDictionary convenience methods

### Queue & Stack
- Queue<T>: FIFO, Enqueue/Dequeue
- Stack<T>: LIFO, Push/Pop
- PriorityQueue<TElement, TPriority>: .NET 6+, min-heap

### HashSet
- HashSet<T>: O(1) Contains, Add, Remove
- IntersectWith, UnionWith, ExceptWith — set operations in-place

## LINQ

### Querying Collections
var result = list
    .Where(x => x.Age > 18)
    .Select(x => new { x.Name, x.Age })
    .OrderBy(x => x.Age)
    .Take(10)
    .ToList();

### Aggregation
list.Sum(x => x.Amount);
list.Average(x => x.Score);
list.Max(x => x.Age);
list.Count(x => x.IsActive);
list.Any(x => x.Score > 90);  // exists
list.All(x => x.IsValid);     // all match

### Grouping
var grouped = list
    .GroupBy(x => x.Department)
    .Select(g => new { Dept = g.Key, Count = g.Count() });

### Projection
list.Select((item, index) => new { item, index });
list.SelectMany(x => x.Tags); // flatten nested collections

### Performance
- Use ToList() to materialize, ToArray() for arrays
- Avoid multiple enumeration of IEnumerable
- AsParallel() for CPU-bound parallel LINQ (PLINQ)

## Async/Await

### Task Pattern
async Task<int> FetchDataAsync() {
    var result = await httpClient.GetStringAsync(url);
    return result.Length;
}
// await Task.WhenAll(task1, task2) — parallel
// await Task.WhenAny(task1, task2) — first to complete
// ConfigureAwait(false) in library code

### Cancellation
async Task ProcessAsync(CancellationToken ct) {
    ct.ThrowIfCancellationRequested();
    await Task.Delay(1000, ct);
}
// Pass CancellationToken throughout call chain

## Patterns

### Records (C# 9+)
record Person(string Name, int Age); // immutable value type
record class: reference semantics
record struct: value semantics

### Pattern Matching
switch (shape) {
    case Circle c when c.Radius > 10:
        return "large circle";
    case Square { Side: > 5 }:
        return "large square";
    default:
        return "other";
}

### Null Safety
string? nullable = null;          // nullable reference type
string nonNullable = "value";     // non-nullable (C# 8+)
nullable?.Length                  // null-conditional
nullable ?? "default"             // null-coalescing
nullable ??= "default"            // null-coalescing assignment

### Span<T> and Memory
- Span<T>: zero-allocation slice of memory
- ReadOnlySpan<T>: read-only view
- Use for string slicing without allocation: str.AsSpan(0, 5)
- Memory<T>: async-compatible version of Span

### IDisposable & Using
using var conn = new SqlConnection(connStr);
// Auto-calls Dispose() at end of scope

### Dependency Injection
// Register in Program.cs
services.AddSingleton<IService, ServiceImpl>();
services.AddScoped<IRepo, RepoImpl>();
services.AddTransient<IHelper, HelperImpl>();
// Inject via constructor
class MyController {
    MyController(IService svc) { _svc = svc; }
}

## Entity Framework

### LINQ to DB
var users = await context.Users
    .Where(u => u.IsActive)
    .Include(u => u.Orders)
    .OrderBy(u => u.Name)
    .ToListAsync();

### Common Patterns
- AsNoTracking() for read-only queries — better performance
- SaveChangesAsync() to persist changes
- Migrations: dotnet ef migrations add Name

## Common Algorithms

### Two Pointer
int left = 0, right = arr.Length - 1;
while (left < right) {
    int sum = arr[left] + arr[right];
    if (sum == target) return (left, right);
    else if (sum < target) left++;
    else right--;
}

### BFS
var queue = new Queue<int>();
var visited = new HashSet<int> { start };
queue.Enqueue(start);
while (queue.Count > 0) {
    int node = queue.Dequeue();
    foreach (int neighbor in graph[node]) {
        if (visited.Add(neighbor))
            queue.Enqueue(neighbor);
    }
}

## Common Pitfalls
- Comparing strings with == is fine (value comparison), but culture-sensitive
- DateTime vs DateTimeOffset: use DateTimeOffset for timezone awareness
- List<T> foreach doesn't allow modification — use for loop or ToList()
- async void: only for event handlers, never for regular async methods
- Task.Result or .Wait() can deadlock in UI/ASP.NET context — use await
- String concatenation in loops: use StringBuilder
