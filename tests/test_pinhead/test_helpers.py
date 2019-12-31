import os
import pytest
import json

from pinhead.helpers.get_user_id_from_message_text import get_user_id_from_message_text
from pinhead.helpers.collect_statistics import collect_statistics
from pinhead.helpers.checkers import include_reactions, include_evaluation, include_final_status
from pinhead.helpers.filters import (filter_finished_messages,
                                     filter_messages_from_channel_action,
                                     filter_not_evaluated_messages)

from pinhead.config import SLACK_CHANNEL_BOT_ID

from factories import MessageFactory, ReactionFactory


def _load_fixture(fixture_file_name: str) -> any:
    dirname = os.path.dirname(__file__)
    fixture_file_path = os.path.join(dirname, f'fixtures/{fixture_file_name}')
    fixture_file = open(fixture_file_path)
    fixture_json = fixture_file.read()
    fixture = json.loads(fixture_json)
    return fixture


@pytest.mark.parametrize("message_text, user_id", [
    ('asdf asdf 123456> adsf asdf ', None),
    ('asdf asdf @123456> adsf asdf ', None),
    ('asdf asdf <@123456> adsf asdf ', '123456'),
    ('<@123456>', '123456'),
    ('123456', None),
])
def test_get_user_id_from_message_text(message_text, user_id):
    assert get_user_id_from_message_text(message_text) == user_id


@pytest.mark.parametrize("reactions, expected_result", [
    (
        [{'name': 'x'}, {'name': 'test'}],
        True
    ),
    (
        [{'name': '-1'}, {'name': 'test'}],
        False
    ),
])
def test_include_final_statuses(reactions, expected_result):
    assert include_final_status(reactions) == expected_result


@pytest.mark.parametrize("reactions, expected_result", [
    (
        [{'name': '+1'}, {'name': 'test'}],
        True
    ),
    (
        [{'name': 'podorojnik'}, {'name': 'test'}],
        False
    ),
])
def test_include_evaluation(reactions, expected_result):
    assert include_evaluation(reactions) == expected_result


@pytest.mark.parametrize("reactions, desired_reactions_names, expected_result", [
    (
        [{'name': '+1'}, {'name': 'test'}],
        ['+1'],
        True
    ),
    (
        [{'name': 'podorojnik'}, {'name': 'test'}],
        ['-1'],
        False
    ),
])
def test_include_reactions(reactions, desired_reactions_names, expected_result):
    assert include_reactions(reactions, desired_reactions_names) == expected_result


@pytest.mark.parametrize("fixtures_file_name, expected_result", [
    ('messages.json', 11)
])
def test_filter_finished_messages(fixtures_file_name, expected_result):
    messages = _load_fixture(fixtures_file_name)
    assert len(filter_finished_messages(messages)) == expected_result


@pytest.mark.parametrize("fixtures_file_name, expected_result", [
    ('messages.json', 9)
])
def test_filter_messages_from_channel_action(fixtures_file_name, expected_result):
    messages = _load_fixture(fixtures_file_name)
    assert len(filter_messages_from_channel_action(messages, 'test_id')) == expected_result


@pytest.mark.parametrize("fixtures_file_name, expected_result", [
    ('messages.json', 9)
])
def test_filter_not_evaluated_messages(fixtures_file_name, expected_result):
    messages = _load_fixture(fixtures_file_name)
    assert len(filter_not_evaluated_messages(messages)) == expected_result


@pytest.mark.parametrize("fixtures_file_name, expected_result", [
    ('messages.json',
     {
         'total_count': 12,
         'rejected': {'total_count': 3, 'liked_count': 1, 'disliked_count': 0},
         'fixed': {'total_count': 4, 'liked_count': 0, 'disliked_count': 0},
         'dirty_fixed': {
             'total_count': 3, 'liked_count': 2, 'disliked_count': 0},
         'planned_to_fix': {'total_count': 1, 'liked_count': 0, 'disliked_count': 0},
         'nothing': {'total_count': 1, 'liked_count': 0, 'disliked_count': 0}}
     )
])
def test_collect_statistics(fixtures_file_name, expected_result):
    messages = _load_fixture(fixtures_file_name)
    assert collect_statistics(messages) == expected_result
