# WordNet Lookup

[![PyPI version](https://img.shields.io/pypi/v/wordnet-lookup.svg)](https://pypi.org/project/wordnet-lookup/)
[![PyPI downloads](https://img.shields.io/pypi/dm/wordnet-lookup.svg)](https://pypi.org/project/wordnet-lookup/)
[![Python versions](https://img.shields.io/pypi/pyversions/wordnet-lookup.svg)](https://pypi.org/project/wordnet-lookup/)
[![License](https://img.shields.io/badge/License-MIT%20%2B%20WordNet-yellow.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/craigtrim/wordnet-lookup)

**WordNet lookups in microseconds. No database. No downloads. No complexity.**

Stop waiting for database queries or corpus downloads. `wordnet-lookup` gives you instant WordNet term validation using pre-compiled static dictionaries. One import, one function call, zero hassle.

## Why This Exists

Traditional WordNet interfaces (NLTK, WordNet database) require corpus downloads, database connections, and I/O operations. For simple term validation, that's overkill. This library eliminates all of that by embedding WordNet terms directly in Python dictionaries. The result? Lookups in microseconds with zero external dependencies.

## Quick Start

```bash
pip install wordnet-lookup
```

```python
from wordnet_lookup import is_wordnet_term

# That's it. Start validating.
is_wordnet_term('alpha')        # True
is_wordnet_term('waddling')     # True
is_wordnet_term('myxovirus')    # True
is_wordnet_term('nonexistent')  # False

# Handles plurals automatically
is_wordnet_term('computers')    # True

# Case insensitive
is_wordnet_term('ALPHA')        # True
```

## Features

- **Zero Dependencies** - Pure Python, no external packages
- **Zero I/O** - No filesystem access, no database queries
- **Zero Setup** - No corpus downloads or configuration
- **Microsecond Lookups** - O(1) dictionary access
- **Smart Plurals** - Automatically checks singular forms
- **Simple API** - One function does it all

## What This Library Does (and Doesn't Do)

**Does:**
- Validates whether a term exists in WordNet 3.0
- Handles basic plural forms automatically
- Works offline with zero external dependencies

**Doesn't:**
- Provide definitions, synonyms, or semantic relationships (use NLTK for that)
- Include very recent terms, slang, or proper nouns (WordNet 3.0 is from 2006)
- Update automatically with new WordNet versions (static snapshot)
- Perform spell-checking or suggestions

**Use this when:** You need fast term validation for NLP preprocessing, filtering, or validation.

**Don't use this when:** You need definitions, synsets, semantic networks, or comprehensive spell-checking.

## Documentation

For detailed usage, performance benchmarks, and advanced features, see the [API Documentation](docs/API.md).

## How It Works

WordNet terms are stored as MD5 hash suffixes in 256 `frozenset` buckets (by first two hex characters of the hash). Lookups hash the input, route to the correct bucket, and perform O(1) set membership. Modules are lazy-loaded on first access per bucket.

For the gory details, see [Implementation Notes](docs/IMPLEMENTATION.md).

## Development

```bash
git clone https://github.com/craigtrim/wordnet-lookup.git
cd wordnet-lookup
make install  # Install dependencies
make test     # Run tests
make all      # Full build pipeline
```

See [API Documentation](docs/API.md) for detailed development information.

## License

This package is dual-licensed:
- **Software**: MIT License
- **WordNet Data**: Princeton WordNet License

See [LICENSE](LICENSE) for complete terms.

## Attribution

This package contains data derived from Princeton WordNet 3.0 (2006):

> WordNet 3.0 Copyright 2006 by Princeton University. All rights reserved.

**Note:** This is a static snapshot of WordNet 3.0. The data is not automatically updated with newer WordNet releases.

## Links

- **Repository**: [github.com/craigtrim/wordnet-lookup](https://github.com/craigtrim/wordnet-lookup)
- **PyPI**: [pypi.org/project/wordnet-lookup](https://pypi.org/project/wordnet-lookup)
- **WordNet**: [wordnet.princeton.edu](https://wordnet.princeton.edu)
- **Author**: Craig Trim ([craigtrim@gmail.com](mailto:craigtrim@gmail.com))
