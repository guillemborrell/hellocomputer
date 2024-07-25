from anyio import open_file
from langchain_core.prompts import PromptTemplate
from pathlib import Path

import hellocomputer

PROMPT_DIR = Path(hellocomputer.__file__).parent / "prompts"


class Prompts:
    @classmethod
    async def getter(cls, name):
        async with await open_file(PROMPT_DIR / f"{name}.md") as f:
            return await f.read()

    @classmethod
    async def intent(cls):
        return PromptTemplate.from_template(await cls.getter("intent"))

    @classmethod
    async def general(cls):
        return PromptTemplate.from_template(await cls.getter("general_prompt"))

    @classmethod
    async def sql(cls):
        return PromptTemplate.from_template(await cls.getter("sql_prompt"))
