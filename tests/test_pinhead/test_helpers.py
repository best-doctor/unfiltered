import pytest

from pinhead.helpers import get_user_id_from_message_text, filter_unreacted_bot_messages
from pinhead.config import SLACK_CHANNEL_BOT_ID

from factories import MessageFactory, ReactionFactory


@pytest.mark.parametrize("message_text, user_id", [
    ('asdf asdf 123456> adsf asdf ', None),
    ('asdf asdf @123456> adsf asdf ', None),
    ('asdf asdf <@123456> adsf asdf ', '123456'),
    ('<@123456>', '123456'),
    ('123456', None),
])
def test_get_user_id_from_message_text(message_text, user_id):
    assert get_user_id_from_message_text(message_text) == user_id


@pytest.mark.parametrize("test_messages, messages_with_reaction_count", [
    ([
        {
            'reactions': [{'name': '+1'}, {'name': 'test'}],
            'subtype': 'bot_message',
            'bot_id': SLACK_CHANNEL_BOT_ID,
        },
        {
            'reactions': [{'name': '-1'}, {'name': 'test'}],
            'subtype': 'bot_message',
            'bot_id': SLACK_CHANNEL_BOT_ID,
        }
    ], 0),

    ([
        {
            'reactions': [{'name': '+1'}, {'name': 'test'}],
            'subtype': 'subtytle',
            'bot_id': SLACK_CHANNEL_BOT_ID,
        },
        {
            'reactions': [{'name': '1'}, {'name': 'test'}],
            'subtype': 'bot_message',
            'bot_id': SLACK_CHANNEL_BOT_ID,
        }
    ], 1),

    ([
        {
            'reactions': [{'name': '+1'}, {'name': 'test'}],
            'subtype': 'bot_messages',
            'bot_id': 'test_bot_id',
        },
        {
            'reactions': [{'name': '-1'}, {'name': 'test'}],
            'subtype': 'bot_message',
            'bot_id': 'tst_bot_id',
        }
    ], 0),
    ([
        {
            'reactions': [{'name': '1'}, {'name': 'test'}],
            'subtype': 'bot_message',
            'bot_id': SLACK_CHANNEL_BOT_ID,
        },
        {
            'reactions': [{'name': '1'}, {'name': 'test'}],
            'subtype': 'bot_message',
            'bot_id': SLACK_CHANNEL_BOT_ID,
        }
    ], 2),
    ([
        {
            'reactions': [],
            'subtype': 'bot_message',
            'bot_id': SLACK_CHANNEL_BOT_ID,
        },
        {
            'reactions': [{'name': '1'}, {'name': 'test'}],
            'subtype': 'bot_message',
            'bot_id': SLACK_CHANNEL_BOT_ID,
        }
    ], 2),
])
def test_filter_unreacted_bot_messages(test_messages, messages_with_reaction_count):
    messages = []
    for test_message in test_messages:
        reactions = [ReactionFactory(name=r['name']) for r in test_message['reactions']]
        message = MessageFactory(
            reactions=reactions, subtype=test_message['subtype'], bot_id=test_message['bot_id'])
        messages.append(message)

    filtered_messages = filter_unreacted_bot_messages(messages)
    assert len(filtered_messages) == messages_with_reaction_count
