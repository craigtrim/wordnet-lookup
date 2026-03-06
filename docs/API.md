# API Documentation

## Table of Contents

- [Installation](#installation)
- [is_wordnet_term](#is_wordnet_term)
- [get_suffixes](#get_suffixes)
- [get_inflections](#get_inflections)
- [get_morphology](#get_morphology)
- [Performance](#performance)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Development](#development)

## Installation

```bash
pip install wordnet-lookup
```

---

## is_wordnet_term

```python
from wordnet_lookup import is_wordnet_term

is_wordnet_term(word: str) -> bool
```

Returns `True` if `word` (or a normalized form of it) exists in the WordNet corpus.

### Normalization applied

1. Lowercase + strip whitespace
2. Unicode NFKD normalization (e.g. `naïve` -> `naive`)
3. Trailing-s plural stripping (e.g. `computers` -> `computer`), only for words longer than 3 characters

### Examples

```python
is_wordnet_term('alpha')        # True
is_wordnet_term('waddling')     # True
is_wordnet_term('myxovirus')    # True
is_wordnet_term('nonexistent')  # False

# Case-insensitive, whitespace-tolerant
is_wordnet_term('ALPHA')        # True
is_wordnet_term(' alpha ')      # True

# Plurals handled automatically
is_wordnet_term('computers')    # True
is_wordnet_term('acetabulars')  # True

# Unicode normalization
is_wordnet_term('naïve')        # True
```

### Direct class usage

```python
from wordnet_lookup import FindWordnet

finder = FindWordnet()
finder.exists('waddling')   # True
```

### Batch usage

```python
words = ['alpha', 'beta', 'gamma', 'notaword']
valid = [w for w in words if is_wordnet_term(w)]
# ['alpha', 'beta', 'gamma']
```

---

## get_suffixes

```python
from wordnet_lookup import get_suffixes

get_suffixes(word: str) -> list[str] | None
```

Returns pre-computed derivational suffixes for a WordNet word in innermost-first order.

### Return values

| Return | Meaning |
|--------|---------|
| `['ful', 'ly']` | Word is in WordNet with derivational structure |
| `[]` | Word is in WordNet, morphologically simple (no derivational suffixes recorded) |
| `None` | Word is not in WordNet |

`None` vs `[]` is intentional and load-bearing. Callers can use `get_suffixes()` as a single combined existence + morphology check.

### Examples

```python
get_suffixes('happiness')       # ['ness']
get_suffixes('beautifully')     # ['ful', 'ly']
get_suffixes('nationalized')    # ['al', 'ize', 'ed']
get_suffixes('cat')             # []   - in WordNet, no derivational suffixes
get_suffixes('xyz123')          # None - not in WordNet
```

### Caller pattern

```python
suffixes = get_suffixes(word)

if suffixes is None:
    pass  # not a WordNet word - discard
elif suffixes == []:
    pass  # in WordNet, morphologically simple
else:
    pass  # in WordNet with derivational structure
```

---

## get_inflections

```python
from wordnet_lookup import get_inflections

get_inflections(word: str) -> list[str] | None
```

Returns inflectional suffixes for a word by detecting them at runtime against the closed set of English inflectional endings. The recovered stem is validated via WordNet existence.

Unlike `get_suffixes()`, this runs at call time (not pre-computed).

### Inflectional suffixes detected

| Suffix | Examples | Pattern |
|--------|----------|---------|
| `-s` | cats, walks | plural noun, 3rd-person singular verb |
| `-es` | boxes, matches | plural after sibilant |
| `-ing` | running, hoping | present participle / gerund |
| `-ed` | walked, hoped | past tense, past participle |
| `-est` | fastest, happiest | superlative adjective |

**Comparative `-er` is intentionally excluded.** Without part-of-speech data, it is indistinguishable from agentive `-er` (derivational), which is already handled by `get_suffixes()`.

### Allomorphic stem restoration

When a suffix is stripped, multiple candidate base forms are tried:

| Allomorph | Example | Restoration |
|-----------|---------|-------------|
| Direct | `walked` -> `walk` | stem as-is |
| E-restore | `hoped` -> `hope` | stem + `e` |
| Double-consonant reduction | `running` -> `run` | deduplicate final consonant |
| Y-restore | `happiest` -> `happy` | `i` -> `y` |

### Return values

| Return | Meaning |
|--------|---------|
| `['ing']` | Inflectional suffix detected, WordNet base form recovered |
| `[]` | Word is itself a WordNet base form (no inflection) |
| `None` | Word not in WordNet and no inflected base form found |

### Examples

```python
get_inflections('cats')         # ['s']
get_inflections('running')      # ['ing']
get_inflections('walked')       # ['ed']
get_inflections('fastest')      # ['est']
get_inflections('boxes')        # ['es']
get_inflections('cat')          # []   - base form
get_inflections('xyz123')       # None - not in WordNet
```

---

## get_morphology

```python
from wordnet_lookup import get_morphology, Morphology

get_morphology(word: str) -> Morphology | None
```

Returns a unified morphological analysis combining derivational (pre-computed, O(1)) and inflectional (runtime) suffix detection.

### Morphology dataclass

```python
@dataclass(frozen=True)
class Morphology:
    derivational: list[str]   # from get_suffixes()
    inflectional: list[str]   # from get_inflections()
```

Both fields are always lists (never `None`). `None` is returned only if the word cannot be anchored to any WordNet base form by either method.

### Return values

| Return | Meaning |
|--------|---------|
| `Morphology(derivational=['ful','ly'], inflectional=[])` | Derivational word, base form |
| `Morphology(derivational=[], inflectional=['s'])` | Simple word, inflected |
| `Morphology(derivational=[], inflectional=[])` | Simple word, base form |
| `None` | Not in WordNet by either check |

### Examples

```python
get_morphology('beautifully')
# Morphology(derivational=['ful', 'ly'], inflectional=[])

get_morphology('happiness')
# Morphology(derivational=['ness'], inflectional=[])

get_morphology('cats')
# Morphology(derivational=[], inflectional=['s'])

get_morphology('cat')
# Morphology(derivational=[], inflectional=[])

get_morphology('xyz123')
# None
```

### Flat suffix list

```python
m = get_morphology('cats')
m.derivational + m.inflectional   # ['s']
```

### When to use get_morphology vs get_suffixes + get_inflections separately

Use `get_morphology()` when you need both kinds of suffix data in one call. Use `get_suffixes()` alone when you only need derivational structure and want to avoid the runtime cost of inflectional detection.

---

## Performance

### Complexity

| Operation | Complexity | Typical Time |
|-----------|------------|--------------|
| `is_wordnet_term()` | O(1) warm | ~400 ns |
| `get_suffixes()` | O(1) warm | ~400 ns |
| `get_inflections()` | O(k) suffixes tried | ~2-5 us |
| `get_morphology()` | O(k) combined | ~2-5 us |
| First bucket load | O(n) entries | ~2 ms |

`get_inflections()` and `get_morphology()` are slower than `get_suffixes()` because they run WordNet lookups at call time rather than returning pre-computed data.

### Benchmark

```python
import time
from wordnet_lookup import is_wordnet_term

start = time.perf_counter()
result = is_wordnet_term('myxovirus')
elapsed = time.perf_counter() - start
print(f"Lookup time: {elapsed*1000:.6f}ms")  # Typically microseconds
```

### Memory

| Scenario | Approximate Memory |
|----------|--------------------|
| Cold start (no lookups) | ~0 MB |
| 1 bucket loaded | ~0.07 MB |
| All 256 hs/ buckets loaded | ~7 MB |
| All 256 sx/ buckets loaded | ~5 MB |

---

## How It Works

### Architecture

1. **Hash-Based Storage**: WordNet terms are stored as MD5 hash suffixes in 256 `frozenset` buckets (`hs/`)
2. **Suffix Data**: Derivational suffixes stored as pipe-delimited strings in 256 `dict` buckets (`sx/`)
3. **Inflectional Detection**: Runtime suffix stripping with allomorphic restoration against WordNet
4. **Bucket Routing**: First 2 hex characters of the MD5 hash determine the bucket (00-ff)
5. **Lazy Loading**: All modules imported on-demand and cached
6. **Plural Handling**: If a word is not found and ends with `s`, the singular form is checked
7. **Case Insensitive**: All inputs normalized to lowercase

For a detailed technical deep-dive, see [IMPLEMENTATION.md](IMPLEMENTATION.md).

---

## Project Structure

```
wordnet-lookup/
├── wordnet_lookup/
│   ├── __init__.py              # Public API exports
│   ├── find_wordnet.py          # Core hash existence lookup
│   ├── find_suffixes.py         # Derivational suffix lookup (polars, parquet)
│   ├── find_inflections.py      # Runtime inflectional suffix detection
│   ├── morphology.py            # Morphology dataclass + get_morphology()
│   ├── hs/                      # 256 frozenset hash buckets (existence)
│   │   ├── h_00.py
│   │   └── ...                  # Through h_ff.py
│   └── sx/                      # 256 dict hash buckets (suffix data)
│       ├── sx_00.py
│       └── ...                  # Through sx_ff.py
├── builder/
│   ├── build_hash_files.py      # Generates hs/ modules
│   └── wordnet_words.txt        # Source word list (88,013 words)
├── tests/
│   ├── find_inflections_test.py
│   ├── find_suffixes_test.py
│   ├── find_wordnet_test.py
│   ├── morphology_test.py
│   └── wordnet_lookup_test.py
├── docs/
│   ├── API.md                   # This file
│   └── IMPLEMENTATION.md        # Technical deep-dive
├── pyproject.toml
├── Makefile
└── README.md
```

---

## Development

### Setup

```bash
git clone https://github.com/craigtrim/wordnet-lookup.git
cd wordnet-lookup
make install
```

### Running Tests

```bash
make test      # Run pytest (4291 tests)
make all       # Full build pipeline
```

### Code Quality

- **Ruff**: Fast Python linter
- **Pre-commit**: Git hooks
- **Autopep8**: Code formatting
- **Pytest**: Testing framework

```bash
make linters
poetry run pre-commit run --all-files
```

---

## Requirements

- Python 3.7+
- No external dependencies for existence lookup
- `polars` required only for `get_suffixes()` (suffix parquet loading)

---

## License

Dual-licensed:

- **Software**: MIT License
- **WordNet Data**: Princeton WordNet License

> WordNet 3.0 Copyright 2006 by Princeton University. All rights reserved.
