# !/usr/bin/env python
# -*- coding: UTF-8 -*-
""" O(1) WordNet term validation via hash-based lookup """

import hashlib
import importlib
import unicodedata

_cache = {}


def _get_hash_set(prefix: str) -> frozenset:
    if prefix not in _cache:
        module = importlib.import_module(f'wordnet_lookup.hs.h_{prefix}')
        _cache[prefix] = getattr(module, f'hashes_{prefix}')
    return _cache[prefix]


def _calculate_md5(input_text: str) -> str:
    return hashlib.md5(input_text.lower().strip().encode()).hexdigest()


def _hash_exists(input_text: str) -> bool:
    if not input_text:
        return False
    h = _calculate_md5(input_text)
    prefix, suffix = h[:2], h[2:]
    return suffix in _get_hash_set(prefix)


class FindWordnet:
    """
    O(1) WordNet term lookup using hash-based frozenset buckets.

    Uses MD5 hashing with lazy-loaded modules for fast membership testing
    against 88,013 WordNet terms.
    """

    def exists(self, input_text: str) -> bool:
        input_text = input_text.lower().strip()

        if _hash_exists(input_text):
            return True

        # Normalize unicode accents to ASCII (e.g., phaéton -> phaeton)
        normalized = unicodedata.normalize('NFKD', input_text).encode(
            'ascii', 'ignore').decode('ascii')
        if normalized != input_text and _hash_exists(normalized):
            return True

        # Check plural (on normalized form)
        if normalized.endswith('s') and len(normalized) > 3:
            if _hash_exists(normalized[:-1]):
                return True

        return False
