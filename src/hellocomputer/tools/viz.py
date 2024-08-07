from langchain.tools import BaseTool
from pydantic import BaseModel, Field


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
