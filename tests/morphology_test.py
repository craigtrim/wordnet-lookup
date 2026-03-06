"""500+ parametrized tests for wordnet_lookup.morphology (get_morphology).

get_morphology() returns:
  Morphology(derivational=[...], inflectional=[...])
    — when either get_suffixes() or get_inflections() can anchor the word
  None
    — when both are None (word has no WordNet anchor at all)

The inflectional field is [] for words directly in WordNet (including most
common inflected forms like 'running', 'walked', 'cats' that WN contains).
Inflectional is non-empty only for forms NOT in WN whose stem is recoverable.
"""
import pytest

from wordnet_lookup import Morphology, get_morphology


# fmt: off
def _morph_variants(word: str, d: list, i: list) -> list[tuple]:
    expected = Morphology(derivational=d, inflectional=i)
    return [
        (word,               expected),
        (word.upper(),       expected),
        (word.capitalize(),  expected),
        (f' {word} ',        expected),
        (f'\t{word}\t',      expected),
        (f'  {word}  ',      expected),
    ]


# ------------------------------------------------------------------ #
# Words with derivational suffixes, inflectional=[]                  #
# ------------------------------------------------------------------ #

_DERIV_CASES: list[tuple[str, list]] = [
    ('happiness',        ['ness']),
    ('sadness',          ['ness']),
    ('goodness',         ['ness']),
    ('madness',          ['ness']),
    ('darkness',         ['ness']),
    ('kindness',         ['ness']),
    ('fitness',          ['ness']),
    ('brightness',       ['ness']),
    ('hardness',         ['ness']),
    ('weakness',         ['ness']),
    ('softness',         ['ness']),
    ('quickness',        ['ness']),
    ('boldness',         ['ness']),
    ('coldness',         ['ness']),
    ('loudness',         ['ness']),
    ('rudeness',         ['ness']),
    ('blindness',        ['ness']),
    ('calmness',         ['ness']),
    ('beautifully',      ['ful', 'ly']),
    ('carefully',        ['ful', 'ly']),
    ('quickly',          ['ly']),
    ('slowly',           ['ly']),
    ('sadly',            ['ly']),
    ('kindly',           ['ly']),
    ('beautiful',        ['ful']),
    ('careful',          ['ful']),
    ('helpful',          ['ful']),
    ('harmful',          ['ful']),
    ('painful',          ['ful']),
    ('graceful',         ['ful']),
    ('peaceful',         ['ful']),
    ('hopeful',          ['ful']),
    ('nationalize',      ['al', 'ize']),
    ('computerize',      ['er', 'ize']),
    ('modernize',        ['ize']),
    ('realize',          ['ize']),
    ('nationalized',     ['al', 'ize', 'ed']),
    ('computerized',     ['er', 'ize', 'ed']),
    ('modernized',       ['ize', 'ed']),
    ('realized',         ['ize', 'ed']),
    ('nationalization',  ['al', 'ize', 'ation']),
    ('computerization',  ['er', 'ize', 'ation']),
    ('modernization',    ['ize', 'ation']),
    ('realization',      ['ize', 'ation']),
    ('freedom',          ['dom']),
    ('boredom',          ['dom']),
    ('wisdom',           ['dom']),
    ('kingdom',          ['dom']),
    ('stardom',          ['dom']),
    ('running',          ['ing']),
    ('walking',          ['ing']),
    ('talking',          ['ing']),
    ('jumping',          ['ing']),
    ('hoping',           ['ing']),
    ('singing',          ['ing']),
    ('dancing',          ['ing']),
    ('reading',          ['ing']),
    ('writing',          ['ing']),
    ('childhood',        ['hood']),
    ('manhood',          ['hood']),
    ('brotherhood',      ['hood']),
    ('sisterhood',       ['hood']),
    ('parenthood',       ['hood']),
    ('neighborhood',     ['hood']),
    # past tense forms in sx/ buckets
    ('walked',           ['ed']),
    ('talked',           ['ed']),
    ('jumped',           ['ed']),
]

_DERIV_INPUTS = [
    (variant, Morphology(derivational=d, inflectional=[]))
    for (word, d) in _DERIV_CASES
    for (variant, _) in _morph_variants(word, d, [])
]


@pytest.mark.parametrize('word,expected', _DERIV_INPUTS)
def test_get_morphology_derivational(word, expected):
    assert get_morphology(word) == expected


# ------------------------------------------------------------------ #
# Words in WordNet with no suffixes: Morphology([], [])               #
# ------------------------------------------------------------------ #

_EMPTY_WORDS = [
    # base forms
    'cat', 'dog', 'run', 'walk', 'talk', 'jump', 'fast', 'happy', 'big',
    'funny', 'hope', 'like', 'stop', 'sit', 'plan', 'win', 'swim', 'hit',
    'put', 'cut', 'red', 'sad', 'mad', 'wet', 'hot', 'fat', 'thin', 'flat',
    'glad', 'slim', 'dim', 'tame', 'lame', 'sane', 'safe', 'bare', 'rare',
    'rude', 'vague', 'huge', 'pale', 'noble', 'fine', 'pure', 'cute', 'vile',
    # inflected forms directly in WordNet (no sx/ data, inflections=None→[])
    'cats', 'dogs', 'runs', 'walks',
    'fastest', 'longest', 'coldest', 'biggest',
]

