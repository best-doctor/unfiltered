from typing import List, Dict

LIKE_EMOJI_NAME = '+1'
DISLIKE_EMOJI_NAME = '-1'
FIX_EMOJI_NAME = 'white_check_mark'
DIRTY_FIX_EMOJI_NAME = 'podorojnik'
REJECT_EMOJI_NAME = 'x'
PLANNED_TO_FIX_EMOJI_NAME = 'eyes'

REACT_REMINDER = (
    "You don't appreciate solving of your problem, "
    'please react with emojis right now for {0}'
)
# STATISTICS_MESSAGES =

REMIND_REACT_FOR_DAYS = 5
STATISTICS_PERIOD_IN_DAYS = 5
STATISTICS_MESSAGE: Dict[str, str] = {}

IS_DEBUG_ENABLED = False

ATTENDANTS: List[Dict[str, str]] = []
SLACK_CHANNEL_ID = ''
DEBUG_SLACK_CHANNEL_ID = ''
SLACK_CHANNEL_BOT_ID = ''
SLACK_TOKEN = ''

try:
    from .local_config import *  # noqa:F401,F403
except ImportError:
    pass
