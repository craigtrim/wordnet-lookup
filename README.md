# WordNet Lookup

[![PyPI version](https://badge.fury.io/py/wordnet-lookup.svg)](https://badge.fury.io/py/wordnet-lookup)
[![Downloads](https://pepy.tech/badge/wordnet-lookup)](https://pepy.tech/project/wordnet-lookup)
[![Downloads/Month](https://pepy.tech/badge/wordnet-lookup/month)](https://pepy.tech/project/wordnet-lookup)
[![Tests](https://img.shields.io/badge/tests-549-brightgreen)](https://github.com/craigtrim/wordnet-lookup/tree/master/tests)
[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Is this token a word? O(1) answer. No setup. No dependencies.**

A simple question deserves a simple answer. This library gives you instant yes/no validation against 88,000 common English words from the Princeton WordNet lexicon — plus morphological suffix extraction.

## Quick Start

```bash
pip install wordnet-lookup
```

```python
from wordnet_lookup import is_wordnet_term, get_suffixes

# Word existence — O(1), no I/O
is_wordnet_term('alpha')        # True
is_wordnet_term('waddling')     # True
is_wordnet_term('myxovirus')    # True
is_wordnet_term('nonexistent')  # False

# Case-insensitive, whitespace-tolerant
is_wordnet_term('ALPHA')        # True
is_wordnet_term(' alpha ')      # True

# Plurals handled automatically
is_wordnet_term('computers')    # True

# Morphological suffix extraction
get_suffixes('happiness')       # ['ness']
get_suffixes('beautifully')     # ['ful', 'ly']
get_suffixes('nationalized')    # ['al', 'ize', 'ed']
get_suffixes('cat')             # []   — in WordNet, no derivational suffixes
get_suffixes('xyz123')          # None — not in WordNet
```

## Features

- **Zero Dependencies** — Pure Python, no external packages
- **Zero I/O** — No filesystem access, no database queries
- **Zero Setup** — No corpus downloads or configuration
- **Microsecond Lookups** — O(1) hash-based access
- **Smart Plurals** — Automatically checks singular forms
- **Unicode Normalization** — Accented forms (e.g. `naïve`, `café`) resolved to ASCII
- **Suffix Extraction** — `get_suffixes()` returns derivational suffixes in order, or `None` if the word isn't in WordNet

## When to Use This

- **Tokenization filtering** — Keep real words, discard garbage
- **Input validation** — Reject nonsense in user input
- **NLP preprocessing** — Filter candidates before expensive operations
- **Morphological analysis** — Identify suffix chains for stemming pipelines
- **Data cleaning** — Identify malformed or corrupted text

## What This Doesn't Do

- No definitions, synonyms, or semantic relationships (use spaCy for that)
- No slang, proper nouns, or recent coinages (WordNet is from 2006)
- No spell-checking or suggestions (just yes/no)
- No hyphenated compounds or multi-word phrases

## Documentation

See [API Documentation](https://github.com/craigtrim/wordnet-lookup/blob/master/docs/API.md) and [Implementation Notes](https://github.com/craigtrim/wordnet-lookup/blob/master/docs/IMPLEMENTATION.md) for full details.

## Development

```bash
git clone https://github.com/craigtrim/wordnet-lookup.git
cd wordnet-lookup
make all      # Full build pipeline
```

## License

Dual-licensed: **MIT** (software) + **Princeton WordNet License** (data). See [LICENSE](https://github.com/craigtrim/wordnet-lookup/blob/master/LICENSE).

> WordNet 3.0 Copyright 2006 by Princeton University. All rights reserved.

## See Also

- **[bnc-lookup](https://github.com/craigtrim/bnc-lookup)** — O(1) lookup using the British National Corpus
- **[morphroot](https://github.com/craigtrim/morphroot)** — Suffix extraction pipeline that feeds this library

## Links

- **Repository**: [github.com/craigtrim/wordnet-lookup](https://github.com/craigtrim/wordnet-lookup)
- **PyPI**: [pypi.org/project/wordnet-lookup](https://pypi.org/project/wordnet-lookup)
- **WordNet**: [wordnet.princeton.edu](https://wordnet.princeton.edu)
