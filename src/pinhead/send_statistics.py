from .slack_api import get_messages_for_days, send_message
from .helpers.collect_statistics import collect_statistics
from .helpers.filters import filter_messages_from_channel_action

from .config import (STATISTICS_PERIOD_IN_DAYS,
                     STATISTICS_MESSAGE, MESSAGE_FINAL_STATUSES_WITH_NOTHING, SLACK_CHANNEL_ID)


all_messages = get_messages_for_days(STATISTICS_PERIOD_IN_DAYS)
channel_requests = filter_messages_from_channel_action(all_messages)
messages_statistics = collect_statistics(channel_requests)

message = STATISTICS_MESSAGE['total'].format(messages_statistics['total_count'])
for message_status in MESSAGE_FINAL_STATUSES_WITH_NOTHING:
    if (messages_statistics[message_status]['total_count'] < 1):
        continue
    message += STATISTICS_MESSAGE[message_status].format(
        messages_statistics[message_status]['total_count'],
        messages_statistics[message_status]['liked_count'],
        messages_statistics[message_status]['disliked_count'],
    )


send_message(SLACK_CHANNEL_ID, message)
