from .find_wordnet import FindWordnet


def is_wordnet_term(input_text: str) -> bool:
    return FindWordnet().exists(input_text)
