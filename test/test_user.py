from pathlib import Path

import hellocomputer
from hellocomputer.config import Settings, StorageEngines
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
        OwnershipDB(settings).set_ownership(
            "test@test.com", "sid", "session_name", "record_id"
        )
        == "sid"
    )


def test_get_sessions():
    assert OwnershipDB(settings).sessions("test@test.com") == [
        {"sid": "sid", "session_name": "session_name"}
    ]
