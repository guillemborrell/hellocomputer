from pathlib import Path

import hellocomputer
from hellocomputer.db import StorageEngines
from hellocomputer.users import UserDB

TEST_STORAGE = StorageEngines.local
TEST_OUTPUT_FOLDER = Path(hellocomputer.__file__).parents[2] / "test" / "output"


def test_create_user():
    user = UserDB(storage_engine=TEST_STORAGE, path=TEST_OUTPUT_FOLDER)
    user_data = {"name": "John Doe", "email": "[email protected]"}
    user_data = user.dump_user_record(user_data, record_id="test")

    assert user_data["name"] == "John Doe"


def test_user_exists():
    user = UserDB(storage_engine=TEST_STORAGE, path=TEST_OUTPUT_FOLDER)
    user_data = {"name": "John Doe", "email": "[email protected]"}
    user.dump_user_record(user_data, record_id="test")

    assert user.user_exists("[email protected]")
    assert not user.user_exists("notpresent")
