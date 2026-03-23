# PHP — Best Practices & Algorithms Reference

## Data Structures

### Arrays (PHP arrays are ordered maps)
- $arr = []; or $arr = array();
- array_push($arr, $val) or $arr[] = $val
- array_pop($arr), array_shift($arr), array_unshift($arr, $val)
- sort($arr) — in-place, reindexes
- usort($arr, fn($a,$b) => $a['age'] <=> $b['age']) — custom sort
- rsort — reverse sort
- asort — sort preserving keys
- ksort — sort by key

### Merging Sorted Arrays
function mergeSorted(array $a, array $b): array {
    $result = [];
    $i = $j = 0;
    while ($i < count($a) && $j < count($b)) {
        if ($a[$i] <= $b[$j]) $result[] = $a[$i++];
        else $result[] = $b[$j++];
    }
    return array_merge($result, array_slice($a, $i), array_slice($b, $j));
}
// Simple but slower: array_merge($a, $b) then sort()

### Array Functions
array_map(fn($x) => $x * 2, $arr)
array_filter($arr, fn($x) => $x > 0)
array_reduce($arr, fn($carry, $item) => $carry + $item, 0)
array_unique($arr) — remove duplicates
array_flip($arr) — swap keys and values
array_combine($keys, $values) — create from two arrays
array_chunk($arr, 3) — split into chunks
array_slice($arr, $offset, $length)
in_array($val, $arr) — O(n) search
array_search($val, $arr) — returns key or false
array_keys($arr), array_values($arr)
array_column($records, 'name') — pluck column

### Associative Arrays
$user = ['name' => 'Alice', 'age' => 30];
isset($user['email']) — check key exists
$user['email'] ?? 'default' — null coalescing
array_key_exists('name', $user) — explicit check
array_merge($defaults, $overrides) — merge, later wins

## Modern PHP (8.x)

### Types
function add(int $a, int $b): int { return $a + $b; }
function findUser(int $id): ?User { ... } // nullable
Union types: int|string
Intersection types: Countable&Traversable

### Match Expression
$result = match($status) {
    'active' => 'User is active',
    'banned', 'suspended' => 'Account restricted',
    default => 'Unknown status',
};
// Strict comparison, no type coercion, must be exhaustive

### Named Arguments
array_slice(array: $arr, offset: 2, length: 3, preserve_keys: true);

### Constructor Promotion
class User {
    public function __construct(
        private readonly string $name,
        private int $age = 0,
    ) {}
}

### Enums (PHP 8.1)
enum Status: string {
    case Active = 'active';
    case Banned = 'banned';
}
$s = Status::Active;
$s->value; // 'active'

### Fibers (PHP 8.1)
$fiber = new Fiber(function(): void {
    $value = Fiber::suspend('first');
    echo "Got: $value\n";
});
$value = $fiber->start();
$fiber->resume('hello');

## OOP

### Abstract Classes & Interfaces
interface Sortable {
    public function sort(): void;
}
abstract class Collection implements Sortable {
    abstract protected function validate(mixed $item): bool;
}

### Traits
trait Timestampable {
    private DateTime $createdAt;
    public function setCreatedAt(): void {
        $this->createdAt = new DateTime();
    }
}
class Post { use Timestampable; }

### Magic Methods
__construct, __destruct
__get($name), __set($name, $value) — property overloading
__call($name, $args) — method overloading
__toString() — string casting
__invoke() — call object as function

## Error Handling

### Exceptions
try {
    $result = riskyOperation();
} catch (InvalidArgumentException $e) {
    log($e->getMessage());
} catch (RuntimeException|LogicException $e) {
    handle($e);
} finally {
    cleanup();
}
throw new InvalidArgumentException("Value must be positive");

### Custom Exceptions
class ValidationException extends RuntimeException {
    public function __construct(
        private array $errors,
        string $message = '',
    ) {
        parent::__construct($message ?: implode(', ', $errors));
    }
    public function getErrors(): array { return $this->errors; }
}

## String Operations
sprintf("Hello %s, you are %d", $name, $age)
str_contains($str, 'needle') — PHP 8.0+
str_starts_with($str, 'prefix')
str_ends_with($str, 'suffix')
trim, ltrim, rtrim
explode(',', $str) — split
implode(', ', $arr) — join
preg_match('/pattern/', $str, $matches)
preg_replace('/pattern/', $replacement, $str)

## Algorithms

### BFS
$visited = [$start => true];
$queue = [$start];
while (!empty($queue)) {
    $node = array_shift($queue);
    foreach ($graph[$node] as $neighbor) {
        if (!isset($visited[$neighbor])) {
            $visited[$neighbor] = true;
            $queue[] = $neighbor;
        }
    }
}

### Binary Search
function binarySearch(array $arr, int $target): int {
    $lo = 0; $hi = count($arr) - 1;
    while ($lo <= $hi) {
        $mid = intdiv($lo + $hi, 2);
        if ($arr[$mid] === $target) return $mid;
        elseif ($arr[$mid] < $target) $lo = $mid + 1;
        else $hi = $mid - 1;
    }
    return -1;
}

## Common Pitfalls
- == vs ===: "0" == false is true — always use ===
- array_shift() is O(n) — use SplQueue for frequent dequeues
- count() is O(1) for arrays, but cache for objects implementing Countable
- Integer division: use intdiv() not /
- Floating point comparison: use abs($a-$b) < PHP_FLOAT_EPSILON
- Never use extract() — pollutes variable scope
- Avoid variable variables ($$var)
- Type juggling with loose comparisons causes bugs
