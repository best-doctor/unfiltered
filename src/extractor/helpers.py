from typing import Iterable, List


def flat(some_list: Iterable[Iterable]) -> List:
    return [item for sublist in some_list for item in sublist]
