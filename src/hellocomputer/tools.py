from typing import Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from hellocomputer.config import settings
from hellocomputer.db.sessions import SessionDB


class DuckdbQueryInput(BaseModel):
    query: str = Field(description="Question to be translated to a SQL statement")
    session_id: str = Field(description="Session ID necessary to fetch the data")


class DuckdbQueryTool(BaseTool):
    name: str = "sql_query"
    description: str = "Run a SQL query in the database containing all the datasets "
    "and provide a summary of the results"
    args_schema: Type[BaseModel] = DuckdbQueryInput

    def _run(self, query: str, session_id: str) -> str:
        """Run the query"""
        db = SessionDB(settings, session_id)

    async def _arun(self, query: str, session_id: str) -> str:
        """Use the tool asynchronously."""
        db = SessionDB(settings, session_id)
        return "Table"


class PlotHistogramInput(BaseModel):
    column_name: str = Field(description="Name of the column containing the values")
    table_name: str = Field(description="Name of the table that contains the data")
    num_bins: int = Field(description="Number of bins of the histogram")


class PlotHistogramTool(BaseTool):
    name: str = "plot_histogram"
    description: str = """
    Generate a histogram plot given a name of an existing table of the database, 
    and a name of a column in the table. The default number of bins is 10, but 
    you can forward the number of bins if you are requested to"""
