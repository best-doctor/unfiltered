import re

from datetime import datetime, timedelta
from typing import List, Optional

from slack_api_helpers import get_channel_messages_for_period
from my_types import Message

from local_config import SLACK_CHANNEL_BOT_ID
from config import LIKE_EMOJI_NAME, DISLIKE_EMOJI_NAME


def _filter_channel_bot_messages(messages: List[Message]) -> List[Message]:
    return [m for m in messages if m.get('subtype') == 'bot_message' and m.get('bot_id') == SLACK_CHANNEL_BOT_ID]


def _check_message_reactions_do_not_have_reaction(message: Message):
    for reaction in message.get('reactions'):
        if reaction.get('name') == LIKE_EMOJI_NAME or reaction.get('name') == DISLIKE_EMOJI_NAME:
            return False
    return True


def _filter_unreacted_messages(messages: List[Message]) -> List[Message]:
    return list(filter(_check_message_reactions_do_not_have_reaction, messages))


def get_unreacted_messages_for_period(days: int = 1) -> List[Message]:
    end_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=days)

    all_messages = get_channel_messages_for_period(
        end_time, start_time)
    bot_messages = _filter_channel_bot_messages(all_messages)
    unreacted_bot_messages = _filter_unreacted_messages(bot_messages)
    return unreacted_bot_messages


def get_user_id_from_message_text(message_text: str) -> Optional[str]:
    wrapper_user_id_array = re.findall(r"<@[\w]*>", message_text)
    if not wrapper_user_id_array:
        return None
    return wrapper_user_id_array[0].replace('<@', '').replace('>', '')
