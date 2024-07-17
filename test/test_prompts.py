import pytest
from hellocomputer.models import Prompts
from langchain.prompts import PromptTemplate


@pytest.mark.asyncio
async def test_get_general_prompt():
    general: str = await Prompts.general()
    assert general.startswith("You're a helpful assistant")


@pytest.mark.asyncio
async def test_general_templated():
    prompt = PromptTemplate.from_template(await Prompts.general())
    assert "Do as I say" in prompt.format(query="Do as I say")
