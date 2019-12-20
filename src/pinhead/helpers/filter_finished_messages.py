from typing import List

from pinhead.my_types import Message
from pinhead.helpers.collect_statistics import has_not_any_reaction


def filter_finished_messages(messages: List[Message]) -> List[Message]:
    return [message for message in messages if not has_not_any_reaction(message.get('reactions'))]
