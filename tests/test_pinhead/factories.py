from factory import Factory, SubFactory

from pinhead.my_types import Message, Reaction


class ReactionFactory(Factory):
    ABSTRACT_FACTORY = True

    class Meta:
        model = Reaction

    name = 'reaction_name'
    users = ['1', '2']
    count = 2

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        return target_class(*args, **kwargs)


class MessageFactory(Factory):
    ABSTRACT_FACTORY = True

    class Meta:
        model = Message

    text = 'text '
    user = '1'
    bot_id = '123'
    subtype = 'aaaa'
    ts = '1233'
    reactions = [SubFactory(ReactionFactory)]

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        return target_class(*args, **kwargs)

    # def get(self, property_name: str):
