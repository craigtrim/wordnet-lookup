import pytest

from wordnet_lookup import get_suffixes, is_wordnet_term


def test_lookup():
    assert is_wordnet_term('alpha')


def test_exists():
    assert is_wordnet_term('waddling')
    assert not is_wordnet_term('waddling22')
    assert is_wordnet_term('myxovirus')
    assert is_wordnet_term('according')
    assert is_wordnet_term('acetabulars')


def test_unicode_normalization():
    assert is_wordnet_term('phaéton')
    assert is_wordnet_term('protégé')
    assert is_wordnet_term('outré')


def test_empty_and_whitespace():
    assert not is_wordnet_term('')
    assert not is_wordnet_term('   ')
    assert not is_wordnet_term('\t')
    assert not is_wordnet_term('\n')


def test_case_insensitivity():
    assert is_wordnet_term('ALPHA')
    assert is_wordnet_term('Alpha')
    assert is_wordnet_term('COMPUTER')
    assert is_wordnet_term('Computer')
    assert is_wordnet_term('LANGUAGE')


def test_whitespace_stripping():
    assert is_wordnet_term(' alpha ')
    assert is_wordnet_term('  computer  ')
    assert is_wordnet_term('\talpha\t')


def test_common_words():
    assert is_wordnet_term('computer')
    assert is_wordnet_term('language')
    assert is_wordnet_term('beautiful')
    assert is_wordnet_term('running')
    assert is_wordnet_term('knowledge')
    assert is_wordnet_term('mountain')
    assert is_wordnet_term('freedom')


def test_invalid_tokens():
    assert not is_wordnet_term('abc123')
    assert not is_wordnet_term('xyzzy')
    assert not is_wordnet_term('flurble')
    assert not is_wordnet_term('12345')
    assert not is_wordnet_term('zzzzzzz')
    assert not is_wordnet_term('qwerty123')


def test_plural_stripping():
    assert is_wordnet_term('dogs')
    assert is_wordnet_term('cats')
    assert is_wordnet_term('books')
    assert is_wordnet_term('mountains')


def test_plural_stripping_short_words():
    # len <= 3 after normalization: plural stripping does NOT apply
    assert not is_wordnet_term('xys')  # nonsense; len=3, no stripping
    assert not is_wordnet_term('zzs')  # nonsense; len=3, no stripping


def test_unicode_extended():
    assert is_wordnet_term('naïve')
    assert is_wordnet_term('café')
    assert is_wordnet_term('résumé')
    assert is_wordnet_term('façade')


def test_suffixes_with_derivation():
    assert get_suffixes('happiness') == ['ness']
    assert get_suffixes('beautifully') == ['ful', 'ly']
    assert get_suffixes('nationalized') == ['al', 'ize', 'ed']
    assert get_suffixes('running') == ['ing']
    assert get_suffixes('freedom') == ['dom']
    assert get_suffixes('quickly') == ['ly']
    assert get_suffixes('darkness') == ['ness']
    assert get_suffixes('beautiful') == ['ful']
    assert get_suffixes('computerization') == ['er', 'ize', 'ation']


def test_suffixes_monomorphemic():
    assert get_suffixes('cat') == []
    assert get_suffixes('ness') == []


def test_suffixes_not_in_wordnet():
    assert get_suffixes('xyz123') is None
    assert get_suffixes('waddling22') is None
    assert get_suffixes('flurble') is None


def test_suffixes_empty_and_whitespace():
    assert get_suffixes('') is None
    assert get_suffixes('   ') is None


def test_suffixes_case_insensitive():
    assert get_suffixes('HAPPINESS') == ['ness']
    assert get_suffixes('Beautifully') == ['ful', 'ly']


def test_suffixes_whitespace_stripping():
    assert get_suffixes(' happiness ') == ['ness']
    assert get_suffixes('  running  ') == ['ing']


# fmt: off
_KNOWN_WORDS = [
    'computer', 'language', 'mountain', 'freedom', 'running',
    'beautiful', 'happiness', 'knowledge', 'darkness', 'quickly',
    'national', 'natural', 'animal', 'planet', 'science',
    'history', 'theory', 'system', 'process', 'method',
    'result', 'number', 'problem', 'question', 'answer',
    'student', 'teacher', 'doctor', 'mother', 'father',
    'brother', 'sister', 'morning', 'evening', 'winter',
    'summer', 'garden', 'window', 'bottle', 'forest',
]


def _variants(word: str) -> list[str]:
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


_POSITIVE_INPUTS = [v for w in _KNOWN_WORDS for v in _variants(w)]


@pytest.mark.parametrize('word', _POSITIVE_INPUTS)
def test_is_wordnet_term_positive(word):
    assert is_wordnet_term(word)


@pytest.mark.parametrize('word', [
    # numbers
    '123', '456', '789', '0000', '99999',
    # alphanumeric
    'abc123', 'word1', 'test99', 'item42', 'node7',
    # gibberish
    'xyzzy', 'flurble', 'zzzzzz', 'qqqqq', 'blargh',
    'glorp', 'snurble', 'wazzle', 'frumble', 'snibbet',
    # hyphens — none exist in the wordlist
    'well-known', 'mother-in-law', 'self-aware', 'up-to-date',
    'long-term', 'short-term', 'first-class', 'state-of-the-art',
    # apostrophes
    "it's", "don't", "can't", "won't", "they're",
    # mixed garbage
    'hello!', 'world?', 'foo.bar', 'a@b', 'x#y',
])
def test_is_wordnet_term_negative(word):
    assert not is_wordnet_term(word)


_SUFFIX_CASES = [
    ('happiness',       ['ness']),
    ('beautifully',     ['ful', 'ly']),
    ('nationalized',    ['al', 'ize', 'ed']),
    ('running',         ['ing']),
    ('freedom',         ['dom']),
    ('quickly',         ['ly']),
    ('darkness',        ['ness']),
    ('beautiful',       ['ful']),
    ('computerization', ['er', 'ize', 'ation']),
]


def _suffix_variants(word: str, expected: list) -> list[tuple]:
    return [
        (word,                    expected),
        (word.upper(),            expected),
        (word.capitalize(),       expected),
        (f' {word} ',             expected),
        (f'\t{word}\t',           expected),
        (f'  {word}  ',           expected),
    ]


_SUFFIX_INPUTS = [(v, e) for (w, e) in _SUFFIX_CASES for (v, e) in _suffix_variants(w, e)]


@pytest.mark.parametrize('word,expected', _SUFFIX_INPUTS)
def test_get_suffixes_variants(word, expected):
    assert get_suffixes(word) == expected
# fmt: on


def main():
    test_exists()


if __name__ == '__main__':
    main()
