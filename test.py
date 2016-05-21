import pytest
import json
from run import SlackAttachmentCheck as sac
from models import Slack


@pytest.fixture
def get_data():
    return (Slack.select().limit(1000))


def test_iterate_through_json_obj(get_data):
    results = sac.iterate_through_json_obj(get_data)
    assert len(results) == 63


def test_look_for_matches(get_data):
    msgs = sac.iterate_through_json_obj(get_data)
    results = sac.check_urls_in_attachments(r"docs\.google\.com", msgs)
    assert len(results) == 1


def test_look_for_false_matches(get_data):
    msgs = sac.iterate_through_json_obj(get_data)
    results = sac.check_urls_in_attachments(r"xyz\.com", msgs)
    assert len(results) == 0
