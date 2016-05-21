import pytest
import json
from run import SlackAttachmentCheck as sac


@pytest.fixture
def get_json():
    with open('test.json', 'r') as fp:
        return json.load(fp)


def test_iterate_through_json_obj(get_json):
    results = sac.iterate_through_json_obj(get_json)
    # This should be *one* because the second message with attachments is hidden
    assert len(results) == 1


def test_look_for_matches(get_json):
    msgs = sac.iterate_through_json_obj(get_json)
    results = sac.check_urls_in_attachments(r"digitalocean\.com", msgs)
    assert len(results) == 1


def test_look_for_false_matches(get_json):
    msgs = sac.iterate_through_json_obj(get_json)
    results = sac.check_urls_in_attachments(r"google\.com", msgs)
    assert len(results) == 0
