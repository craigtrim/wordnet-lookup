# API Documentation

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Direct Dictionary Access](#direct-dictionary-access)
- [Performance](#performance)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Development](#development)

## Installation

```bash
pip install wordnet-lookup
```

## Basic Usage

The main interface is the `is_wordnet_term()` function:

```python
from wordnet_lookup import is_wordnet_term

# Check if a word exists in WordNet
is_wordnet_term('alpha')        # True
is_wordnet_term('waddling')     # True
is_wordnet_term('myxovirus')    # True
is_wordnet_term('nonexistent')  # False

# Validate words
if is_wordnet_term('according'):
    print("Valid WordNet term")

# Works with various forms
is_wordnet_term('acetabulars')  # Handles plurals automatically
```

## Advanced Usage

For more control, you can use the `FindWordnet` class directly:

```python
from wordnet_lookup import FindWordnet

finder = FindWordnet()
exists = finder.exists('waddling')
```

### Batch Validation

```python
from wordnet_lookup import is_wordnet_term

words = ['alpha', 'beta', 'gamma', 'notaword']
valid_words = [word for word in words if is_wordnet_term(word)]
print(valid_words)  # ['alpha', 'beta', 'gamma']
```

### Case Handling

All lookups are case-insensitive:

```python
is_wordnet_term('ALPHA')   # True
is_wordnet_term('Alpha')   # True
is_wordnet_term('alpha')   # True
```

### Plural Detection

The library automatically handles common plural forms:

```python
# If 'acetabulars' isn't found directly, checks 'acetabular'
is_wordnet_term('acetabulars')  # True

# Works for most regular plurals
is_wordnet_term('computers')    # True
is_wordnet_term('databases')    # True
```

## Performance

The library is optimized for speed with zero I/O overhead. All lookups are performed against pre-compiled dictionaries:

### Benchmark Example

```python
import time
from wordnet_lookup import is_wordnet_term

# Single lookup benchmark
start = time.perf_counter()
result = is_wordnet_term('myxovirus')
elapsed = time.perf_counter() - start
print(f"Lookup time: {elapsed*1000:.6f}ms")  # Typically microseconds

# Batch lookup benchmark
words = ['alpha', 'beta', 'gamma', 'delta', 'epsilon']
start = time.perf_counter()
results = [is_wordnet_term(word) for word in words]
elapsed = time.perf_counter() - start
print(f"Batch lookup time: {elapsed*1000:.6f}ms for {len(words)} words")
```

### Performance Characteristics

- **Lookup Complexity**: O(1) - Direct dictionary access
- **Memory**: All dictionaries loaded at import (one-time cost)
- **I/O Operations**: Zero - No file system or database access
- **Typical Latency**: Microseconds per lookup

### Comparison with Traditional WordNet

Traditional WordNet interfaces require:
- Database connections or file I/O
- NLTK corpus downloads
- Multiple filesystem lookups
- Synset traversal overhead

`wordnet-lookup` eliminates all of these by using pre-compiled static dictionaries.

## How It Works

### Architecture

1. **Hash-Based Storage**: WordNet terms are stored as MD5 hash suffixes in 256 `frozenset` buckets
2. **Bucket Routing**: The first 2 hex characters of the hash determine the bucket (00-ff)
3. **Lazy Loading**: Hash modules are imported on-demand and cached
4. **Plural Handling**: If a word isn't found and ends with 's', the singular form is checked
5. **Case Insensitive**: All inputs are normalized to lowercase

### Lookup Flow

```python
# When you call: is_wordnet_term('Alpha')

1. Normalize: 'Alpha' -> 'alpha'
2. Hash: MD5('alpha') -> 'e9c...2d1'
3. Split: prefix='e9', suffix='c...2d1'
4. Load bucket: import h_e9.py (if not cached)
5. Check: suffix in hashes_e9  # O(1) frozenset lookup
6. If not found and ends with 's':
   - Repeat for singular form
7. Return: True/False
```

### Data Source

The hash files are pre-compiled from the Princeton WordNet corpus (88,013 unique terms).

For detailed implementation notes, see [IMPLEMENTATION.md](IMPLEMENTATION.md).

## Project Structure

```
wordnet-lookup/
├── wordnet_lookup/
│   ├── __init__.py           # Main API exports
│   ├── find_wordnet.py       # Core lookup logic
│   └── hs/
│       ├── __init__.py       # Hash module exports
│       ├── h_00.py           # Hashes with prefix '00'
│       ├── h_01.py           # Hashes with prefix '01'
│       └── ...               # Through 'ff' (256 files)
├── builder/
│   ├── build_hash_files.py   # Generates hash files
│   └── wordnet_words.txt     # Source word list
├── tests/
│   └── wordnet_lookup_test.py
├── docs/
│   ├── API.md                # This file
│   └── IMPLEMENTATION.md     # Technical deep-dive
├── pyproject.toml            # Poetry configuration
├── Makefile                  # Build commands
└── README.md                 # Quick start guide
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/craigtrim/wordnet-lookup.git
cd wordnet-lookup

# Install dependencies
make install
```

### Running Tests

```bash
# Run tests
make test

# Run full build (install, test, lint, build)
make all
```

### Code Quality

The project uses modern Python tooling:

- **Ruff**: Fast Python linter
- **Pre-commit**: Git hooks for code quality
- **Autopep8**: Code formatting
- **Pytest**: Testing framework

```bash
# Run linters
make linters

# Run pre-commit hooks
poetry run pre-commit run --all-files
```

### Makefile Targets

```bash
make install   # Install dependencies
make test      # Run pytest
make linters   # Run ruff and autopep8
make build     # Build distribution
make publish   # Publish to PyPI
make all       # Full build pipeline
```

## Requirements

- Python 3.7+
- No external dependencies

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `make test`
2. Code passes linting: `make linters`
3. Pre-commit hooks are satisfied

## License

This package is dual-licensed:
- **Software**: MIT License
- **WordNet Data**: Princeton WordNet License

See [LICENSE](../LICENSE) for complete terms.

### Attribution

This package contains data derived from Princeton WordNet:

> WordNet 3.0 Copyright 2006 by Princeton University. All rights reserved.

For more information about WordNet, visit [wordnet.princeton.edu](https://wordnet.princeton.edu)
