# C — Best Practices & Algorithms Reference

## Memory Management

### malloc / free
- Always check malloc return value: if (ptr == NULL) { handle error }
- Free every malloc — use valgrind to detect leaks
- Never access freed memory (use-after-free)
- Never double-free
- calloc(n, size) — allocates and zeroes memory
- realloc(ptr, new_size) — resize allocation, returns NULL on failure

### Stack vs Heap
- Stack: local variables — fast, automatic cleanup, limited size (~1-8MB)
- Heap: malloc/calloc — explicit management, large allocations
- Return values from functions: never return pointer to local stack variable
- Use static for persistence without heap allocation

### Pointer Arithmetic
- ptr + n advances by n * sizeof(*ptr) bytes
- Array and pointer interchangeable: arr[i] == *(arr + i)
- NULL pointer check before dereference
- void* for generic pointers — cast before use

## Data Structures in C

### Arrays
- Fixed size at compile time: int arr[100];
- VLA (variable length array): int arr[n]; — avoid in modern C
- Dynamic: int *arr = malloc(n * sizeof(int));
- Sorting: qsort(arr, n, sizeof(int), compare_fn)
- qsort comparator: int cmp(const void *a, const void *b) { return *(int*)a - *(int*)b; }

### Merging Two Sorted Arrays
- Allocate result array: int *result = malloc((n+m) * sizeof(int));
- Two-pointer: i=0, j=0, k=0; compare arr1[i] vs arr2[j]
- Copy remaining elements after one array exhausted
- Free result when done
- Time O(n+m), Space O(n+m)

### Linked List
struct Node {
    int data;
    struct Node *next;
};
- Insert at head: O(1), Insert at tail: O(n) without tail pointer
- Always set next = NULL for new nodes
- Free: traverse and free each node

### Stack with Array
#define MAX 100
int stack[MAX];
int top = -1;
void push(int x) { stack[++top] = x; }
int pop() { return stack[top--]; }
int peek() { return stack[top]; }

### Hash Table (open addressing)
- djb2 hash: hash = hash * 33 + c
- Linear probing for collision resolution
- Load factor < 0.7 for good performance
- Resize when load factor exceeded

## Algorithms

### Sorting
- qsort: stdlib.h, O(n log n) average, not stable
- Merge sort: stable, O(n log n), requires O(n) extra space
- Insertion sort: O(n^2) but fast for nearly sorted, in-place

### Binary Search
int binary_search(int *arr, int n, int target) {
    int lo = 0, hi = n - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2; // avoid overflow
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
Note: mid = lo + (hi - lo) / 2 to prevent integer overflow

### Recursion
- Always define base case first
- Check stack depth for deep recursion — default ~1MB
- Convert to iterative with explicit stack when depth is large

## String Handling

### C Strings
- Null-terminated: last char is '\0'
- strcpy(dst, src) — always ensure dst has enough space
- strncpy(dst, src, n) — safer, always add null terminator
- strcat, strncat — append strings
- strlen — O(n) every call — cache the result
- strcmp: returns 0 if equal, negative/positive otherwise
- sprintf, snprintf — format into string buffer

### Safe String Operations
- Always use snprintf instead of sprintf
- Always use strncmp instead of strcmp when length matters
- Use strtok_r (reentrant) instead of strtok in multi-threaded code

## Idiomatic C

### Struct Patterns
typedef struct {
    int x;
    int y;
} Point;
Point p = {.x = 1, .y = 2}; // designated initializers

### Function Pointers
int (*compare)(const void *, const void *);
compare = my_compare_fn;
// Used in callbacks, qsort, generic containers

### Error Handling
- Return 0 for success, -1 or error code for failure
- Use errno for system errors (errno.h)
- perror("message") prints errno description
- Always propagate errors up the call chain

### Macros
#define MAX(a, b) ((a) > (b) ? (a) : (b))
// Always parenthesize arguments in macros
// Use static inline functions instead of macros when possible

### Bit Manipulation
- Set bit: x |= (1 << n)
- Clear bit: x &= ~(1 << n)
- Toggle bit: x ^= (1 << n)
- Check bit: x & (1 << n)
- Count bits: __builtin_popcount(x)

## Common Patterns

### Merge Two Sorted Arrays
int *merge_sorted(int *a, int n, int *b, int m) {
    int *result = malloc((n + m) * sizeof(int));
    int i = 0, j = 0, k = 0;
    while (i < n && j < m)
        result[k++] = (a[i] <= b[j]) ? a[i++] : b[j++];
    while (i < n) result[k++] = a[i++];
    while (j < m) result[k++] = b[j++];
    return result;
}

### Dynamic Array (Vector)
typedef struct {
    int *data;
    int size;
    int capacity;
} Vec;
void vec_push(Vec *v, int x) {
    if (v->size == v->capacity) {
        v->capacity *= 2;
        v->data = realloc(v->data, v->capacity * sizeof(int));
    }
    v->data[v->size++] = x;
}

## Common Pitfalls
- Buffer overflow: writing past array bounds — always bounds check
- Off-by-one: array indices 0 to n-1, not 1 to n
- Uninitialized variables — always initialize
- Integer overflow: use long or unsigned carefully
- Signed/unsigned comparison warnings — take seriously
- Forgetting to null-terminate strings
- Returning address of local variable
