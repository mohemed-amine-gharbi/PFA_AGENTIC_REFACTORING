# C++ — Best Practices & Algorithms Reference

## Modern C++ (C++17/20)

### Smart Pointers — Prefer over raw pointers
- unique_ptr<T>: sole ownership, zero overhead, auto-delete
- shared_ptr<T>: shared ownership, reference counted
- weak_ptr<T>: non-owning reference to shared_ptr (break cycles)
- make_unique<T>(args) and make_shared<T>(args) — preferred over new

### RAII (Resource Acquisition Is Initialization)
- Acquire resources in constructor, release in destructor
- Objects on stack auto-cleanup when out of scope
- Use smart pointers and containers — never raw new/delete
- Lock guards: std::lock_guard<std::mutex> lock(mtx);

## STL Containers

### Sequence Containers
- std::vector<T>: dynamic array, O(1) random access, O(1) amortized push_back
- std::array<T,N>: fixed-size stack array, prefer over C arrays
- std::deque<T>: O(1) push/pop at both ends
- std::list<T>: doubly linked, O(1) insert/delete with iterator

### Associative Containers
- std::map<K,V>: sorted BST, O(log n)
- std::unordered_map<K,V>: hash table, O(1) avg
- std::set<T>: sorted unique elements, O(log n)
- std::unordered_set<T>: hash set, O(1) avg
- std::multimap / std::multiset: allow duplicates

### Priority Queue
- std::priority_queue<T>: max-heap by default
- Min-heap: priority_queue<int, vector<int>, greater<int>>
- Custom: priority_queue<T, vector<T>, Compare>

## Algorithms (STL)

### Sorting
std::sort(v.begin(), v.end()); // introsort O(n log n)
std::sort(v.begin(), v.end(), [](auto& a, auto& b){ return a.age < b.age; });
std::stable_sort(...); // preserves equal element order
std::partial_sort(v.begin(), v.begin()+k, v.end()); // top-k

### Merging Sorted Containers
std::merge(v1.begin(), v1.end(), v2.begin(), v2.end(), back_inserter(result));
// O(n+m), requires pre-allocated or back_inserter
std::inplace_merge(v.begin(), mid, v.end()); // merge in-place

### Searching
std::binary_search(v.begin(), v.end(), target); // returns bool
std::lower_bound(v.begin(), v.end(), target); // first >= target
std::upper_bound(v.begin(), v.end(), target); // first > target
std::find(v.begin(), v.end(), target); // linear search

### Other Useful Algorithms
std::transform(in.begin(), in.end(), out.begin(), fn);
std::accumulate(v.begin(), v.end(), 0); // sum
std::count_if(v.begin(), v.end(), pred);
std::remove_if(...) // returns new end, use with erase
std::unique(v.begin(), v.end()); // remove consecutive duplicates

## Modern C++ Features

### Range-Based For
for (const auto& item : container) { ... }
for (auto& [key, val] : myMap) { ... } // structured bindings

### Lambda Functions
auto square = [](int x) { return x * x; };
auto add = [](int x, int y) -> int { return x + y; };
// Capture: [=] by value, [&] by reference, [x, &y] mixed

### Auto and Type Deduction
auto it = myMap.find(key);
auto [found_key, found_val] = *it; // structured binding
// Use auto to avoid verbose iterator types

### Constexpr
constexpr int factorial(int n) { return n <= 1 ? 1 : n * factorial(n-1); }
// Computed at compile time when possible

### std::optional (C++17)
std::optional<User> findUser(int id) {
    if (found) return user;
    return std::nullopt;
}
if (auto user = findUser(42); user.has_value()) { ... }

### std::variant (C++17)
std::variant<int, string, double> v = 42;
std::get<int>(v); // access by type
std::visit([](auto& val) { ... }, v); // visitor pattern

## Memory Management

### Stack Allocation Preferred
- Local variables on stack: fast, no fragmentation
- std::array instead of new int[n]
- std::vector instead of dynamic arrays

### When Heap is Needed
- Large objects, dynamic size, shared ownership
- Always prefer smart pointers over raw new/delete
- unique_ptr for single owner, shared_ptr for shared

## Common Patterns

### Two Sum with Hash Map
unordered_map<int, int> seen;
for (int i = 0; i < nums.size(); i++) {
    int complement = target - nums[i];
    if (seen.count(complement)) return {seen[complement], i};
    seen[nums[i]] = i;
}

### BFS
queue<int> q;
unordered_set<int> visited;
q.push(start);
visited.insert(start);
while (!q.empty()) {
    int node = q.front(); q.pop();
    for (int neighbor : graph[node]) {
        if (!visited.count(neighbor)) {
            visited.insert(neighbor);
            q.push(neighbor);
        }
    }
}

## Common Pitfalls
- iterator invalidation: don't modify container while iterating
- std::endl flushes buffer — use '\n' for performance
- Integer overflow: use long long or check with __int128
- Slicing: store polymorphic objects by pointer/reference, not value
- std::vector<bool> is not a container of bool — use deque<bool>
- Missing virtual destructor in base class with inheritance
