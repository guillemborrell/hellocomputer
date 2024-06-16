from pathlib import Path

import hellocomputer
from hellocomputer.db import StorageEngines
from hellocomputer.db.users import OwnershipDB, UserDB

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


def test_assign_owner():
    assert (
        OwnershipDB(storage_engine=TEST_STORAGE, path=TEST_OUTPUT_FOLDER).set_ownersip(
            "something.something@something", "testsession", "test"
        )
        == "testsession"
    )


def test_get_sessions():
    assert OwnershipDB(storage_engine=TEST_STORAGE, path=TEST_OUTPUT_FOLDER).sessions(
        "something.something@something"
    ) == ["testsession"]
