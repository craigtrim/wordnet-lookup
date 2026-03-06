from .find_suffixes import get_suffixes
from .find_inflections import get_inflections
from .find_wordnet import FindWordnet
from .morphology import Morphology, get_morphology


def is_wordnet_term(input_text: str) -> bool:
    return FindWordnet().exists(input_text)


__all__ = ['is_wordnet_term', 'get_suffixes',
           'get_inflections', 'Morphology', 'get_morphology']
