from pathlib import Path

import hellocomputer
from hellocomputer.analytics import DDB, StorageEngines

TEST_STORAGE = StorageEngines.local
TEST_XLS_PATH = (
    Path(hellocomputer.__file__).parents[2]
    / "test"
    / "data"
    / "TestExcelHelloComputer.xlsx"
)
TEST_OUTPUT_FOLDER = Path(hellocomputer.__file__).parents[2] / "test" / "output"


def test_0_dump():
    db = DDB(storage_engine=TEST_STORAGE, path=TEST_OUTPUT_FOLDER)
    db.load_xls(TEST_XLS_PATH).dump()

    assert db.sheets == ("answers",)
    assert (TEST_OUTPUT_FOLDER / "answers.csv").exists()


def test_load():
    db = DDB(storage_engine=TEST_STORAGE, path=TEST_OUTPUT_FOLDER).load_folder()
    results = db.query("select * from answers").fetchall()
    assert len(results) == 6


def test_load_description():
    db = DDB(storage_engine=TEST_STORAGE, path=TEST_OUTPUT_FOLDER).load_folder()
    file_description = db.load_description()
    assert file_description.startswith("answers")


def test_schema():
    db = DDB(storage_engine=TEST_STORAGE, path=TEST_OUTPUT_FOLDER).load_folder()
    schema = []
    for sheet in db.sheets:
        schema.append(db.table_schema(sheet))

    print(db.schema)

    assert db.schema.startswith("The schema of the database")


def test_query_prompt():
    db = DDB(storage_engine=TEST_STORAGE, path=TEST_OUTPUT_FOLDER).load_folder()

    assert db.query_prompt("Find the average score of all students").startswith(
        "The following sentence"
    )
