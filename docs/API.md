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

## Direct Dictionary Access

Access specific alphabetically-organized dictionaries for advanced use cases:

```python
from wordnet_lookup.os import wordnet_terms_a, wordnet_terms_b

# Check directly in the 'a' dictionary
if 'alpha' in wordnet_terms_a:
    print("Found in A dictionary")

# Access multiple dictionaries
from wordnet_lookup.os import (
    wordnet_terms_a,
    wordnet_terms_b,
    wordnet_terms_c
)

# Batch check within specific letter range
words_to_check = ['alpha', 'beta', 'charlie']
results = {
    'alpha': 'alpha' in wordnet_terms_a,
    'beta': 'beta' in wordnet_terms_b,
    'charlie': 'charlie' in wordnet_terms_c
}
```

### Available Dictionaries

Each module exports a dictionary for its letter:

```python
# Import pattern: wordnet_terms_{letter}
from wordnet_lookup.os import (
    wordnet_terms_a,  # Words starting with 'a'
    wordnet_terms_b,  # Words starting with 'b'
    # ... through ...
    wordnet_terms_z   # Words starting with 'z'
)
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

1. **Alphabetical Organization**: WordNet terms are pre-compiled into 26 separate dictionaries (A-Z)
2. **First Character Routing**: Lookups route to the appropriate dictionary based on the first character
3. **Plural Handling**: If a word isn't found and ends with 's', the singular form is checked
4. **Case Insensitive**: All inputs are normalized to lowercase

### Lookup Flow

```python
# When you call: is_wordnet_term('Alpha')

1. Normalize: 'Alpha' -> 'alpha'
2. Get first char: 'a'
3. Route to: wordnet_terms_a
4. Check: 'alpha' in wordnet_terms_a
5. If not found and ends with 's':
   - Try singular: 'alph' in wordnet_terms_a
6. Return: True/False
```

### Data Source

The static dictionaries are pre-compiled from the Princeton WordNet corpus, containing all valid WordNet terms organized alphabetically for optimal lookup performance.

## Project Structure

```
wordnet-lookup/
├── wordnet_lookup/
│   ├── __init__.py           # Main API exports
│   ├── find_wordnet.py       # Core lookup logic
│   └── os/
│       ├── __init__.py       # Dictionary exports
│       ├── wordnet_a.py      # Terms starting with 'a'
│       ├── wordnet_b.py      # Terms starting with 'b'
│       └── ...               # Through 'z'
├── tests/
│   └── wordnet_lookup_test.py
├── docs/
│   └── API.md                # This file
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
