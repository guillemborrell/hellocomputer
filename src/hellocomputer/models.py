from enum import StrEnum
from pathlib import Path

from anyio import open_file
from langchain_core.prompts import PromptTemplate

import hellocomputer

PROMPT_DIR = Path(hellocomputer.__file__).parent / "prompts"


class AvailableModels(StrEnum):
    llama_small = "accounts/fireworks/models/llama-v3p1-8b-instruct"
    llama_medium = "accounts/fireworks/models/llama-v3p1-70b-instruct"
    llama_large = "accounts/fireworks/models/llama-v3p1-405b-instruct"
    # Function calling models
    mixtral_8x7b = "accounts/fireworks/models/mixtral-8x7b-instruct"
    mixtral_8x22b = "accounts/fireworks/models/mixtral-8x22b-instruct"
    firefunction_2 = "accounts/fireworks/models/firefunction-v2"


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
