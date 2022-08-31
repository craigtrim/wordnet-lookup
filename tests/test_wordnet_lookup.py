from baseblock import Stopwatch

from wordnet_lookup import is_wordnet_term


def test_lookup():
    assert is_wordnet_term('alpha')


def test_exists():

    sw = Stopwatch()
    assert is_wordnet_term('waddling')
    print(str(sw))

    sw = Stopwatch()
    assert not is_wordnet_term('waddling22')
    print(str(sw))

    sw = Stopwatch()
    assert is_wordnet_term('myxovirus')
    print(str(sw))

    sw = Stopwatch()
    assert is_wordnet_term('according')
    print(str(sw))

    sw = Stopwatch()
    assert is_wordnet_term('acetabulars')
    print(str(sw))


def main():
    test_exists()


if __name__ == "__main__":
    main()
