from wordnet_lookup import is_wordnet_term


def test_lookup():
    assert is_wordnet_term('alpha')
