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
