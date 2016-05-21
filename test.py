import pytest
from run import SlackAttachmentCheck as sac


def test_iterate_through_json_obj():
    results = sac.iterate_through_json_obj('test.json')
    # This should be *one* because the second message with attachments is hidden
    assert len(results) == 1


def test_look_for_matches():
    msgs = sac.iterate_through_json_obj('test.json')
    results = sac.check_urls_in_attachments(r"digitalocean\.com", msgs)
    assert len(results) == 1


def test_look_for_false_matches():
    msgs = sac.iterate_through_json_obj('test.json')
    results = sac.check_urls_in_attachments(r"google\.com", msgs)
    assert len(results) == 0
