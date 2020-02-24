from typing import List

from pinhead.my_types import Message

from pinhead.config import SLACK_CHANNEL_BOT_ID

from pinhead.helpers.checkers import include_final_status, include_evaluation


def filter_finished_messages(messages: List[Message]) -> List[Message]:
    return [message for message in messages if include_final_status(message.get('reactions'))]


def filter_messages_from_channel_action(
    messages: List[Message], bot_id: str = SLACK_CHANNEL_BOT_ID,
) -> List[Message]:
    return [m for m in messages if (m.get('subtype') == 'bot_message'
                                    and m.get('bot_id') == bot_id)]


def filter_not_evaluated_messages(messages: List[Message]) -> List[Message]:
    return [message for message in messages if not include_evaluation(message.get('reactions'))]
