# Java — Best Practices & Algorithms Reference

## Data Structures

### Arrays & Lists
- int[] arr = new int[n] — fixed size primitive array
- ArrayList<Integer> — dynamic size, O(1) amortized add
- LinkedList<T> — O(1) insert/delete at ends, slow random access
- Arrays.sort(arr) — Dual-Pivot Quicksort O(n log n)
- Collections.sort(list) — TimSort, stable
- Arrays.binarySearch(arr, key) — O(log n) on sorted array

### Merging Two Sorted Lists
- Two-pointer approach: compare, add smaller, advance pointer
- PriorityQueue (min-heap) for k sorted lists merge
- Collections.merge does not exist — implement manually
- Time: O(n+m), Space: O(n+m) for new list

### Maps
- HashMap — O(1) avg, unsorted, allows null key
- TreeMap — O(log n), sorted by key, NavigableMap interface
- LinkedHashMap — insertion-order or access-order
- ConcurrentHashMap — thread-safe HashMap alternative

### Sets
- HashSet — O(1) avg, unsorted
- TreeSet — O(log n), sorted, NavigableSet
- LinkedHashSet — insertion order preserved

### Queues & Deques
- ArrayDeque — preferred over Stack and LinkedList for queue/stack
- PriorityQueue — min-heap by default
- PriorityQueue with comparator: new PriorityQueue<>((a,b) -> b-a) for max-heap
- BlockingQueue for producer-consumer patterns

## Algorithms

### Sorting
Arrays.sort(arr); // primitives — Dual-Pivot Quicksort
Arrays.sort(arr, Comparator.comparingInt(User::getAge)); // objects
Collections.sort(list, (a, b) -> a.name.compareTo(b.name));
// Stable sort for objects, unstable for primitives

### Binary Search
int idx = Arrays.binarySearch(sortedArr, key);
// Returns index if found, negative value if not
// Manual: lo=0, hi=n-1, mid=(lo+hi)/2

### Dynamic Programming
- Use int[][] dp = new int[m][n] for 2D DP
- Initialize with Integer.MAX_VALUE or Integer.MIN_VALUE carefully
- Avoid overflow: use long when summing large int values

### Graph
- Adjacency list: Map<Integer, List<Integer>> graph = new HashMap<>()
- BFS: Queue<Integer> queue = new LinkedList<>() + boolean[] visited
- DFS: recursive or Deque<Integer> as explicit stack
- Dijkstra: PriorityQueue with custom comparator

## Idiomatic Java

### Streams API
list.stream()
    .filter(x -> x > 0)
    .map(x -> x * 2)
    .sorted()
    .collect(Collectors.toList());

// Grouping
Map<String, List<User>> byCity = users.stream()
    .collect(Collectors.groupingBy(User::getCity));

// Counting
long count = list.stream().filter(x -> x > 5).count();

// Optional
Optional<User> found = users.stream()
    .filter(u -> u.getId() == id)
    .findFirst();
found.ifPresent(u -> System.out.println(u.getName()));

### String Operations
- String.format("Hello %s", name)
- String.join(", ", list)
- String.valueOf(42) — convert to string
- StringBuilder for concatenation in loops
- String is immutable — never use += in loops
- str.split("\\s+") — split on whitespace

### Null Safety
- Use Optional<T> instead of returning null
- Objects.requireNonNull(param, "message")
- Avoid NullPointerException: check before dereference
- Use @NonNull/@Nullable annotations

### Records (Java 16+)
record Point(int x, int y) {} // immutable data class
// Auto-generates constructor, getters, equals, hashCode, toString

### Sealed Classes (Java 17+)
sealed interface Shape permits Circle, Square {}
record Circle(double radius) implements Shape {}
record Square(double side) implements Shape {}

## OOP Patterns

### Builder Pattern
User user = User.builder()
    .name("Alice")
    .age(30)
    .email("alice@example.com")
    .build();

### Factory Method
interface Animal { void speak(); }
class AnimalFactory {
    static Animal create(String type) {
        return switch(type) {
            case "dog" -> new Dog();
            case "cat" -> new Cat();
            default -> throw new IllegalArgumentException();
        };
    }
}

### Strategy Pattern
interface SortStrategy { void sort(int[] arr); }
class BubbleSort implements SortStrategy { ... }
class QuickSort implements SortStrategy { ... }

## Common Patterns

### Two Pointers
int left = 0, right = arr.length - 1;
while (left < right) {
    int sum = arr[left] + arr[right];
    if (sum == target) return new int[]{left, right};
    else if (sum < target) left++;
    else right--;
}

### BFS Template
Queue<Integer> queue = new LinkedList<>(List.of(start));
boolean[] visited = new boolean[n];
visited[start] = true;
while (!queue.isEmpty()) {
    int node = queue.poll();
    for (int neighbor : graph.get(node)) {
        if (!visited[neighbor]) {
            visited[neighbor] = true;
            queue.offer(neighbor);
        }
    }
}

## Performance Tips
- Prefer ArrayList over LinkedList for most use cases
- Use primitive arrays when possible — avoids boxing overhead
- StringBuilder instead of String concatenation in loops
- Avoid creating unnecessary objects in hot paths
- Use entrySet() instead of keySet() when you need both key and value
- Stream parallel(): only for CPU-bound tasks with large data

## Common Pitfalls
- Integer == Integer compares reference, not value — use .equals()
- int overflow: use long or Math.addExact()
- ConcurrentModificationException: don't modify collection while iterating
- Arrays.asList() returns fixed-size list — can't add/remove
- Collections.unmodifiableList() only makes wrapper immutable
- String.equals() not == for string comparison
