from .slack_api_helpers import send_message, get_message_permalink
from .helpers import get_unreacted_messages_for_period, get_user_id_from_message_text

from .config import REACT_REMINDER, REMIND_REACT_FOR_DAYS


unreacted_messages = get_unreacted_messages_for_period(REMIND_REACT_FOR_DAYS)

for message in unreacted_messages:
    user_id = get_user_id_from_message_text(message.get('text'))
    if not user_id:
        continue
    message_permalink = get_message_permalink(message.get('ts'))
    send_message(user_id, REACT_REMINDER.format(message_permalink))
