import pytest
import os
import hellocomputer
from hellocomputer.config import settings
from hellocomputer.models import Chat
from hellocomputer.extraction import extract_code_block
from pathlib import Path
from hellocomputer.analytics import DDB


TEST_OUTPUT_FOLDER = Path(hellocomputer.__file__).parents[2] / "test" / "output"


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
    db = DDB().load_folder_local(TEST_OUTPUT_FOLDER)

    prompt = os.linesep.join(
        [
            query,
            db.db_schema(),
            db.load_description_local(TEST_OUTPUT_FOLDER),
            "Return just the SQL statement",
        ]
    )

    chat = await chat.eval("You're an expert sql developer", prompt)
    query = extract_code_block(chat.last_response_content())
    assert query.startswith("SELECT")
