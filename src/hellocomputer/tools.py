from pydantic import BaseModel, Field
from typing import Type
from langchain.tools import BaseTool
from hellocomputer.db.sessions import SessionDB
from hellocomputer.config import settings


class DuckdbQueryInput(BaseModel):
    query: str = Field(description="Question to be translated to a SQL statement")
    session_id: str = Field(description="Session ID necessary to fetch the data")


class DuckdbQueryTool(BaseTool):
    name: str = "Calculator"
    description: str = "Tool to evaluate mathemetical expressions"
    args_schema: Type[BaseModel] = DuckdbQueryInput

    def _run(self, query: str, session_id: str) -> str:
        """Run the query"""
        db = SessionDB(settings, session_id)
        return "Table"

    async def _arun(self, query: str, session_id: str) -> str:
        """Use the tool asynchronously."""
        db = SessionDB(settings, session_id)
        return "Table"
