from typing import List

from pinhead.my_types import (Message, MessagesStatistics,
                              MessagesStatisticsByType, MessageFinalStatus)
from pinhead.config import (FINAL_STATUSES_EMOJI_NAMES,
                            MESSAGE_FINAL_STATUSES,
                            EVALUATION_EMOJI_NAMES)

from pinhead.helpers.checkers import include_reactions, include_final_status


default_type_statistics: MessagesStatisticsByType = {
    'total_count': 0,
    'liked_count': 0,
    'disliked_count': 0,
}


def _count_statistics_for_message(
    message: Message,
    message_final_status: MessageFinalStatus,
    messages_statistics: MessagesStatistics,
) -> MessagesStatistics:
    messages_statistics[message_final_status]['total_count'] += 1
    if include_reactions(message.get('reactions'), [EVALUATION_EMOJI_NAMES['like']]):
        messages_statistics[message_final_status]['liked_count'] += 1

    if include_reactions(message.get('reactions'), [EVALUATION_EMOJI_NAMES['dislike']]):
        messages_statistics[message_final_status]['disliked_count'] += 1

    return messages_statistics


def _count_statistics_by_messages_final_status(
    message: Message,
    messages_statistics: MessagesStatistics,
) -> MessagesStatistics:
    for message_final_status in MESSAGE_FINAL_STATUSES:
        if include_reactions(message.get('reactions'),
                             [FINAL_STATUSES_EMOJI_NAMES[message_final_status]]):
            messages_statistics = _count_statistics_for_message(
                message, message_final_status, messages_statistics)
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

        if not include_final_status(message.get('reactions')):
            messages_statistics = _count_statistics_for_message(
                message, 'nothing', messages_statistics)
            continue

        messages_statistics = _count_statistics_by_messages_final_status(
            message, messages_statistics)

    return messages_statistics
