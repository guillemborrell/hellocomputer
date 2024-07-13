from enum import StrEnum

from langchain_core.prompts import PromptTemplate
from langchain_fireworks import Fireworks


class AvailableModels(StrEnum):
    llama3_70b = "accounts/fireworks/models/llama-v3-70b-instruct"
    # Function calling model
    mixtral_8x7b = "accounts/fireworks/models/mixtral-8x7b-instruct"
    mixtral_8x22b = "accounts/fireworks/models/mixtral-8x22b-instruct"
    firefunction_2 = "accounts/fireworks/models/firefunction-v2"


general_prompt = """
You're a helpful assistant. Perform the following tasks:

----
{query}
----
"""

sql_prompt = """
You're a SQL expert. Write a query using the duckdb dialect. The goal of the query is the following:

----
{query}
----

Return only the sql statement without any additional text.
"""


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
        prompt = PromptTemplate.from_template(general_prompt)

        response = await self.model.ainvoke(prompt.format(query=task))
        self.responses.append(response)
        return self

    async def sql_eval(self, question):
        prompt = PromptTemplate.from_template(sql_prompt)

        response = await self.model.ainvoke(prompt.format(query=question))
        self.responses.append(response)
        return self

    def last_response_content(self):
        last_response = self.responses[-1]
        return last_response

    def last_response_metadata(self):
        return self.responses[-1].response_metadata
