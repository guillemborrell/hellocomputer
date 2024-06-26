from pathlib import Path

import hellocomputer
import pytest
from hellocomputer.config import settings
from hellocomputer.db import StorageEngines
from hellocomputer.extraction import extract_code_block
from hellocomputer.models import Chat
from hellocomputer.db.sessions import SessionDB

TEST_STORAGE = StorageEngines.local
TEST_OUTPUT_FOLDER = Path(hellocomputer.__file__).parents[2] / "test" / "output"
TEST_XLS_PATH = (
    Path(hellocomputer.__file__).parents[2]
    / "test"
    / "data"
    / "TestExcelHelloComputer.xlsx"
)
SID = "test"


@pytest.mark.asyncio
@pytest.mark.skipif(
    settings.anyscale_api_key == "Awesome API", reason="API Key not set"
)
async def test_chat_simple():
    chat = Chat(api_key=settings.anyscale_api_key, temperature=0)
    chat = await chat.eval("Your're a helpful assistant", "Say literlly 'Hello'")
    assert chat.last_response_content() == "Hello!"


@pytest.mark.asyncio
@pytest.mark.skipif(
    settings.anyscale_api_key == "Awesome API", reason="API Key not set"
)
async def test_simple_data_query():
    query = "write a query that finds the average score of all students in the current database"

    chat = Chat(api_key=settings.anyscale_api_key, temperature=0.5)
    db = SessionDB(
        storage_engine=StorageEngines.local, path=TEST_XLS_PATH.parent, sid=SID
    ).load_xls(TEST_XLS_PATH)

    chat = await chat.eval("You're an expert sql developer", db.query_prompt(query))
    query = extract_code_block(chat.last_response_content())
    assert query.startswith("SELECT")


@pytest.mark.asyncio
@pytest.mark.skipif(
    settings.anyscale_api_key == "Awesome API", reason="API Key not set"
)
async def test_data_query():
    q = "find the average score of all the sudents"

    llm = Chat(api_key=settings.anyscale_api_key, temperature=0.5)
    db = SessionDB(
        storage_engine=TEST_STORAGE, path=TEST_OUTPUT_FOLDER, sid="test"
    ).load_folder()

    chat = await llm.eval("You're a DUCKDB expert", db.query_prompt(q))
    query = extract_code_block(chat.last_response_content())
    result = db.query(query).pl()

    assert result.shape[0] == 1
