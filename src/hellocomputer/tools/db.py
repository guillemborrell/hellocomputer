from typing import Type, Literal

from langchain.tools import BaseTool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from hellocomputer.config import settings
from hellocomputer.state import SidState
from hellocomputer.db.sessions import SessionDB
from hellocomputer.models import AvailableModels


## This in case I need to create more ReAct agents


class DuckdbQueryInput(BaseModel):
    query: str = Field(description="Question to be translated to a SQL statement")
    session_id: str = Field(description="Session ID necessary to fetch the data")


class DuckdbQueryTool(BaseTool):
    name: str = "sql_query"
    description: str = "Run a SQL query in the database containing all the datasets "
    "and provide a summary of the results, and the name of the table with them if the "
    "volume of the results is large"
    args_schema: Type[BaseModel] = DuckdbQueryInput

    def _run(self, query: str, session_id: str) -> str:
        """Run the query"""
        session = SessionDB(settings, session_id)
        session.db.sql(query)

    async def _arun(self, query: str, session_id: str) -> str:
        """Use the tool asynchronously."""
        session = SessionDB(settings, session_id)
        session.db.sql(query)
        return "Table"


class SQLSubgraph:
    """
    Creates the question-answering agent that generates and runs SQL
    queries
    """

    @property
    def start_node(self):
        return "sql_agent"

    async def call_model(self, state: SidState):
        db = SessionDB(settings=settings).set_session(state.sid)
        sql_toolkit = db.sql_toolkit

        agent_llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=AvailableModels.firefunction_2,
            temperature=0.5,
            max_tokens=256,
        ).bind_tools(sql_toolkit.get_tools())

        messages = state["messages"]
        response = agent_llm.ainvoke(messages)
        return {"messages": [response]}

    @property
    def query_tool_node(self) -> ToolNode:
        db = SessionDB(settings=settings)
        sql_toolkit = db.sql_toolkit
        return ToolNode(sql_toolkit.get_tools())

    def add_nodes_edges(
        self, workflow: StateGraph, origin: str, destination: str
    ) -> StateGraph:
        """Creates the nodes and edges of the subgraph given a workflow

        Args:
            workflow (StateGraph): Workflow that will get nodes and edges added
            origin (str): Origin node
            destination (str): Destination node

        Returns:
            StateGraph: Resulting workflow
        """

        def should_continue(state: SidState):
            messages = state["messages"]
            last_message = messages[-1]
            if last_message.tool_calls:
                return destination
            return "__end__"

        workflow.add_node("sql_agent", self.call_model)
        workflow.add_node("sql_tool_node", self.query_tool_node)
        workflow.add_edge(origin, "sql_agent")
        workflow.add_conditional_edges("sql_agent", should_continue)
        workflow.add_edge("sql_agent", "sql_tool_node")

        return workflow
