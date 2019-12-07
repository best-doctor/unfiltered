import pytest

from pinhead.helpers import get_user_id_from_message_text


@pytest.mark.parametrize("message_text, user_id", [
    ('asdf asdf 123456> adsf asdf ', None),
    ('asdf asdf @123456> adsf asdf ', None),
    ('asdf asdf <@123456> adsf asdf ', '123456'),
    ('<@123456>', '123456'),
    ('123456', None),
])
def test_get_user_id_from_message_text(message_text, user_id):
    assert get_user_id_from_message_text(message_text) == user_id
