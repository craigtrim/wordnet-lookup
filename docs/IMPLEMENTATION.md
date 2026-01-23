# Implementation Notes

Technical deep-dive into the hash-based lookup system.

## Why Hashes?

The original implementation used 26 Python lists organized alphabetically (A-Z). This had two problems:

1. **O(n) lookups**: `in` on a Python list scans linearly
2. **Uneven distribution**: The 's' bucket had 9,389 entries; 'x' had 171

Hashing solves both: MD5 distributes uniformly across 256 buckets, and `frozenset` provides O(1) membership testing.

## Why MD5?

MD5 is:
- **Fast**: ~300ns per hash on modern hardware
- **Uniform**: Excellent distribution for non-cryptographic use
- **Sufficient**: Cryptographic weakness irrelevant for lookup tables

We only store the suffix (30 chars) after splitting on the 2-char prefix, saving ~6% space per entry.

## Why frozenset?

| Data Structure | Lookup | Memory | Mutability |
|---------------|--------|--------|------------|
| list | O(n) | Lower | Mutable |
| set | O(1) | Higher | Mutable |
| frozenset | O(1) | Higher | Immutable |

`frozenset` wins because:
- O(1) average-case lookup via hash table
- Immutability allows Python to optimize memory layout
- Hashable (can be used as dict keys if needed)

## Why 256 Buckets?

Two hex characters = 16 × 16 = 256 possible prefixes. This gives:
- ~344 entries per bucket on average (88,013 ÷ 256)
- Small enough files for fast imports
- Uniform distribution (MD5 property)

One hex character (16 buckets) = ~5,500 entries each = slower imports.
Three hex characters (4,096 buckets) = too many tiny files.

## Why Lazy Loading?

Eager loading imports all 256 modules at startup:
```python
from wordnet_lookup.hs import hashes_00, hashes_01, ...  # 256 imports
```

Problems:
- Slow startup (~500ms to load 88k strings)
- Memory for all 256 sets even if only a few are used

Lazy loading with caching:
```python
def _get_hash_set(prefix: str) -> frozenset:
    if prefix not in _cache:
        module = importlib.import_module(f'wordnet_lookup.hs.h_{prefix}')
        _cache[prefix] = getattr(module, f'hashes_{prefix}')
    return _cache[prefix]
```

Benefits:
- Fast startup (near-zero)
- Only loads buckets actually accessed
- Cached after first access per prefix

## Hash Function

```python
def _calculate_md5(input_text: str) -> str:
    return hashlib.md5(input_text.lower().strip().encode()).hexdigest()
```

Input normalization:
- `.lower()`: Case-insensitive matching
- `.strip()`: Ignore leading/trailing whitespace
- `.encode()`: UTF-8 bytes for hashing

The same normalization is applied at build time and lookup time.

## Lookup Flow

```
Input: "Hello"
    │
    ▼
Normalize: "hello"
    │
    ▼
MD5: "5d41402abc4b2a76b9719d911017c592"
    │
    ▼
Split: prefix="5d", suffix="41402abc4b2a76b9719d911017c592"
    │
    ▼
Load: importlib.import_module('wordnet_lookup.hs.h_5d')
    │
    ▼
Check: "41402abc4b2a76b9719d911017c592" in hashes_5d
    │
    ▼
Return: True/False
```

## Plural Handling

If the word ends with 's' and isn't found, try the singular:

```python
if input_text.endswith('s') and len(input_text) > 3:
    if _hash_exists(input_text[:-1]):
        return True
```

This catches regular plurals like "computers" → "computer".

Limitation: Doesn't handle irregular plurals ("mice" → "mouse").

## Build Process

The `builder/build_hash_files.py` script:

1. Reads `wordnet_words.txt` (88,013 words, one per line)
2. Hashes each word with MD5
3. Groups by first 2 hex chars of hash
4. Writes 256 Python files with `frozenset` literals
5. Generates `__init__.py` with imports

```python
# Example generated file: h_5d.py
hashes_5d = frozenset({
    '41402abc4b2a76b9719d911017c592',
    '8f14e45fceea167a5a36dedd4bea254',
    ...
})
```

## Performance Characteristics

| Operation | Complexity | Typical Time |
|-----------|------------|--------------|
| Hash computation | O(n) string length | ~300ns |
| Bucket lookup | O(1) dict access | ~50ns |
| Set membership | O(1) average | ~50ns |
| Module import (cold) | O(n) entries | ~2ms |
| Module import (cached) | O(1) | ~50ns |

Total lookup time: ~400ns warm, ~2ms cold (first access to a bucket).

## Memory Usage

- Each hash suffix: 30 chars = ~80 bytes (Python string overhead)
- 88,013 entries × 80 bytes ≈ 7 MB if all loaded
- Lazy loading: Only used buckets in memory
- Typical usage: 10-50 buckets = 0.3-1.8 MB

## Collision Resistance

MD5 collision probability for 88k entries:

```
P(collision) ≈ n² / 2^129
            ≈ (88000)² / 2^129
            ≈ 10^-30
```

Effectively zero. And collisions would only cause false positives (saying a non-word exists), not false negatives.

## Why Not Bloom Filters?

Bloom filters are space-efficient probabilistic sets with false positives. They'd work here, but:

1. `frozenset` is fast enough
2. Zero false positives with sets
3. Simpler implementation
4. No bit manipulation or multiple hash functions

For 88k entries, the space savings aren't worth the complexity.

## Future Optimizations

Potential improvements (not implemented):

1. **Single binary file**: Pack all hashes into one file, memory-map it
2. **Perfect hashing**: Eliminate collision chains entirely
3. **Compile to C extension**: For extreme performance needs

Current implementation is fast enough for most use cases.
