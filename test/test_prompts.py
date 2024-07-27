import pytest
from hellocomputer.prompts import Prompts
from langchain.prompts import PromptTemplate


@pytest.mark.asyncio
async def test_get_general_prompt():
    general: PromptTemplate = await Prompts.general()
    assert general.format(query="whatever").startswith(
        "You've been asked to do a task you can't do"
    )
