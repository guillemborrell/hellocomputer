from pathlib import Path

import hellocomputer
import pytest
from hellocomputer.analytics import DDB, StorageEngines
from hellocomputer.config import settings
from hellocomputer.extraction import extract_code_block
from hellocomputer.models import Chat

TEST_XLS_PATH = (
    Path(hellocomputer.__file__).parents[2]
    / "test"
    / "data"
    / "TestExcelHelloComputer.xlsx"
)


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
    db = DDB(storage_engine=StorageEngines.local, path=TEST_XLS_PATH.parent).load_xls(
        TEST_XLS_PATH
    )

    chat = await chat.eval("You're an expert sql developer", db.query_prompt(query))
    query = extract_code_block(chat.last_response_content())
    assert query.startswith("SELECT")
