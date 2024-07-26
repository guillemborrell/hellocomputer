from pathlib import Path

import hellocomputer
import pytest
from hellocomputer.config import Settings, StorageEngines
from hellocomputer.db.sessions import SessionDB
from hellocomputer.models import AvailableModels
from hellocomputer.prompts import Prompts
from hellocomputer.extraction import initial_intent_parser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

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

SID = "test"


@pytest.mark.asyncio
@pytest.mark.skipif(settings.llm_api_key == "Awesome API", reason="API Key not set")
async def test_chat_simple():
    llm = ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=AvailableModels.mixtral_8x7b,
        temperature=0.5,
    )
    prompt = ChatPromptTemplate.from_template(
        """Say literally {word}, a single word. Don't be verbose, 
        I'll be disappointed if you say more than a single word"""
    )
    chain = prompt | llm
    response = await chain.ainvoke({"word": "Hello"})

    assert "hello" in response.content.lower()


@pytest.mark.asyncio
@pytest.mark.skipif(settings.llm_api_key == "Awesome API", reason="API Key not set")
async def test_query_context():
    db = SessionDB(settings, sid=SID).load_xls(TEST_XLS_PATH).llmsql

    llm = ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=AvailableModels.mixtral_8x7b,
        temperature=0.5,
    )

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    context = toolkit.get_context()
    assert "table_info" in context
    assert "table_names" in context


@pytest.mark.asyncio
@pytest.mark.skipif(settings.llm_api_key == "Awesome API", reason="API Key not set")
async def test_initial_intent():
    llm = ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=AvailableModels.llama_small,
        temperature=0,
    )
    prompt = await Prompts.intent()
    chain = prompt | llm | initial_intent_parser

    response = await chain.ainvoke({"query", "Make me a sandwich"})
    assert response == "general"

    response = await chain.ainvoke(
        {"query", "Which is the average score of all the students"}
    )
    assert response == "query"


#
#     chat = await chat.sql_eval(db.query_prompt(query))
#     query = extract_code_block(chat.last_response_content())
#     assert query.startswith("SELECT")
#
#
# @pytest.mark.asyncio
# @pytest.mark.skipif(settings.llm_api_key == "Awesome API", reason="API Key not set")
# async def test_data_query():
#     q = "Find the average score of all the sudents"
#
#     llm = Chat(
#         api_key=settings.llm_api_key,
#         temperature=0.5,
#     )
#     db = SessionDB(
#         storage_engine=TEST_STORAGE, path=TEST_OUTPUT_FOLDER, sid="test"
#     ).load_folder()
#
#     chat = await llm.sql_eval(db.query_prompt(q))
#     query = extract_code_block(chat.last_response_content())
#     result: pl.DataFrame = db.query(query).pl()
#
#     assert result.shape[0] == 1
#     assert result.select([pl.col("avg(Score)")]).to_series()[0] == 0.5
#
