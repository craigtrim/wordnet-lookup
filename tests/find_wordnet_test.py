"""500+ parametrized tests for wordnet_lookup.find_wordnet (is_wordnet_term)."""
import pytest

from wordnet_lookup import is_wordnet_term


# fmt: off
def _wn_variants(word: str) -> list[str]:
    return [
        word,
        word.upper(),
        word.capitalize(),
        word[0].upper() + word[1:].upper(),
        f' {word}',
        f'{word} ',
        f' {word} ',
        f'\t{word}',
        f'{word}\t',
        f'\t{word}\t',
        f'  {word}  ',
    ]


_TRUE_WORDS = [
    # common nouns
    'computer', 'language', 'mountain', 'knowledge', 'animal', 'planet',
    'science', 'history', 'theory', 'system', 'method', 'result', 'number',
    'problem', 'question', 'answer', 'student', 'teacher', 'doctor', 'mother',
    'father', 'brother', 'sister', 'morning', 'evening', 'winter', 'summer',
    'garden', 'window', 'bottle', 'forest', 'river', 'ocean', 'island',
    'desert', 'valley', 'bridge', 'castle', 'temple', 'market', 'library',
    'kitchen', 'bedroom', 'ceiling', 'carpet', 'pillow', 'blanket', 'mirror',
    # adjectives
    'beautiful', 'freedom', 'running', 'national', 'natural', 'process',
    'ancient', 'modern', 'serious', 'curious', 'obvious', 'nervous', 'famous',
    'gentle', 'simple', 'complex', 'narrow', 'hollow', 'tender', 'bitter',
    'silent', 'fragile', 'humble', 'sturdy', 'vivid', 'cloudy', 'rainy',
    # verbs and derivations
    'quickly', 'happiness', 'darkness', 'knowledge', 'freedom', 'walking',
    'running', 'talking', 'sleeping', 'playing', 'reading', 'writing',
    'singing', 'dancing', 'driving', 'cooking', 'eating', 'drinking',
    # rare / technical
    'alpha', 'myxovirus', 'according', 'waddling',
]

_TRUE_INPUTS = [v for w in _TRUE_WORDS for v in _wn_variants(w)]


@pytest.mark.parametrize('word', _TRUE_INPUTS)
def test_is_wordnet_term_true(word):
    assert is_wordnet_term(word)


@pytest.mark.parametrize('word', [
    # pure numbers
    '0', '1', '123', '456', '789', '0000', '99999', '1234567890',
    # alphanumeric
    'abc123', 'word1', 'test99', 'item42', 'node7', 'val0', 'key1',
    # gibberish
    'xyzzy', 'flurble', 'zzzzzz', 'qqqqq', 'blargh', 'glorp',
    'snurble', 'wazzle', 'frumble', 'snibbet', 'blorf', 'grumf',
    'qxyzzy', 'waddling22', 'alpha99', 'zork', 'frobnicate',
    # hyphens (none in the corpus)
    'well-known', 'mother-in-law', 'self-aware', 'up-to-date',
    'long-term', 'short-term', 'first-class', 'state-of-the-art',
    'twenty-one', 'full-time', 'high-end', 'low-key',
    # apostrophes (none in the corpus)
    "it's", "don't", "can't", "won't", "they're", "i've", "you'd",
    # punctuation / symbols
    'hello!', 'world?', 'foo.bar', 'a@b', 'x#y', 'z$z', 'a&b',
    # empty / whitespace-only (all falsy)
    '', '   ', '\t', '\n', '\r\n',
])
def test_is_wordnet_term_false(word):
    assert not is_wordnet_term(word)


@pytest.mark.parametrize('word,expected', [
    # unicode normalization
    ('phaéton', True),
    ('protégé', True),
    ('outré', True),
    ('naïve', True),
    ('café', True),
    ('résumé', True),
    ('façade', True),
    ('PHAÉTON', True),
    ('NAÏVE', True),
    (' naïve ', True),
    # plural stripping
    ('acetabulars', True),
    ('computers', True),
    ('mountains', True),
    ('dogs', True),
    ('cats', True),
    ('books', True),
    # short words (len <= 3: plural strip does NOT apply)
    ('xys', False),
    ('zzs', False),
])
def test_is_wordnet_term_special_cases(word, expected):
    assert is_wordnet_term(word) is expected
# fmt: on
