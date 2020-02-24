from typing import List, Optional

from pinhead.my_types import Reaction
from pinhead.config import FINAL_STATUSES_EMOJI_NAMES, EVALUATION_EMOJI_NAMES


def include_reactions(
    message_reactions: Optional[List[Reaction]], desired_reactions_names: List[str],
) -> bool:
    if not message_reactions:
        return False
    for message_reaction in message_reactions:
        if message_reaction.get('name') in desired_reactions_names:
            return True

    return False


def include_evaluation(reactions: Optional[List[Reaction]]) -> bool:
    return include_reactions(reactions, list(EVALUATION_EMOJI_NAMES.values()))


def include_final_status(reactions: Optional[List[Reaction]]) -> bool:
    return include_reactions(reactions, list(FINAL_STATUSES_EMOJI_NAMES.values()))
