# Implementation Notes

Technical deep-dive into the hash-based lookup system.

---

## Architecture Overview

The library has two parallel lookup systems, both using the same structural pattern: 256 lazy-loaded Python modules bucketed by MD5 prefix.

| System | Modules | Data type | Purpose |
|--------|---------|-----------|---------|
| `hs/` | `h_00.py` … `h_ff.py` | `frozenset` of hash suffixes | Word existence |
| `sx/` | `sx_00.py` … `sx_ff.py` | `dict[hash_suffix → pipe_string]` | Suffix extraction |

---

## Existence Lookup (`hs/`)

### Why Hashes?

The original implementation used 26 Python lists organized alphabetically (A-Z). Two problems:

1. **O(n) lookups** — `in` on a Python list scans linearly
2. **Uneven distribution** — the `'s'` bucket had 9,389 entries; `'x'` had 171

MD5 hashing solves both: uniform distribution across 256 buckets, and `frozenset` gives O(1) membership testing.

### Why MD5?

- **Fast** — ~300 ns per hash on modern hardware
- **Uniform** — excellent distribution for non-cryptographic use
- **Sufficient** — cryptographic weakness is irrelevant for lookup tables

Only the suffix (30 chars) is stored per entry; the 2-char prefix is encoded in the module name, saving ~6% space.

### Why `frozenset`?

| Structure | Lookup | Mutability |
|-----------|--------|------------|
| `list` | O(n) | Mutable |
| `set` | O(1) | Mutable |
| `frozenset` | O(1) | **Immutable** |

`frozenset` wins because immutability lets Python optimize memory layout, and hashability allows future use as dict keys if needed.

### Why 256 Buckets?

Two hex chars = 16 × 16 = 256 possible prefixes.

- ~344 entries per bucket on average (88,013 ÷ 256)
- Small enough for fast imports
- 16 buckets (1 hex char) → ~5,500 entries each → slower imports
- 4,096 buckets (3 hex chars) → too many tiny files

### Lazy Loading

All 256 modules are not loaded at startup. Each bucket is imported on first access and cached:

```python
_cache = {}

def _get_hash_set(prefix: str) -> frozenset:
    if prefix not in _cache:
        module = importlib.import_module(f'wordnet_lookup.hs.h_{prefix}')
        _cache[prefix] = getattr(module, f'hashes_{prefix}')
    return _cache[prefix]
```

Benefits:
- Near-zero startup time
- Only the buckets actually accessed are loaded
- Memory proportional to usage, not corpus size

### Lookup Flow

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
Split: prefix="5d", key="41402abc4b2a76b9719d911017c592"
    │
    ▼
Load: h_5d.hashes_5d  (frozenset, cached after first use)
    │
    ▼
Check: key in hashes_5d  → True/False
```

### Normalization Pipeline

```python
def exists(self, input_text: str) -> bool:
    input_text = input_text.lower().strip()

    # 1. Direct hash lookup
    if _hash_exists(input_text):
        return True

    # 2. Unicode normalization (e.g. 'naïve' → 'naive')
    normalized = unicodedata.normalize('NFKD', input_text)\
        .encode('ascii', 'ignore').decode('ascii')
    if normalized != input_text and _hash_exists(normalized):
        return True

    # 3. Plural stripping (e.g. 'computers' → 'computer')
    if normalized.endswith('s') and len(normalized) > 3:
        if _hash_exists(normalized[:-1]):
            return True

    return False
```

**Plural handling note:** strips a trailing `'s'` if the word is longer than 3 characters. Catches regular plurals only — irregular forms (`mice`, `geese`, `children`) are not handled.

---

## Suffix Lookup (`sx/`)

### Data Source

Suffix data is pre-computed by [morphroot](https://github.com/craigtrim/morphroot) (see issue [#10](https://github.com/craigtrim/morphroot/issues/10)). The builder runs `extract_suffixes()` over all 88,013 WordNet words and produces the `sx/` modules.

Re-run when suffix extraction logic changes:

```bash
# in morphroot repo
make wordnet-suffixes
# then commit updated sx/ modules in wordnet-lookup
```

### Storage Format

Each `sx_XX.py` module contains a `dict` mapping the 30-char hash suffix to a pipe-delimited suffix string:

```python
# sx_3a.py
suffixes_3a = {
    'f2d...': 'ness',
    'a1c...': 'ful|ly',
    '9b7...': 'al|ize|ed',
    ...
}
```

`dict` (not `frozenset`) because values must be retrieved, not just tested for membership.

### Lookup Flow

```
Input: 'beautifully'
    │
    ▼
