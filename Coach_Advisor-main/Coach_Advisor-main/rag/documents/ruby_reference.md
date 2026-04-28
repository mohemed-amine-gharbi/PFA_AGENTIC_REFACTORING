# Ruby — Best Practices & Algorithms Reference

## Data Structures

### Arrays
- arr = [] or arr = Array.new(n, default_value)
- arr.push(x) / arr << x — append
- arr.pop, arr.shift, arr.unshift(x)
- arr.sort — new sorted array
- arr.sort! — in-place sort
- arr.sort_by { |x| x.age } — sort by attribute
- arr.min, arr.max, arr.minmax
- Binary search: arr.bsearch { |x| x >= target } — requires sorted

### Merging Two Sorted Arrays
def merge_sorted(a, b)
  result = []
  i, j = 0, 0
  while i < a.length && j < b.length
    if a[i] <= b[j]; result << a[i]; i += 1
    else; result << b[j]; j += 1
    end
  end
  result + a[i..] + b[j..]
end
# Or: (a + b).sort — simpler but O((n+m)log(n+m))

### Hashes
- hash = {} or hash = Hash.new(0) — with default value
- hash[key] = value
- hash.fetch(key, default) — raises KeyError without default
- hash.dig(:user, :name) — nested access
- hash.select { |k,v| v > 0 } — filter
- hash.map { |k,v| [k, v*2] }.to_h — transform values
- hash.merge(other) { |key, old, new| old + new } — merge with block

### Sets
require 'set'
s = Set.new([1, 2, 3])
s.add(4); s.include?(3)
s1 & s2 (intersection), s1 | s2 (union), s1 - s2 (difference)

## Enumerable — Core Power of Ruby

### Transformation
arr.map { |x| x * 2 }
arr.flat_map { |x| [x, x*2] }
arr.each_with_object({}) { |x, h| h[x] = x**2 }
arr.zip([1,2,3]) # [[a1,1], [a2,2], ...]

### Filtering & Finding
arr.select { |x| x > 0 }
arr.reject { |x| x.nil? }
arr.find { |x| x > 5 }
arr.count { |x| x.even? }
arr.any? { |x| x > 10 }
arr.all? { |x| x > 0 }
arr.none? { |x| x.nil? }

### Aggregation
arr.sum { |x| x.amount }
arr.reduce(0) { |sum, x| sum + x }
arr.inject(:+) # sum shorthand
arr.group_by { |x| x.category }
arr.tally # count occurrences: ["a","b","a"] => {"a"=>2,"b"=>1}
arr.chunk_while { |a,b| b - a <= 1 } # group consecutive

### Chaining
users
  .select(&:active?)
  .sort_by(&:name)
  .first(10)
  .map { |u| { id: u.id, name: u.name } }

## Idiomatic Ruby

### Blocks, Procs, Lambdas
- Block: do |x| ... end or { |x| ... }
- Proc: Proc.new { |x| x * 2 } — loose argument handling
- Lambda: ->(x) { x * 2 } — strict argument handling
- & converts method to block: arr.map(&:upcase)
- yield calls the block passed to a method

### String Operations
- Interpolation: "Hello #{name}"
- Heredoc: <<~TEXT ... TEXT
- gsub, sub for replacement
- split, strip, chomp, chop
- String multiplication: "ha" * 3 => "hahaha"
- Symbols vs strings: :symbol for identifiers, frozen & faster

### Modules & Mixins
module Greetable
  def greet
    "Hello, #{name}"
  end
end
class User
  include Greetable  # mixin
  attr_reader :name
end
# extend for class-level methods
# prepend to override methods

### Method Missing & Dynamic Methods
def method_missing(name, *args)
  if name.to_s.start_with?("find_by_")
    # dynamic finder
  else
    super
  end
end

### Frozen String Literal
# frozen_string_literal: true
# At top of file — all literals frozen, reduces allocations

## Error Handling
begin
  result = risky_operation()
rescue ArgumentError => e
  puts "Bad argument: #{e.message}"
rescue StandardError => e
  puts "Error: #{e.message}"
ensure
  cleanup()
end
raise ArgumentError, "Value must be positive" if value < 0

## OOP Patterns

### attr_accessor
class Person
  attr_accessor :name, :age  # getter + setter
  attr_reader :id             # getter only
  attr_writer :email          # setter only
end

### Comparable
class Box
  include Comparable
  attr_accessor :volume
  def <=>(other)
    volume <=> other.volume
  end
end
# Now Box supports <, >, ==, sort, min, max

## Algorithms

### BFS
visited = Set.new([start])
queue = [start]
until queue.empty?
  node = queue.shift
  graph[node].each do |neighbor|
    unless visited.include?(neighbor)
      visited.add(neighbor)
      queue << neighbor
    end
  end
end

### Memoization
def fib(n, memo = {})
  return n if n <= 1
  memo[n] ||= fib(n-1, memo) + fib(n-2, memo)
end

## Common Pitfalls
- nil.method raises NoMethodError — use safe navigation &.
- Symbols and strings are different keys in hash
- Array#map vs Array#each: map returns new array
- puts vs print vs p: p calls inspect, useful for debugging
- Frozen string error: can't modify frozen String
- Thread safety: MRI GIL protects only Ruby code, not C extensions
