from enum import StrEnum
from pathlib import Path

from anyio import open_file
from langchain_core.prompts import PromptTemplate
from langchain_fireworks import Fireworks

import hellocomputer

PROMPT_DIR = Path(hellocomputer.__file__).parent / "prompts"


class AvailableModels(StrEnum):
    llama3_70b = "accounts/fireworks/models/llama-v3-70b-instruct"
    # Function calling model
    mixtral_8x7b = "accounts/fireworks/models/mixtral-8x7b-instruct"
    mixtral_8x22b = "accounts/fireworks/models/mixtral-8x22b-instruct"
    firefunction_2 = "accounts/fireworks/models/firefunction-v2"


class Prompts:
    @classmethod
    async def getter(cls, name):
        async with await open_file(PROMPT_DIR / f"{name}.md") as f:
            return await f.read()

    @classmethod
    async def general(cls):
        return await cls.getter("general_prompt")

    @classmethod
    async def sql(cls):
        return await cls.getter("sql_prompt")


class Chat:
    @staticmethod
    def raise_no_key(api_key):
        if api_key:
            return api_key
        elif api_key is None:
            raise ValueError(
                "You need to provide a valid API in the api_key init argument"
            )
        else:
            raise ValueError("You need to provide a valid API key")

    def __init__(
        self,
        model: AvailableModels = AvailableModels.mixtral_8x7b,
        api_key: str = "",
        temperature: float = 0.5,
    ):
        self.model = model
        self.api_key = self.raise_no_key(api_key)
        self.messages = []
        self.responses = []

        self.model: Fireworks = Fireworks(
            model=model, temperature=temperature, api_key=self.api_key
        )

    async def eval(self, task):
        prompt = PromptTemplate.from_template(await Prompts.general())

        response = await self.model.ainvoke(prompt.format(query=task))
        self.responses.append(response)
        return self

    async def sql_eval(self, question):
        prompt = PromptTemplate.from_template(await Prompts.sql())

        response = await self.model.ainvoke(prompt.format(query=question))
        self.responses.append(response)
        return self

    def last_response_content(self):
        last_response = self.responses[-1]
        return last_response

    def last_response_metadata(self):
        return self.responses[-1].response_metadata
