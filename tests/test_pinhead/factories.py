from factory import Factory, SubFactory

from pinhead.my_types import Message, Reaction


class ReactionFactory(Factory):
    name: 'reaction_name'
    users: ['1', '2']
    count: 2


class MessageFactory(Factory):
    class Meta:
        model = Message

    text: 'text '
    user: '1'
    bot_id: '123'
    subtype: 'aaaa'
    ts: '1233'
    reactions: [SubFactory(ReactionFactory)]
