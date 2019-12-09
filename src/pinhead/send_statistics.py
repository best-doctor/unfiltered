from .slack_api import get_messages_for_days
from .helpers.collect_statistics import collect_statistics

from .config import STATISTICS_PERIOD_IN_DAYS


all_messages = get_messages_for_days(STATISTICS_PERIOD_IN_DAYS)
messages_statistics = collect_statistics(all_messages)

# print(messages_statistics)
