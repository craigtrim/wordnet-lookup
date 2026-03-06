"""Runtime inflectional suffix detection for WordNet words.

Unlike get_suffixes() (which uses pre-computed static files), inflectional
suffix detection runs at call time against the closed set of English
inflectional endings. The stem is validated via FindWordnet.exists().

Inflectional suffixes handled:
    -s   / -es  : plural noun, 3rd-person singular verb
    -ing         : present participle / gerund
    -ed          : past tense, past participle
    -est         : superlative adjective

Comparative -er is intentionally excluded: without POS data it is
indistinguishable from agentive -er (derivational), which is already
handled by get_suffixes().

Related GitHub Issue (morphroot):
    #13 - Add get_inflections() and get_morphology() API
    https://github.com/craigtrim/morphroot/issues/13
"""

from __future__ import annotations

_MIN_STEM = 2

# Inflectional suffixes to try, ordered longest-first so -est is tried
# before -s, -ing before -s, etc.
_INFLECTIONAL: list[str] = ['est', 'ing', 'ed', 'es', 's']

# Suffixes that trigger e-drop at the surface (hoping → hope, hoped → hope)
_E_DROP_TRIGGERS: frozenset[str] = frozenset({'ing', 'ed', 'er', 'est'})


def _candidates(stem: str, suffix: str) -> list[str]:
    """Return allomorphic candidate base forms for a stripped stem.

    Covers the three most common English inflectional allomorphs:
        1. Direct: walk  (walked → walk)
        2. E-restore: hope (hoped → hop + e)
        3. Double-consonant: run (running → runn → run)
        4. Y-restore: happy (happiest → happi → happy)
    """
    candidates: list[str] = []

    if len(stem) < _MIN_STEM:
        return candidates

    # 1. Direct
    candidates.append(stem)

    # 2. E-restore (e-drop triggers only)
    if suffix in _E_DROP_TRIGGERS:
        candidates.append(stem + 'e')

    # 3. Double-consonant reduction: "runn" → "run", "stopp" → "stop"
    if len(stem) >= 2 and stem[-1] == stem[-2]:
        candidates.append(stem[:-1])

    # 4. Y-restore: "happi" → "happy" (common in -est, -ed, -es)
    if stem.endswith('i'):
        candidates.append(stem[:-1] + 'y')

    return candidates


def get_inflections(word: str) -> list[str] | None:
    """Return the inflectional suffixes for a word derived from a WordNet base.

    Runs at call time (not pre-computed). Strips each candidate inflectional
    suffix, applies allomorphic restoration, and checks whether the resulting
    stem exists in WordNet.

    Args:
        word: Any English word. Case-insensitive.

    Returns:
        List of inflectional suffixes detected, e.g. ["s"], ["ing"], ["ed"].
        Empty list [] if the word is itself a WordNet base form (no inflection).
        None if no WordNet base form can be recovered (word not in WordNet
        and no valid inflected stem found).

    Examples:
        >>> get_inflections("cats")
        ['s']
        >>> get_inflections("running")
        ['ing']
        >>> get_inflections("walked")
        ['ed']
        >>> get_inflections("fastest")
        ['est']
        >>> get_inflections("cat")
        []
        >>> get_inflections("xyz123")
        None
    """
    from .find_wordnet import FindWordnet

    normalized = word.lower().strip()
    if not normalized:
        return None

    wn = FindWordnet()

    # Word is already a base form in WordNet — no inflectional ending.
    if wn.exists(normalized):
        return []

    for suffix in _INFLECTIONAL:
        if not normalized.endswith(suffix):
            continue
        stem = normalized[: -len(suffix)]
        for candidate in _candidates(stem, suffix):
            if wn.exists(candidate):
                return [suffix]

    return None
