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

1. **O(n) lookups** - `in` on a Python list scans linearly
2. **Uneven distribution** - the `'s'` bucket had 9,389 entries; `'x'` had 171

MD5 hashing solves both: uniform distribution across 256 buckets, and `frozenset` gives O(1) membership testing.

### Why MD5?

- **Fast** - ~300 ns per hash on modern hardware
- **Uniform** - excellent distribution for non-cryptographic use
- **Sufficient** - cryptographic weakness is irrelevant for lookup tables

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

**Plural handling note:** strips a trailing `'s'` if the word is longer than 3 characters. Catches regular plurals only - irregular forms (`mice`, `geese`, `children`) are not handled.

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
    # word is not in WordNet - discard entirely
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

## Inflectional Suffix Detection (`find_inflections.py`)

### What it covers

Unlike derivational suffixes (pre-computed), inflectional suffixes are detected at runtime by stripping each candidate ending and validating the recovered stem against WordNet.

Inflectional endings tried (longest-first to prevent prefix shadowing):

```python
_INFLECTIONAL = ['est', 'ing', 'ed', 'es', 's']
```

Longest-first ordering matters: `est` must be tried before `s`, or `fastest` would incorrectly match on `-s` -> `fastes` (not a word) before trying `fastest` -> `fast`.

### Comparative -er exclusion

`-er` is intentionally absent. Without part-of-speech data, `er` is ambiguous:

- Inflectional (comparative): `faster` -> `fast`
- Derivational (agentive): `teacher` -> `teach`, `runner` -> `run`

Agentive `-er` is already handled by `get_suffixes()` from pre-computed data. Including `-er` in inflectional detection would cause false positives and double-counting. Callers who need comparative forms should use POS-tagged pipelines.

### Allomorphic restoration

Stripping a suffix does not always yield the base form directly. Four allomorphs are tried for each stem:

```
1. Direct         : walk   (walked -> walk)
2. E-restore      : hope   (hoped  -> hop + e)
3. Consonant-drop : run    (running -> runn -> run)
4. Y-restore      : happy  (happiest -> happi -> happy)
```

E-restore is only attempted for suffixes in `_E_DROP_TRIGGERS = {'ing', 'ed', 'er', 'est'}` because e-drop does not occur with `-s` or `-es`.

```python
def _candidates(stem: str, suffix: str) -> list[str]:
    candidates = [stem]                          # 1. Direct
    if suffix in _E_DROP_TRIGGERS:
        candidates.append(stem + 'e')            # 2. E-restore
    if len(stem) >= 2 and stem[-1] == stem[-2]:
        candidates.append(stem[:-1])             # 3. Consonant-drop
    if stem.endswith('i'):
        candidates.append(stem[:-1] + 'y')       # 4. Y-restore
    return candidates
```

### Lookup flow

```
Input: "running"
    |
    v
Normalize: "running"
    |
    v
FindWordnet().exists("running") -> True  ->  return []   (base form in WordNet)

Input: "cats"
    |
    v
Normalize: "cats"
    |
    v
FindWordnet().exists("cats") -> False
    |
    v
Try suffix 'est': "cats" does not end with 'est'
Try suffix 'ing': "cats" does not end with 'ing'
Try suffix 'ed':  "cats" does not end with 'ed'
Try suffix 'es':  "cats" does not end with 'es'
Try suffix 's':   "cats" ends with 's' -> stem = "cat"
    Candidates: ["cat", "cate"]
    FindWordnet().exists("cat") -> True  ->  return ['s']
```

### Why runtime rather than pre-computed?

Inflectional endings form a closed set (a handful of suffixes vs. open-ended derivational morphology). The combinatorics are tractable at call time (~2-5 us per word). Pre-computing inflectional data would require storing stem mappings for every inflected form in the corpus, adding significant storage with marginal speed benefit.

---

## Combined Morphology (`morphology.py`)

### Morphology dataclass

```python
@dataclass(frozen=True)
class Morphology:
    derivational: list[str]   # from get_suffixes() - pre-computed
    inflectional: list[str]   # from get_inflections() - runtime
```

`frozen=True` makes instances hashable and immutable, allowing safe use as dict keys or in sets.

### Aggregation logic

```python
def get_morphology(word: str) -> Morphology | None:
    d = get_suffixes(word)       # None | [] | [...]
    i = get_inflections(word)    # None | [] | [...]

    if d is None and i is None:
        return None              # Not in WordNet by either path

    return Morphology(
        derivational=d or [],
        inflectional=i or [],
    )
```

`None` from either function means "not found by this method," not "not in WordNet." A word may be found by `get_suffixes()` but return `None` from `get_inflections()` if no inflectional suffix can be stripped to a valid stem; both results are still valid and combined.

### None vs [] contract (both fields)

The same `None` vs `[]` contract that applies to `get_suffixes()` individually applies to the combined result:

- `get_morphology()` returns `None` only when **both** checks fail
- Each field within `Morphology` is always a list (never `None`)
- An empty list in a field means "found, but no suffixes of this type"

### Interaction between derivational and inflectional

Derivational and inflectional suffixes are linguistically distinct layers. Derivational suffixes change word class or meaning (beautiful -> beautifully), while inflectional suffixes mark grammatical categories (cat -> cats). A word can carry both:

```
"nationalized" -> derivational: ['al', 'ize', 'ed']
```

Note: `-ed` in `nationalized` is derivational (participial adjective derivation), captured by `get_suffixes()`. In contrast, `walked` has inflectional `-ed` captured by `get_inflections()`. The pre-computed derivational data takes precedence in `get_suffixes()`.

---

## Design Decisions

### Why not Bloom filters?

Bloom filters are space-efficient probabilistic sets, but:
- `frozenset` is already fast enough (~50 ns)
- Zero false positives - Bloom filters have inherent false positive rate
- Simpler implementation - no bit manipulation or multiple hash functions

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
