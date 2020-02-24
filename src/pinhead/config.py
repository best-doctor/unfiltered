from typing import List, Dict

from .my_types import MessageFinalStatus

ATTENDANTS: List[Dict[str, str]] = []

SLACK_CHANNEL_ID = ''
DEBUG_SLACK_CHANNEL_ID = ''
SLACK_CHANNEL_BOT_ID = ''
SLACK_TOKEN = ''

STATISTICS_MESSAGE: Dict[str, str] = {
    'total': '',
    'rejected': '',
    'fixed': '',
    'dirty_fixed': '',
    'planned_to_fix': '',
    'nothing': '',
}

REACT_REMINDER = (
    "You don't appreciate solving of your problem, "
    'please react with emojis right now for {0}'
)

MESSAGE_FINAL_STATUSES: List[MessageFinalStatus] = [
    'fixed', 'rejected', 'dirty_fixed', 'planned_to_fix']

MESSAGE_FINAL_STATUSES_WITH_NOTHING: List[MessageFinalStatus] = MESSAGE_FINAL_STATUSES + [
    'nothing']

EVALUATION_EMOJI_NAMES = {
    'like': '+1',
    'dislike': '-1',
}

FINAL_STATUSES_EMOJI_NAMES: Dict[MessageFinalStatus, str] = {
    'fixed': 'white_check_mark',
    'dirty_fixed': 'podorojnik',
    'rejected': 'x',
    'planned_to_fix': 'eyes',
}


REMIND_REACT_FOR_DAYS = 2
STATISTICS_PERIOD_IN_DAYS = 2


IS_DEBUG_ENABLED = False

try:
    from .local_config import *  # noqa:F401,F403
except ImportError:
    pass
