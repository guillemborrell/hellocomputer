from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState


from hellocomputer.config import settings
from hellocomputer.extraction import initial_intent_parser
from hellocomputer.models import AvailableModels
from hellocomputer.prompts import Prompts


async def intent(state: MessagesState):
    messages = state["messages"]
    query = messages[-1]
    llm = ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=AvailableModels.llama_small,
        temperature=0,
    )
    prompt = await Prompts.intent()
    chain = prompt | llm | initial_intent_parser

    return {"messages": [await chain.ainvoke({"query", query.content})]}


async def answer_general(state: MessagesState):
    llm = ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=AvailableModels.llama_small,
        temperature=0,
    )
    prompt = await Prompts.general()
    chain = prompt | llm

    return {"messages": [await chain.ainvoke({})]}


# async def answer_query(state: MessagesState):
#     llm = ChatOpenAI(
#         base_url=settings.llm_base_url,
#         api_key=settings.llm_api_key,
#         model=AvailableModels.llama_small,
#         temperature=0,
#     )
#     prompt = await Prompts.sql()
#     chain = prompt | llm
#
#     return {"messages": [await chain.ainvoke({})]}


async def answer_visualization(state: MessagesState):
    llm = ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=AvailableModels.llama_small,
        temperature=0,
    )
    prompt = await Prompts.visualization()
    chain = prompt | llm

    return {"messages": [await chain.ainvoke({})]}
