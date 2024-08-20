from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from hellocomputer.db.sessions import SessionDB


class SidState(TypedDict):
    messages: Annotated[list, add_messages]
    sid: SessionDB
