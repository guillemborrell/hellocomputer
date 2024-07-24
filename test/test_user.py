from pathlib import Path

import hellocomputer
from hellocomputer.config import StorageEngines, Settings
from hellocomputer.db.users import OwnershipDB, UserDB

settings = Settings(
    storage_engine=StorageEngines.local,
    path=Path(hellocomputer.__file__).parents[2] / "test" / "output",
)


def test_create_user():
    user = UserDB(settings)
    user_data = {"name": "John Doe", "email": "[email protected]"}
    user_data = user.dump_user_record(user_data, record_id="test")

    assert user_data["name"] == "John Doe"


def test_user_exists():
    user = UserDB(settings)
    user_data = {"name": "John Doe", "email": "[email protected]"}
    user.dump_user_record(user_data, record_id="test")

    assert user.user_exists("[email protected]")
    assert not user.user_exists("notpresent")


def test_assign_owner():
    assert (
        OwnershipDB(settings).set_ownersip(
            "something.something@something", "testsession", "test"
        )
        == "testsession"
    )


def test_get_sessions():
    assert OwnershipDB(settings).sessions("something.something@something") == [
        "testsession"
    ]
