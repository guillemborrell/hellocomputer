from typing import Literal

from langgraph.graph import END, START, MessagesState, StateGraph

from hellocomputer.nodes import (
    intent,
    answer_general,
    answer_query,
    answer_visualization,
)


def route_intent(state: MessagesState) -> Literal["general", "query", "visualization"]:
    messages = state["messages"]
    last_message = messages[-1]
    return last_message.content


workflow = StateGraph(MessagesState)

# Nodes

workflow.add_node("intent", intent)
workflow.add_node("answer_general", answer_general)
workflow.add_node("answer_query", answer_query)
workflow.add_node("answer_visualization", answer_visualization)

# Edges

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
