# Rust — Best Practices & Algorithms Reference

## Ownership & Borrowing

### Ownership Rules
- Each value has exactly one owner
- When owner goes out of scope, value is dropped (freed)
- Move semantics by default for non-Copy types
- Implement Copy trait for cheap types (integers, booleans, references)
- Clone explicitly for deep copy: let b = a.clone();

### Borrowing
- &T: shared (immutable) reference — multiple allowed
- &mut T: exclusive (mutable) reference — only one at a time
- References must not outlive the value they point to
- Cannot have &mut and & active simultaneously

### Lifetimes
- 'a lifetime annotation: fn longest<'a>(x: &'a str, y: &'a str) -> &'a str
- Needed when compiler can't infer relationship between references
- Lifetime elision rules handle most common cases automatically
- 'static: lives entire program duration (string literals)

## Data Structures

### Vec<T>
- let mut v: Vec<i32> = Vec::new();
- let v = vec![1, 2, 3]; // macro
- v.push(4); v.pop();
- v.sort(); v.sort_by(|a, b| a.cmp(b));
- v.sort_by_key(|x| x.len());
- Binary search: v.binary_search(&target) — returns Result<usize, usize>

### Merging Two Sorted Vecs
fn merge_sorted(a: &[i32], b: &[i32]) -> Vec<i32> {
    let mut result = Vec::with_capacity(a.len() + b.len());
    let (mut i, mut j) = (0, 0);
    while i < a.len() && j < b.len() {
        if a[i] <= b[j] { result.push(a[i]); i += 1; }
        else { result.push(b[j]); j += 1; }
    }
    result.extend_from_slice(&a[i..]);
    result.extend_from_slice(&b[j..]);
    result
}
// Or: use itertools::merge_sorted

### HashMap & HashSet
use std::collections::{HashMap, HashSet};
let mut map: HashMap<String, i32> = HashMap::new();
map.insert("key".to_string(), 42);
map.entry("key".to_string()).or_insert(0) += 1; // increment or init
let val = map.get("key"); // returns Option<&i32>

### BTreeMap / BTreeSet
- Sorted order, O(log n) operations
- Use when you need ordered iteration
- BTreeMap::range() for range queries

### VecDeque
use std::collections::VecDeque;
let mut dq = VecDeque::new();
dq.push_back(1); dq.push_front(0);
dq.pop_front(); dq.pop_back();
// O(1) at both ends, use for BFS queues

## Error Handling

### Result<T, E>
fn parse(s: &str) -> Result<i32, ParseIntError> {
    s.parse::<i32>()
}
match parse("42") {
    Ok(n) => println!("{}", n),
    Err(e) => eprintln!("Error: {}", e),
}
// ? operator — propagate error
fn process(s: &str) -> Result<i32, ParseIntError> {
    let n = s.parse::<i32>()?; // returns Err if fails
    Ok(n * 2)
}

### Option<T>
let v = vec![1, 2, 3];
let first = v.first(); // Option<&i32>
first.unwrap_or(&0); // default value
first.map(|x| x * 2); // transform if Some
first.and_then(|x| if *x > 0 { Some(x) } else { None });
if let Some(val) = first { ... }

### Custom Error Types
use std::fmt;
#[derive(Debug)]
enum AppError {
    NotFound(String),
    ParseError(String),
}
impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            AppError::NotFound(s) => write!(f, "Not found: {}", s),
            AppError::ParseError(s) => write!(f, "Parse error: {}", s),
        }
    }
}
// Use thiserror or anyhow crates for production

## Traits & Generics

### Defining Traits
trait Summary {
    fn summarize(&self) -> String;
    fn default_impl(&self) -> String { // default implementation
        String::from("(Read more...)")
    }
}
impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{}: {}", self.title, self.author)
    }
}

### Generics with Trait Bounds
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list { if item > largest { largest = item; } }
    largest
}
// Or with where clause:
fn process<T>(x: T) where T: Display + Clone { ... }

### Common Traits
- Clone, Copy, Debug, Display, PartialEq, Eq, PartialOrd, Ord
- Iterator: implement next() method, get map/filter/collect for free
- From/Into: type conversion
- Default: zero value
- Deref: coercion (String → &str)

## Iterators

### Chaining
let sum: i32 = (1..=10)
    .filter(|x| x % 2 == 0)
    .map(|x| x * x)
    .sum();

let words: Vec<&str> = text.split_whitespace().collect();
let unique: HashSet<_> = v.iter().cloned().collect();
let max = v.iter().max(); // Option<&T>
let (evens, odds): (Vec<_>, Vec<_>) = v.iter().partition(|&&x| x % 2 == 0);

## Concurrency

### Threads
use std::thread;
let handle = thread::spawn(|| { /* work */ });
handle.join().unwrap();

### Arc & Mutex
use std::sync::{Arc, Mutex};
let data = Arc::new(Mutex::new(vec![1, 2, 3]));
let data_clone = Arc::clone(&data);
thread::spawn(move || {
    let mut v = data_clone.lock().unwrap();
    v.push(4);
});

### Channels
use std::sync::mpsc;
let (tx, rx) = mpsc::channel();
thread::spawn(move || { tx.send(42).unwrap(); });
let val = rx.recv().unwrap();

## Common Pitfalls
- Cannot move out of borrowed context — borrow or clone
- Mutable borrow while immutable borrow active — restructure code
- Using unwrap() in production — use ? or match instead
- Integer overflow in debug mode panics, release mode wraps
- Mutex deadlock: don't lock same mutex twice in same thread
- collect() needs type annotation: let v: Vec<_> = ...
