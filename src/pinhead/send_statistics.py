from .slack_api import get_messages_for_days, send_message
from .helpers.collect_statistics import collect_statistics
from .helpers.filter_unreacted_bot_messages import filter_channel_bot_messages

from .config import STATISTICS_PERIOD_IN_DAYS, STATISTICS_MESSAGE, SLACK_CHANNEL_ID

all_messages = get_messages_for_days(STATISTICS_PERIOD_IN_DAYS)
bot_messages = filter_channel_bot_messages(all_messages)
messages_statistics = collect_statistics(bot_messages)

message = STATISTICS_MESSAGE['total'].format(messages_statistics['total_count'])
for message_type in ['fixed', 'rejected', 'planned_to_fix', 'dirty_fixed', 'nothing']:
    if (messages_statistics[message_type]['total_count'] < 1):
        continue
    message += STATISTICS_MESSAGE[message_type].format(
        messages_statistics[message_type]['total_count'],
        messages_statistics[message_type]['liked_count'],
        messages_statistics[message_type]['disliked_count'],
    )


send_message(SLACK_CHANNEL_ID, message)
