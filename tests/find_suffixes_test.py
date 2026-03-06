"""500+ parametrized tests for wordnet_lookup.find_suffixes (get_suffixes)."""
import pytest

from wordnet_lookup import get_suffixes


# fmt: off
def _suf_variants(word: str, expected: list) -> list[tuple]:
    return [
        (word,             expected),
        (word.upper(),     expected),
        (word.capitalize(), expected),
        (f' {word} ',      expected),
        (f'\t{word}\t',    expected),
        (f'  {word}  ',    expected),
    ]


# ------------------------------------------------------------------ #
# Words with derivational suffixes — grouped by suffix chain          #
# ------------------------------------------------------------------ #

_NESS = [
    'happiness', 'sadness', 'goodness', 'madness', 'darkness', 'kindness',
    'fitness', 'brightness', 'hardness', 'weakness', 'softness', 'quickness',
    'boldness', 'coldness', 'loudness', 'rudeness', 'blindness', 'calmness',
    'dampness', 'fierceness', 'fondness', 'fullness', 'harshness', 'illness',
    'keenness', 'laziness', 'likeness', 'loneliness', 'looseness', 'meanness',
]

_LY = [
    'quickly', 'slowly', 'sadly', 'kindly', 'boldly', 'coldly',
    'loudly', 'blindly',
]

_FUL_LY = [
    'beautifully', 'carefully', 'gracefully', 'peacefully', 'hopefully',
    'wastefully', 'painfully', 'cheerfully',
]

_FUL = [
    'beautiful', 'careful', 'cheerful', 'helpful', 'harmful', 'painful',
    'graceful', 'peaceful', 'hopeful', 'grateful', 'wasteful',
]

_IZE = [
    'nationalize', 'computerize', 'modernize', 'realize', 'legalize',
]

_AL_IZE = [
    'nationalize',
]

_IZE_ED = [
    'nationalized', 'computerized', 'modernized', 'realized', 'legalized',
]

_IZE_ATION = [
    'nationalization', 'computerization', 'modernization', 'realization',
]

_DOM = [
    'freedom', 'boredom', 'wisdom', 'kingdom', 'stardom',
]

_ING = [
    'running', 'walking', 'talking', 'jumping', 'hoping', 'liking',
    'stopping', 'singing', 'dancing', 'reading', 'writing', 'driving', 'flying',
]

_HOOD = [
    'childhood', 'manhood', 'falsehood', 'likelihood',
    'brotherhood', 'sisterhood', 'parenthood', 'neighborhood',
]

_SUFFIX_CASES: list[tuple[str, list]] = (
    [(w, ['ness'])       for w in _NESS]
    + [(w, ['ly'])       for w in _LY]
    + [(w, ['ful', 'ly']) for w in _FUL_LY]
    + [(w, ['ful'])      for w in _FUL]
    + [('nationalize',   ['al', 'ize'])]
    + [('computerize',   ['er', 'ize'])]
    + [('modernize',     ['ize'])]
    + [('realize',       ['ize'])]
    + [('legalize',      ['ize'])]
    + [('nationalized',  ['al', 'ize', 'ed'])]
    + [('computerized',  ['er', 'ize', 'ed'])]
    + [('modernized',    ['ize', 'ed'])]
    + [('realized',      ['ize', 'ed'])]
    + [('legalized',     ['ize', 'ed'])]
    + [('nationalization', ['al', 'ize', 'ation'])]
    + [('computerization', ['er', 'ize', 'ation'])]
    + [('modernization', ['ize', 'ation'])]
    + [('realization',   ['ize', 'ation'])]
    + [(w, ['dom'])      for w in _DOM]
    + [(w, ['ing'])      for w in _ING]
    + [(w, ['hood'])     for w in _HOOD]
)

_SUFFIX_INPUTS = [
    (variant, expected)
    for (word, expected) in _SUFFIX_CASES
    for (variant, _) in _suf_variants(word, expected)
]


@pytest.mark.parametrize('word,expected', _SUFFIX_INPUTS)
def test_get_suffixes_with_derivation(word, expected):
    assert get_suffixes(word) == expected


# ------------------------------------------------------------------ #
# Monomorphemic: in WordNet, no derivational suffixes -> []           #
# ------------------------------------------------------------------ #

_MONO = [
    'cat', 'dog', 'run', 'walk', 'talk', 'jump', 'fast', 'happy', 'big',
    'funny', 'hope', 'like', 'stop', 'sit', 'plan', 'win', 'swim', 'hit',
    'put', 'cut', 'air', 'arm', 'art', 'age', 'aid', 'aim', 'bed', 'bit',
    'bay', 'boy', 'bus', 'car', 'cup', 'day', 'ear', 'egg', 'end', 'eye',
    'fan', 'fat', 'fly', 'fog', 'gap', 'gas', 'hat', 'hay', 'hip', 'hub',
    'ice', 'ink', 'jaw', 'jet', 'joy', 'key', 'lab', 'law', 'leg', 'lip',
    'map', 'mob', 'mud', 'net', 'nut', 'oak', 'oil', 'ore', 'owl', 'pan',
    'paw', 'pea', 'pen', 'pie', 'pig', 'pin', 'pit', 'pod', 'pot', 'pub',
    'rag', 'ram', 'rat', 'raw', 'rib', 'rim', 'rod', 'rot', 'row', 'sap',
    'saw', 'sea', 'set', 'ski', 'sky', 'sob', 'son', 'spa', 'spy', 'sum',
    'sun', 'tan', 'tap', 'tar', 'tea', 'tin', 'tip', 'toe', 'ton', 'top',
]

_MONO_INPUTS = [
    (variant, [])
    for word in _MONO
    for variant in [word, word.upper(), f' {word} ']
]


@pytest.mark.parametrize('word,expected', _MONO_INPUTS)
def test_get_suffixes_monomorphemic(word, expected):
    assert get_suffixes(word) == expected


# ------------------------------------------------------------------ #
# Not in WordNet -> None                                              #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize('word', [
    'xyz123', 'abc123', 'flurble', 'waddling22', 'zork', 'frobnicate',
    'snurble', 'glorp', 'blargh', 'qwerty123', 'well-known', "it's",
    '', '   ', '\t',
])
def test_get_suffixes_none(word):
    assert get_suffixes(word) is None
# fmt: on
