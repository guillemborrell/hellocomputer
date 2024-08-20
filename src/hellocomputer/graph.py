from typing import Literal
from langgraph.graph import END, START, StateGraph


from hellocomputer.nodes import (
    intent,
    answer_general,
    answer_visualization,
)

from hellocomputer.tools import extract_sid
from hellocomputer.tools.db import SQLSubgraph
from hellocomputer.db.sessions import SessionDB
from hellocomputer.state import SidState


def route_intent(state: SidState) -> Literal["general", "query", "visualization"]:
    messages = state["messages"]
    last_message = messages[-1]
    return last_message.content


def get_sid(state: SidState) -> Literal["ok"]:
    print(state["messages"])
    last_message = state["messages"][-1]
    sid = extract_sid(last_message)
    state.sid = SessionDB(sid)


sql_subgraph = SQLSubgraph()

workflow = StateGraph(SidState)

# Nodes

workflow.add_node("intent", intent)
workflow.add_node("answer_general", answer_general)
workflow.add_node("answer_visualization", answer_visualization)

# Edges
workflow.add_edge(START, "intent")
workflow.add_conditional_edges(
    "intent",
    route_intent,
    {
        "general": "answer_general",
        "query": sql_subgraph.start_node,
        "visualization": "answer_visualization",
    },
)
workflow.add_edge("answer_general", END)
workflow.add_edge("answer_visualization", END)

# SQL Subgraph

workflow = sql_subgraph.add_nodes_edges(
    workflow=workflow, origin="intent", destination=END
)

app = workflow.compile()
