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
