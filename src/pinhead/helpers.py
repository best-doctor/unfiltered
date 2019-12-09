import re

from typing import List, Optional

from .my_types import Message

from .config import LIKE_EMOJI_NAME, DISLIKE_EMOJI_NAME, SLACK_CHANNEL_BOT_ID


def _filter_channel_bot_messages(messages: List[Message]) -> List[Message]:
    return [m for m in messages if (m.get('subtype') == 'bot_message'
                                    and m.get('bot_id') == SLACK_CHANNEL_BOT_ID)]


def _check_message_do_not_have_reaction(message: Message):
    reactions = message.get('reactions')
    if not reactions:
        return True
    for reaction in reactions:
        if reaction.get('name') == LIKE_EMOJI_NAME or reaction.get('name') == DISLIKE_EMOJI_NAME:
            return False
    return True


def _filter_unreacted_messages(messages: List[Message]) -> List[Message]:
    return list(filter(_check_message_do_not_have_reaction, messages))


def filter_unreacted_bot_messages(all_messages: List[Message]) -> List[Message]:
    bot_messages = _filter_channel_bot_messages(all_messages)
    return _filter_unreacted_messages(bot_messages)


def get_user_id_from_message_text(message_text: Optional[str]) -> Optional[str]:
    if not message_text:
        return None
    wrapper_user_id_array = re.findall(r'<@[\w]*>', message_text)
    if not wrapper_user_id_array:
        return None
    return wrapper_user_id_array[0].replace('<@', '').replace('>', '')
