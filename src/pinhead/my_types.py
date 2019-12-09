from typing import List
from typing_extensions import TypedDict


class Reaction(TypedDict):
    name: str
    users: List[str]
    count: int


class Message(TypedDict, total=False):
    text: str
    user: str
    bot_id: str
    subtype: str
    ts: str
    reactions: List[Reaction]


class MessagesStatisticsByType(TypedDict):
    total_count: int
    liked_count: int
    disliked_count: int


class MessagesStatistics(TypedDict):
    total_count: int
    rejected: MessagesStatisticsByType
    fixed: MessagesStatisticsByType
    dirty_fixed: MessagesStatisticsByType
    planned_to_fix: MessagesStatisticsByType
    nothing: MessagesStatisticsByType
