from hellocomputer.tools import extract_sid, remove_sid

message = """This is a message
******sid******
"""


def test_match_sid():
    assert extract_sid(message) == "sid"


def test_remove_sid():
    assert remove_sid(message) == "This is a message"
