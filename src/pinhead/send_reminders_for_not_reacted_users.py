from .slack_api import send_message, get_message_permalink, get_messages_for_days

from .helpers.filter_unreacted_bot_messages import filter_unreacted_bot_messages
from .helpers.get_user_id_from_message_text import get_user_id_from_message_text


from .config import REACT_REMINDER, REMIND_REACT_FOR_DAYS


all_messages = get_messages_for_days(REMIND_REACT_FOR_DAYS)
unreacted_bot_messages = filter_unreacted_bot_messages(all_messages)

for message in unreacted_bot_messages:
    user_id = get_user_id_from_message_text(message.get('text'))
    if not user_id:
        continue
    message_permalink = get_message_permalink(message.get('ts'))
    send_message(user_id, REACT_REMINDER.format(message_permalink))
