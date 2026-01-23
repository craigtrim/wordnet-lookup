from wordnet_lookup import is_wordnet_term


def test_lookup():
    assert is_wordnet_term('alpha')


def test_exists():
    assert is_wordnet_term('waddling')
    assert not is_wordnet_term('waddling22')
    assert is_wordnet_term('myxovirus')
    assert is_wordnet_term('according')
    assert is_wordnet_term('acetabulars')


def main():
    test_exists()


if __name__ == '__main__':
    main()
