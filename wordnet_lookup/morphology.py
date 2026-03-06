"""Combined morphological analysis: derivational + inflectional suffixes.

Provides the Morphology dataclass and get_morphology(), which unifies
get_suffixes() (pre-computed derivational, O(1) static lookup) with
get_inflections() (runtime inflectional check against the closed set of
English inflectional endings).

Related GitHub Issue (morphroot):
    #13 - Add get_inflections() and get_morphology() API
    https://github.com/craigtrim/morphroot/issues/13
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Morphology:
    """Structured morphological analysis of a word.

    Attributes:
        derivational: Derivational suffixes in innermost-first order,
            e.g. ["ful", "ly"] for "beautifully". Empty list if the word
            is in WordNet but has no derivational suffixes.
        inflectional: Inflectional suffixes detected at runtime,
            e.g. ["s"] for "cats", ["ing"] for "running". Empty list if
            the word is a base form with no inflectional ending.

    Examples:
        >>> m = get_morphology("beautifully")
        >>> m.derivational
        ['ful', 'ly']
        >>> m.inflectional
        []

        >>> m = get_morphology("cats")
        >>> m.derivational
        []
        >>> m.inflectional
        ['s']

        >>> m.derivational + m.inflectional  # flat list if needed
        ['s']
    """

    derivational: list[str]
    inflectional: list[str]


def get_morphology(word: str) -> Morphology | None:
    """Return the full morphological suffix analysis for a word.

    Combines derivational suffix lookup (pre-computed, O(1)) with
    runtime inflectional suffix detection. Returns None only when the
    word cannot be anchored to any WordNet base form by either method.

    Args:
        word: Any English word. Case-insensitive.

    Returns:
        Morphology dataclass with .derivational and .inflectional lists,
        or None if the word is not in WordNet and no inflected base form
        can be found.

    Examples:
        >>> get_morphology("beautifully")
        Morphology(derivational=['ful', 'ly'], inflectional=[])
        >>> get_morphology("happiness")
        Morphology(derivational=['ness'], inflectional=[])
        >>> get_morphology("cats")
        Morphology(derivational=[], inflectional=['s'])
        >>> get_morphology("cat")
        Morphology(derivational=[], inflectional=[])
        >>> get_morphology("xyz123")
        None
    """
    from .find_suffixes import get_suffixes
    from .find_inflections import get_inflections

    d = get_suffixes(word)
    i = get_inflections(word)

    if d is None and i is None:
        return None

    return Morphology(
        derivational=d or [],
        inflectional=i or [],
    )