Normalize: 'beautifully'
    │
    ▼
MD5 → prefix + key
    │
    ▼
sx_XX dict lookup → 'ful|ly'  (or None if not in dict)
    │
    ├─ Found → split('|') → ['ful', 'ly']
    │
    └─ Not found
           │
           ▼
       FindWordnet().exists(word)?
           │
           ├─ True  → return []   (in WordNet, no suffixes recorded)
           └─ False → return None (not a WordNet word)
```

### `None` vs `[]` Contract

This is intentional and load-bearing:

```python
suffixes = get_suffixes(word)

if suffixes is None:
    # word is not in WordNet — discard entirely
elif suffixes == []:
    # word is in WordNet, morphologically simple
else:
    # word is in WordNet with derivational structure
```

Callers can use `get_suffixes()` as a single combined existence + morphology check, avoiding a separate `is_wordnet_term()` call.

### Coverage

| Metric | Value |
|--------|-------|
| Total words in corpus | 88,013 |
| Words with suffix data | 30,335 (34%) |
| Monomorphemic words | 57,678 (66%) |
| Parquet file (source) | 225 KB (snappy compressed) |

---

## Memory Usage

| Scenario | Approximate Memory |
|----------|--------------------|
| Cold start (no lookups) | ~0 MB |
| 1 bucket loaded | ~0.07 MB |
| 10 buckets loaded | ~0.7 MB |
| All 256 buckets loaded | ~7 MB (existence) + ~5 MB (suffix) |

Each hash suffix string: 30 chars ≈ 80 bytes including Python object overhead.

---

## Performance Characteristics

| Operation | Complexity | Typical Time |
|-----------|------------|--------------|
| Hash computation | O(k) input length | ~300 ns |
| Bucket dict lookup | O(1) | ~50 ns |
| Frozenset/dict membership | O(1) average | ~50 ns |
| Module import (cold) | O(n) entries | ~2 ms |
| Module import (cached) | O(1) | ~50 ns |

**Total per warm lookup: ~400 ns**

---

## Collision Resistance

MD5 collision probability for 88,013 entries:

```
P(collision) ≈ n² / 2^129
             ≈ (88,013)² / 2^129
             ≈ 10⁻³⁰
```

Effectively zero. A collision would cause a false positive (a non-word reported as valid), never a false negative. Acceptable for this use case.

---

## Build Process

### Existence hashes (`hs/`)

`builder/build_hash_files.py`:

1. Reads `builder/wordnet_words.txt` (88,013 words, one per line)
2. MD5-hashes each word
3. Groups by first 2 hex chars
4. Writes 256 `hs/h_XX.py` files with `frozenset` literals

```python
# Example generated file: h_5d.py
hashes_5d = frozenset({
    '41402abc4b2a76b9719d911017c592',
    '8f14e45fceea167a5a36dedd4bea254',
    ...
})
```

### Suffix data (`sx/`)

Built by [morphroot](https://github.com/craigtrim/morphroot):

1. Runs morphological analysis over all 88,013 words
2. Produces hash → pipe-string mappings
3. Writes 256 `sx/sx_XX.py` files with `dict` literals

```python
# Example generated file: sx_3a.py
suffixes_3a = {
    'f2d9...': 'ness',
    'a1c7...': 'ful|ly',
    ...
}
```

---

## Design Decisions

### Why not Bloom filters?

Bloom filters are space-efficient probabilistic sets, but:
- `frozenset` is already fast enough (~50 ns)
- Zero false positives — Bloom filters have inherent false positive rate
- Simpler implementation — no bit manipulation or multiple hash functions

For 88k entries, space savings don't justify the added complexity.

### Why not a single binary file?

Possible optimization: pack all hashes into one memory-mapped binary file. Rejected because:
- Current lazy-loading already gives near-zero startup time
- Memory-mapped I/O adds platform-specific complexity
- Per-bucket Python modules are trivially inspectable and debuggable

### Why not a SQLite database?

- Requires file I/O on every lookup
- Adds disk I/O latency (~100 µs vs ~400 ns)
- Deployment complexity (file path management)

Frozenset buckets in Python modules sidestep all of this.
