# WordNet Lookup

[![PyPI version](https://badge.fury.io/py/wordnet-lookup.svg)](https://badge.fury.io/py/wordnet-lookup)
[![Downloads](https://pepy.tech/badge/wordnet-lookup)](https://pepy.tech/project/wordnet-lookup)
[![Downloads/Month](https://pepy.tech/badge/wordnet-lookup/month)](https://pepy.tech/project/wordnet-lookup)
[![Tests](https://img.shields.io/badge/tests-3-brightgreen)](https://github.com/craigtrim/wordnet-lookup/tree/master/tests)
[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Is this token a word? O(1) answer. No setup. No dependencies.**

A simple question deserves a simple answer. This library gives you instant yes/no validation against 88,000 common English words from the Princeton WordNet lexicon.

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

## The Problem This Solves

In NLP, you frequently need to answer the question: **"Is this token a real word?"**

Not "what does it mean?" Not "give me synonyms." Just: is this a word?

<table>
<tr>
<td align="center"><code>is_wordnet_term('computer')</code></td>
<td align="center"><code>is_wordnet_term('asdfgh')</code></td>
</tr>
<tr>
<td align="center"><img src="https://raw.githubusercontent.com/craigtrim/wordnet-lookup/master/docs/images/yes-hot-dog.png" width="180"></td>
<td align="center"><img src="https://raw.githubusercontent.com/craigtrim/wordnet-lookup/master/docs/images/not-hot-dog.png" width="180"></td>
</tr>
<tr>
<td align="center"><code>True</code></td>
<td align="center"><code>False</code></td>
</tr>
</table>

That's it. O(1) response. No ambiguity.

## Why WordNet?

WordNet isn't the OED (too academic). It's not Urban Dictionary (too ephemeral). It's not a web scrape (too noisy).

It's a **curated lexicon of ~88,000 common English words** maintained by Princeton linguists. The kind of words that appear in newspapers, textbooks, and everyday conversation. If a token passes the WordNet test, you can be confident it's a legitimate, widely-recognized English word.

## When to Use This

- **Tokenization filtering**: Keep real words, discard garbage
- **Input validation**: Reject nonsense in user input
- **NLP preprocessing**: Filter candidates before expensive operations
- **Spell-check pre-filtering**: Quick reject obvious non-words before fuzzy matching
- **Data cleaning**: Identify malformed or corrupted text

## What This Doesn't Do

- No definitions, synonyms, or semantic relationships (use spaCy for that)
- No slang, proper nouns, or recent coinages (WordNet is from 2006)
- No spell-checking or suggestions (just yes/no)

## Documentation

For detailed usage, performance benchmarks, implementation details, and advanced features, see the [API Documentation](https://github.com/craigtrim/wordnet-lookup/blob/master/docs/API.md).

## Development

```bash
git clone https://github.com/craigtrim/wordnet-lookup.git
cd wordnet-lookup
make all      # Full build pipeline
```

See [API Documentation](https://github.com/craigtrim/wordnet-lookup/blob/master/docs/API.md) for detailed development information.

## License

This package is dual-licensed:
- **Software**: MIT License
- **WordNet Data**: Princeton WordNet License

See [LICENSE](https://github.com/craigtrim/wordnet-lookup/blob/master/LICENSE) for complete terms.

## Attribution

This package contains data derived from Princeton WordNet 3.0 (2006):

> WordNet 3.0 Copyright 2006 by Princeton University. All rights reserved.

**Note:** This is a static snapshot of WordNet 3.0. The data is not automatically updated with newer WordNet releases.

## See Also

- **[bnc-lookup](https://github.com/craigtrim/bnc-lookup)** - Similar O(1) lookup using the British National Corpus (BNC)

## Links

- **Repository**: [github.com/craigtrim/wordnet-lookup](https://github.com/craigtrim/wordnet-lookup)
- **PyPI**: [pypi.org/project/wordnet-lookup](https://pypi.org/project/wordnet-lookup)
- **WordNet**: [wordnet.princeton.edu](https://wordnet.princeton.edu)
- **Author**: Craig Trim ([craigtrim@gmail.com](mailto:craigtrim@gmail.com))
