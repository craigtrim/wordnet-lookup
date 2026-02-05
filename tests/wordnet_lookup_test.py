from wordnet_lookup import is_wordnet_term


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


def main():
    test_exists()


if __name__ == '__main__':
    main()
