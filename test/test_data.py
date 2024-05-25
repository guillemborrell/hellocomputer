import hellocomputer
from hellocomputer.analytics import DDB
from pathlib import Path

TEST_DATA_FOLDER = Path(hellocomputer.__file__).parents[2] / "test" / "data"
TEST_OUTPUT_FOLDER = Path(hellocomputer.__file__).parents[2] / "test" / "output"


def test_dump():
    db = (
        DDB()
        .load_metadata(TEST_DATA_FOLDER / "TestExcelHelloComputer.xlsx")
        .dump_local(TEST_OUTPUT_FOLDER)
    )

    assert db.sheets == ("answers",)
    assert (TEST_OUTPUT_FOLDER / "answers.csv").exists()


def test_load():
    db = DDB().load_folder_local(TEST_OUTPUT_FOLDER)

    assert db.sheets == ("answers",)

    results = db.query("select * from answers").fetchall()
    assert len(results) == 2


def test_load_description():
    file_description = DDB().load_description_local(TEST_OUTPUT_FOLDER)
    assert file_description.startswith("answers")


def test_schema():
    db = DDB().load_folder_local(TEST_OUTPUT_FOLDER)
    schema = []
    for sheet in db.sheets:
        schema.append(db.table_schema(sheet))

    assert schema[0].startswith("Table name:")