_EMPTY_MORPH = Morphology(derivational=[], inflectional=[])

_EMPTY_INPUTS = [
    (variant, _EMPTY_MORPH)
    for word in _EMPTY_WORDS
    for variant in [word, word.upper(), word.capitalize(), f' {word} ', f'\t{word}\t', f'  {word}  ']
]


@pytest.mark.parametrize('word,expected', _EMPTY_INPUTS)
def test_get_morphology_empty(word, expected):
    assert get_morphology(word) == expected


# ------------------------------------------------------------------ #
# Words with non-empty inflectional: Morphology([], ['est'/'ing'/...]) #
# ------------------------------------------------------------------ #

_INFLECTIONAL_CASES: list[tuple[str, list]] = [
    ('funniest',  ['est']),
    ('hottest',   ['est']),
    ('saddest',   ['est']),
    ('maddest',   ['est']),
    ('wettest',   ['est']),
    ('reddest',   ['est']),
    ('fattest',   ['est']),
    ('thinnest',  ['est']),
    ('flattest',  ['est']),
    ('gladdest',  ['est']),
    ('slimmest',  ['est']),
    ('dimmest',   ['est']),
    ('grimest',   ['est']),
    ('trimmest',  ['est']),
    ('drabbest',  ['est']),
    ('snuggest',  ['est']),
    ('smuggest',  ['est']),
    ('lamest',    ['est']),
    ('sanest',    ['est']),
    ('rudest',    ['est']),
    ('vaguest',   ['est']),
    ('hugest',    ['est']),
    ('palest',    ['est']),
    ('stalest',   ['est']),
    ('vilest',    ['est']),
    ('cutest',    ['est']),
    ('barest',    ['est']),
    ('noblest',   ['est']),
    ('bussing',   ['ing']),
    ('jazzing',   ['ing']),
    ('hexing',    ['ing']),
    ('frizzing',  ['ing']),
    ('quizzing',  ['ing']),
    ('shrugging', ['ing']),
    ('tugging',   ['ing']),
    ('slugging',  ['ing']),
    ('chugging',  ['ing']),
    ('bugging',   ['ing']),
    ('snugging',  ['ing']),
    ('fugging',   ['ing']),
    ('jazzed',    ['ed']),
    ('jugged',    ['ed']),
    ('lugged',    ['ed']),
    ('fugged',    ['ed']),
    ('apexes',    ['es']),
    ('quizzes',   ['es']),
    ('buzzes',    ['es']),
    ('hexes',     ['es']),
    ('vexes',     ['es']),
    ('poxes',     ['es']),
    ('tuxes',     ['es']),
    ('minxes',    ['es']),
]

_INFLECTIONAL_INPUTS = [
    (variant, Morphology(derivational=[], inflectional=i))
    for (word, i) in _INFLECTIONAL_CASES
    for variant in [word, word.upper(), f' {word} ']
]


@pytest.mark.parametrize('word,expected', _INFLECTIONAL_INPUTS)
def test_get_morphology_inflectional(word, expected):
    assert get_morphology(word) == expected


# ------------------------------------------------------------------ #
# Not in WordNet at all -> None                                       #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize('word', [
    'xyz123', 'abc123', 'flurble', 'waddling22', 'zork', 'frobnicate',
    'snurble', 'glorp', 'blargh', 'qwerty123', 'well-known', "it's",
    '', '   ', '\t',
])
def test_get_morphology_none(word):
    assert get_morphology(word) is None


# ------------------------------------------------------------------ #
# Structural / type tests                                             #
# ------------------------------------------------------------------ #

def test_morphology_is_frozen():
    m = get_morphology('cat')
    with pytest.raises((AttributeError, TypeError)):
        m.derivational = ['x']  # type: ignore[misc]


def test_morphology_returns_morphology_type():
    assert isinstance(get_morphology('cat'), Morphology)
    assert isinstance(get_morphology('happiness'), Morphology)
    assert get_morphology('xyz123') is None


def test_morphology_derivational_is_list():
    m = get_morphology('happiness')
    assert isinstance(m.derivational, list)
    assert isinstance(m.inflectional, list)


def test_morphology_empty_lists_not_none():
    m = get_morphology('cat')
    assert m is not None
    assert m.derivational == []
    assert m.inflectional == []


def test_morphology_combined_access():
    m = get_morphology('beautifully')
    assert m.derivational == ['ful', 'ly']
    assert m.inflectional == []
    assert m.derivational + m.inflectional == ['ful', 'ly']


def test_morphology_equality():
    assert get_morphology('cat') == get_morphology('cat')
    assert get_morphology('happiness') == get_morphology('happiness')
    assert get_morphology('cat') != get_morphology('happiness')


def test_morphology_repr_contains_fields():
    m = get_morphology('happiness')
    r = repr(m)
    assert 'derivational' in r
    assert 'inflectional' in r
# fmt: on
