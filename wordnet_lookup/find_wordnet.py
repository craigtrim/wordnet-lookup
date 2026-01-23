# !/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Facade to find Wordnet Data on Disk """

import hashlib
import importlib

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
    """ Facade to find Wordnet Data on Disk """

    def __init__(self):
        """
        Created:
            5-Oct-2021
            craigtrim@gmail.com
            *   https://github.com/grafflr/graffl-core/issues/2
        Updated:
            31-Aug-2022
            craigtrim@gmail.com
            *   migrate to solo repo
        """
        pass

    def exists(self, input_text: str) -> bool:
        input_text = input_text.lower().strip()

        if _hash_exists(input_text):
            return True

        if input_text.endswith('s') and len(input_text) > 3:
            if _hash_exists(input_text[:-1]):
                return True

        return False
