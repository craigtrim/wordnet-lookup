from .find_suffixes import get_suffixes
from .find_wordnet import FindWordnet


def is_wordnet_term(input_text: str) -> bool:
    return FindWordnet().exists(input_text)


__all__ = ['is_wordnet_term', 'get_suffixes']
