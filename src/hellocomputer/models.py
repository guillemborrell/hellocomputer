from enum import StrEnum
from langchain_community.chat_models import ChatAnyscale
from langchain_core.messages import HumanMessage, SystemMessage


class AvailableModels(StrEnum):
    llama3_8b = "meta-llama/Meta-Llama-3-8B-Instruct"
    llama3_70b = "meta-llama/Meta-Llama-3-70B-Instruct"
    # Function calling model
    mixtral_8x7b = "mistralai/Mixtral-8x7B-Instruct-v0.1"


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
        model: AvailableModels = AvailableModels.llama3_8b,
        api_key: str = "",
        temperature: float = 0.5,
    ):
        self.model_name = model
        self.api_key = self.raise_no_key(api_key)
        self.messages = []
        self.responses = []

        self.model: ChatAnyscale = ChatAnyscale(
            model_name=model, temperature=temperature, anyscale_api_key=self.api_key
        )

    async def eval(self, system: str, human: str):
        self.messages.append(
            [
                SystemMessage(content=system),
                HumanMessage(content=human),
            ]
        )

        response = await self.model.ainvoke(self.messages[-1])
        self.responses.append(response)
        return self

    def last_response_content(self):
        return self.responses[-1].content

    def last_response_metadata(self):
        return self.responses[-1].response_metadata
