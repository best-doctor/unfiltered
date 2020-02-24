from .slack_api import send_message, get_messages_for_days

from .helpers.filters import (filter_messages_from_channel_action,
                              filter_finished_messages,
                              filter_not_evaluated_messages)
from .helpers.get_user_id_from_message_text import get_user_id_from_message_text


from .config import REACT_REMINDER, REMIND_REACT_FOR_DAYS, SLACK_CHANNEL_ID

all_messages = get_messages_for_days(REMIND_REACT_FOR_DAYS)
channel_requests = filter_messages_from_channel_action(all_messages)
finished_channel_requests = filter_finished_messages(channel_requests)
not_evaluated_finished_channel_requests = filter_not_evaluated_messages(finished_channel_requests)


for message in not_evaluated_finished_channel_requests:
    user_id = get_user_id_from_message_text(message.get('text'))
    if not user_id:
        continue

    send_message(SLACK_CHANNEL_ID, REACT_REMINDER.format(user_id), message.get('ts'))
