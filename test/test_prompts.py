import pytest
from hellocomputer.prompts import Prompts
from langchain.prompts import PromptTemplate


@pytest.mark.asyncio
async def test_get_general_prompt():
    general: PromptTemplate = await Prompts.general()
    assert general.format(query="whatever").startswith("You're a helpful assistant")
