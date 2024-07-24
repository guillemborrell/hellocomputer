from pathlib import Path

import hellocomputer
from hellocomputer.config import StorageEngines, Settings
from hellocomputer.db.sessions import SessionDB

settings = Settings(
    storage_engine=StorageEngines.local,
    path=Path(hellocomputer.__file__).parents[2] / "test" / "output",
)

TEST_XLS_PATH = (
    Path(hellocomputer.__file__).parents[2]
    / "test"
    / "data"
    / "TestExcelHelloComputer.xlsx"
)


def test_0_dump():
    db = SessionDB(settings, sid="test")
    db.load_xls(TEST_XLS_PATH).dump()

    assert db.sheets == ("answers",)
    assert (settings.path / "sessions" / "test" / "answers.csv").exists()


def test_load():
    db = SessionDB(settings, sid="test").load_folder()
    results = db.query("select * from answers").fetchall()
    assert len(results) == 6


def test_load_description():
    db = SessionDB(settings, sid="test").load_folder()
    file_description = db.load_description()
    assert file_description.startswith("answers")


def test_schema():
    db = SessionDB(settings, sid="test").load_folder()
    schema = []
    for sheet in db.sheets:
        schema.append(db.table_schema(sheet))

    assert db.schema.startswith("The schema of the database")


def test_query_prompt():
    db = SessionDB(settings, sid="test").load_folder()

    assert db.query_prompt("Find the average score of all students").startswith(
        "The following sentence"
    )
