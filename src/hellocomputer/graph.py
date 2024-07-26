from typing import Literal

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph

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


def route_intent(state: MessagesState) -> Literal["general", "query", "visualization"]:
    messages = state["messages"]
    last_message = messages[-1]
    return last_message.content


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


async def answer_query(state: MessagesState):
    llm = ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=AvailableModels.llama_small,
        temperature=0,
    )
    prompt = await Prompts.sql()
    chain = prompt | llm

    return {"messages": [await chain.ainvoke({})]}


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


workflow = StateGraph(MessagesState)

workflow.add_node("intent", intent)
workflow.add_node("answer_general", answer_general)
workflow.add_node("answer_query", answer_query)
workflow.add_node("answer_visualization", answer_visualization)

workflow.add_edge(START, "intent")
workflow.add_conditional_edges(
    "intent",
    route_intent,
    {
        "general": "answer_general",
        "query": "answer_query",
        "visualization": "answer_visualization",
    },
)
workflow.add_edge("answer_general", END)
workflow.add_edge("answer_query", END)
workflow.add_edge("answer_visualization", END)

app = workflow.compile()
