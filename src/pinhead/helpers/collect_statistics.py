from typing import List, Optional

from pinhead.my_types import (Message, Reaction, MessagesStatistics,
                              MessagesStatisticsByType, MessageType)
from pinhead.config import (LIKE_EMOJI_NAME, DISLIKE_EMOJI_NAME,
                            FIX_EMOJI_NAME, DIRTY_FIX_EMOJI_NAME,
                            REJECT_EMOJI_NAME, PLANNED_TO_FIX_EMOJI_NAME)

message_type_to_emoji_map = {
    'fixed': FIX_EMOJI_NAME,
    'dirty_fixed': DIRTY_FIX_EMOJI_NAME,
    'rejected': REJECT_EMOJI_NAME,
    'planned_to_fix': PLANNED_TO_FIX_EMOJI_NAME,
}

default_type_statistics: MessagesStatisticsByType = {
    'total_count': 0,
    'liked_count': 0,
    'disliked_count': 0,
}


def _has_reaction(reactions: Optional[List[Reaction]], reaction_name: str) -> bool:
    if not reactions:
        return False
    for reaction in reactions:
        if reaction.get('name') == reaction_name:
            return True
    return False


def has_not_any_reaction(reactions: Optional[List[Reaction]]) -> bool:
    if not reactions:
        return True

    for reaction_name in [
            LIKE_EMOJI_NAME,
            DISLIKE_EMOJI_NAME,
            FIX_EMOJI_NAME,
            DIRTY_FIX_EMOJI_NAME,
            REJECT_EMOJI_NAME,
            PLANNED_TO_FIX_EMOJI_NAME]:
        if _has_reaction(reactions, reaction_name):
            return False

    return True


def _count_statistics_for_message(
    message: Message,
    message_type: MessageType,
    messages_statistics: MessagesStatistics,
):
    messages_statistics[message_type]['total_count'] += 1
    if _has_reaction(message.get('reactions'), LIKE_EMOJI_NAME):
        messages_statistics[message_type]['liked_count'] += 1

    if _has_reaction(message.get('reactions'), DISLIKE_EMOJI_NAME):
        messages_statistics[message_type]['disliked_count'] += 1

    return messages_statistics


message_types: List[MessageType] = ['fixed', 'rejected', 'dirty_fixed', 'planned_to_fix']


def _count_statistics_by_messages_type(
    message: Message,
    messages_statistics: MessagesStatistics,
):
    for message_type in message_types:
        if _has_reaction(message.get('reactions'), message_type_to_emoji_map[message_type]):
            messages_statistics = _count_statistics_for_message(
                message, message_type, messages_statistics)
            break

    return messages_statistics


def collect_statistics(messages: List[Message]) -> MessagesStatistics:
    messages_statistics: MessagesStatistics = {
        'total_count': 0,
        'rejected': default_type_statistics.copy(),
        'fixed': default_type_statistics.copy(),
        'dirty_fixed': default_type_statistics.copy(),
        'planned_to_fix': default_type_statistics.copy(),
        'nothing': default_type_statistics.copy(),
    }

    for message in messages:
        messages_statistics['total_count'] += 1
        if not message.get('reactions'):
            messages_statistics['nothing']['total_count'] += 1
            continue

        if has_not_any_reaction(message.get('reactions')):
            messages_statistics = _count_statistics_for_message(
                message, 'nothing', messages_statistics)
            continue

        messages_statistics = _count_statistics_by_messages_type(message, messages_statistics)

    return messages_statistics
