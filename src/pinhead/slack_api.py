import time
import requests

from datetime import datetime, timedelta
from typing import List, Optional

from .my_types import Message
from .config import (SLACK_TOKEN, SLACK_CHANNEL_ID, DEBUG_SLACK_CHANNEL_ID, IS_DEBUG_ENABLED)

channel_id = DEBUG_SLACK_CHANNEL_ID if IS_DEBUG_ENABLED else SLACK_CHANNEL_ID


def _mktime(dt: datetime) -> str:
    return str(time.mktime(dt.timetuple()))


def _get_channel_messages_for_period(latest: datetime, oldest: datetime) -> List[Message]:
    response_json = requests.get(
        'https://slack.com/api/conversations.history',
        params={
            'token': SLACK_TOKEN,
            'channel': channel_id,
            'latest': _mktime(latest),
            'oldest': _mktime(oldest),
            'limit': '1000',
        },
    ).json()
    try:
        messages = response_json['messages']
    except KeyError:
        messages = []
    return messages


def get_messages_for_days(days: int = 1) -> List[Message]:
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    return _get_channel_messages_for_period(end_time, start_time)


def get_message_permalink(message_ts: Optional[str]) -> str:
    if not message_ts:
        return '-'
    response_json = requests.get(
        'https://slack.com/api/chat.getPermalink',
        params={
            'token': SLACK_TOKEN,
            'channel': channel_id,
            'message_ts': message_ts,
        },
    ).json()
    try:
        permalink = response_json['permalink']
    except KeyError:
        permalink = ''
    return permalink


def send_message(channel_id: str, message: str, thread_ts: Optional[str] = None) -> None:
    requests.post(
        'https://slack.com/api/chat.postMessage',
        params={
            'token': SLACK_TOKEN,
            'channel': channel_id,
            'text': message,
            'thread_ts': thread_ts,
        },
    )
