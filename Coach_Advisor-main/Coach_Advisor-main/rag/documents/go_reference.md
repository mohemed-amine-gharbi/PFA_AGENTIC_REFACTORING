# Go — Best Practices & Algorithms Reference

## Data Structures

### Slices
- var s []int — nil slice (preferred zero value)
- s := make([]int, len, cap) — with length and capacity
- append(s, val) — may reallocate, always capture return value
- s[lo:hi] — slice of slice, shares underlying array
- copy(dst, src) — deep copy elements
- Sort: sort.Slice(s, func(i, j int) bool { return s[i] < s[j] })
- Search: sort.SearchInts(s, val) — binary search on sorted

### Maps
- m := make(map[string]int) — always initialize with make
- val, ok := m[key] — two-value form to check existence
- delete(m, key)
- Iterate: for k, v := range m { ... }
- Maps are not ordered — use sorted keys for deterministic output
- Not safe for concurrent access — use sync.Map or mutex

### Merging Two Sorted Slices
func mergeSorted(a, b []int) []int {
    result := make([]int, 0, len(a)+len(b))
    i, j := 0, 0
    for i < len(a) && j < len(b) {
        if a[i] <= b[j] { result = append(result, a[i]); i++ } 
        else { result = append(result, b[j]); j++ }
    }
    result = append(result, a[i:]...)
    result = append(result, b[j:]...)
    return result
}

### Structs
type Point struct {
    X, Y int
}
p := Point{X: 1, Y: 2}
// Embedding for composition
type Circle struct {
    Point  // embedded — promotes X, Y, methods
    Radius float64
}

## Interfaces & Polymorphism

### Interface Definition
type Sorter interface {
    Len() int
    Less(i, j int) bool
    Swap(i, j int)
}
// Interfaces satisfied implicitly — no implements keyword

### sort.Interface
- Implement Len(), Less(), Swap() for custom sort
- sort.Sort(mySorter)
- Or use sort.Slice for simpler cases

### Empty Interface
- interface{} or any (Go 1.18+) — holds any type
- Type assertion: val, ok := x.(string)
- Type switch: switch v := x.(type) { case string: ... }

## Goroutines & Concurrency

### Goroutines
go func() { ... }() — launch goroutine
// Goroutines are cheap — thousands are normal
// Never access shared data without synchronization

### Channels
ch := make(chan int)       // unbuffered
ch := make(chan int, 100)  // buffered
ch <- val   // send (blocks if unbuffered/full)
val := <-ch // receive (blocks if empty)
close(ch)   // signals no more values
for v := range ch { ... } // receive until closed

### Select
select {
case msg := <-ch1: // receive from ch1
case ch2 <- val:   // send to ch2
case <-time.After(1 * time.Second): // timeout
default:           // non-blocking
}

### sync Package
- sync.Mutex: mu.Lock() / mu.Unlock()
- sync.RWMutex: multiple readers, exclusive writer
- sync.WaitGroup: wg.Add(1), wg.Done(), wg.Wait()
- sync.Once: run function exactly once
- sync.Map: concurrent-safe map

## Error Handling

### Error Pattern
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}
result, err := divide(10, 2)
if err != nil {
    // handle error
}

### Custom Errors
type ValidationError struct {
    Field   string
    Message string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

### Error Wrapping (Go 1.13+)
return fmt.Errorf("context: %w", err) // wrap
errors.Is(err, targetErr)              // unwrap check
errors.As(err, &targetType)            // type check

## Idioms

### Defer
defer file.Close()        // runs when function returns
defer mu.Unlock()         // always paired with Lock
// Deferred calls execute LIFO

### Variadic Functions
func sum(nums ...int) int {
    total := 0
    for _, n := range nums { total += n }
    return total
}
sum(1, 2, 3)
sum(nums...)  // pass slice

### Init Pattern
var once sync.Once
var instance *Service
func getInstance() *Service {
    once.Do(func() { instance = &Service{} })
    return instance
}

### Functional Options
type Option func(*Server)
func WithTimeout(d time.Duration) Option {
    return func(s *Server) { s.timeout = d }
}
func NewServer(opts ...Option) *Server {
    s := &Server{timeout: 30 * time.Second}
    for _, opt := range opts { opt(s) }
    return s
}

## Algorithms

### BFS
visited := make(map[int]bool)
queue := []int{start}
visited[start] = true
for len(queue) > 0 {
    node := queue[0]
    queue = queue[1:] // or use proper queue
    for _, neighbor := range graph[node] {
        if !visited[neighbor] {
            visited[neighbor] = true
            queue = append(queue, neighbor)
        }
    }
}

## Common Pitfalls
- Nil map write panics — always initialize with make()
- Goroutine leak — ensure goroutines can exit
- Closing channel twice panics
- Range variable capture in goroutines — capture by copy
- Slice append may or may not share underlying array
- defer in loop: defer runs at function end, not loop iteration
- interface{} comparison can panic if type not comparable
