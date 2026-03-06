"""500+ parametrized tests for wordnet_lookup.find_inflections (get_inflections).

Key behaviors:
- []   : word is directly in WordNet as-is (base form or inflected form that WN knows)
- ['s']  / ['es'] : word not in WN, stem found via -s / -es stripping
- ['ing']         : word not in WN, stem found via -ing + allomorphs
- ['ed']          : word not in WN, stem found via -ed + allomorphs
- ['est']         : word not in WN, stem found via -est + allomorphs
- None            : word not in WN, no inflected stem recoverable
"""
import pytest

from wordnet_lookup import get_inflections


# fmt: off
def _inf_variants(word: str, expected) -> list[tuple]:
    return [
        (word,               expected),
        (word.upper(),       expected),
        (word.capitalize(),  expected),
        (f' {word} ',        expected),
        (f'\t{word}\t',      expected),
        (f'  {word}  ',      expected),
    ]


# ------------------------------------------------------------------ #
# Base forms — in WordNet directly -> []                              #
# ------------------------------------------------------------------ #

_BASE_WORDS = [
    # common nouns / verbs / adjectives — all directly in WordNet
    'cat', 'dog', 'run', 'walk', 'talk', 'jump', 'fast', 'happy', 'big',
    'funny', 'hope', 'like', 'stop', 'sit', 'plan', 'win', 'swim', 'hit',
    'put', 'cut', 'red', 'sad', 'mad', 'wet', 'hot', 'fat', 'thin', 'flat',
    'glad', 'slim', 'dim', 'grim', 'trim', 'drab', 'snug', 'smug', 'tame',
    'lame', 'sane', 'safe', 'bare', 'rare', 'rude', 'vague', 'huge', 'pale',
    'noble', 'fine', 'pure', 'cute', 'vile',
]

_BASE_INPUTS = [
    (variant, [])
    for word in _BASE_WORDS
    for (variant, _) in _inf_variants(word, [])
]


@pytest.mark.parametrize('word,expected', _BASE_INPUTS)
def test_get_inflections_base_forms(word, expected):
    assert get_inflections(word) == expected


# ------------------------------------------------------------------ #
# Inflected forms that ARE in WordNet directly -> []                  #
# ------------------------------------------------------------------ #

_IN_WN_INFLECTED = [
    # These look inflected but WordNet contains them directly
    'cats', 'dogs', 'runs', 'walks', 'talks', 'jumps',
    'running', 'walking', 'talking', 'jumping', 'hoping', 'liking',
    'walked', 'talked', 'jumped', 'hoped', 'liked', 'stopped',
    'fastest', 'biggest', 'longest', 'shortest', 'coldest',
    'boxes', 'matches', 'classes', 'buses', 'dishes', 'fixes',
    'mugging', 'drugging', 'plugging', 'hugging',
    'bussed', 'quizzed', 'hexed', 'vexed', 'shrugged',
    'tugged', 'slugged', 'chugged', 'bugged', 'drugged', 'plugged', 'mugged',
]

_IN_WN_INFLECTED_INPUTS = [
    (variant, [])
    for word in _IN_WN_INFLECTED
    for variant in [word, word.upper(), f' {word} ']
]


@pytest.mark.parametrize('word,expected', _IN_WN_INFLECTED_INPUTS)
def test_get_inflections_wn_inflected_forms(word, expected):
    assert get_inflections(word) == expected


# ------------------------------------------------------------------ #
# -est: not in WN, stem recoverable via allomorph -> ['est']          #
# ------------------------------------------------------------------ #

_EST_WORDS = [
    # e-drop: stem + 'e' in WN
    'lamest', 'sanest', 'rudest', 'vaguest', 'hugest', 'palest',
    'stalest', 'vilest', 'cutest', 'barest', 'noblest',
    # double-consonant reduction: e.g. saddest -> sad
    'funniest', 'hottest', 'saddest', 'maddest', 'wettest', 'reddest',
    'fattest', 'thinnest', 'flattest', 'gladdest', 'slimmest',
    'dimmest', 'grimest', 'trimmest', 'drabbest', 'snuggest', 'smuggest',
]

_EST_INPUTS = [
    (variant, ['est'])
    for word in _EST_WORDS
    for (variant, _) in _inf_variants(word, ['est'])
]


@pytest.mark.parametrize('word,expected', _EST_INPUTS)
def test_get_inflections_est(word, expected):
    assert get_inflections(word) == expected


# ------------------------------------------------------------------ #
# -ing: not in WN, stem recoverable -> ['ing']                        #
# ------------------------------------------------------------------ #

_ING_WORDS = [
    # double-consonant reduction: running -> run, buzzing -> buzz
    'bussing', 'jazzing', 'hexing', 'frizzing', 'quizzing',
    'shrugging', 'tugging', 'slugging', 'chugging', 'bugging',
    'snugging', 'fugging',
]

_ING_INPUTS = [
    (variant, ['ing'])
    for word in _ING_WORDS
    for (variant, _) in _inf_variants(word, ['ing'])
]


@pytest.mark.parametrize('word,expected', _ING_INPUTS)
def test_get_inflections_ing(word, expected):
    assert get_inflections(word) == expected


# ------------------------------------------------------------------ #
# -ed: not in WN, stem recoverable -> ['ed']                          #
# ------------------------------------------------------------------ #

_ED_WORDS = ['jazzed', 'jugged', 'lugged', 'fugged']

_ED_INPUTS = [
    (variant, ['ed'])
    for word in _ED_WORDS
    for (variant, _) in _inf_variants(word, ['ed'])
]


@pytest.mark.parametrize('word,expected', _ED_INPUTS)
def test_get_inflections_ed(word, expected):
    assert get_inflections(word) == expected


# ------------------------------------------------------------------ #
# -es: not in WN, stem recoverable -> ['es']                          #
# ------------------------------------------------------------------ #

_ES_WORDS = ['apexes', 'quizzes', 'buzzes', 'hexes', 'vexes', 'poxes', 'tuxes', 'minxes']

_ES_INPUTS = [
    (variant, ['es'])
    for word in _ES_WORDS
    for (variant, _) in _inf_variants(word, ['es'])
]


@pytest.mark.parametrize('word,expected', _ES_INPUTS)
def test_get_inflections_es(word, expected):
    assert get_inflections(word) == expected


# ------------------------------------------------------------------ #
# Not in WordNet + no recoverable stem -> None                        #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize('word', [
    # pure nonsense
    'xyz123', 'abc123', 'flurble', 'waddling22', 'zork', 'frobnicate',
    'snurble', 'glorp', 'blargh', 'qwerty123',
    # hyphens / apostrophes
    'well-known', "it's", "don't",
    # empty / whitespace
    '', '   ', '\t',
])
def test_get_inflections_none(word):
    assert get_inflections(word) is None
# fmt: on
