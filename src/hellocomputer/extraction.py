import re
from enum import StrEnum

from langchain.output_parsers.enum import EnumOutputParser


def extract_code_block(response):
    # python regex to extract markdown clode block contained in the response string
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    if len(matches) > 1:
        raise ValueError("More than one code block")
    return matches[0].removeprefix("sql").removeprefix("\n")


class InitialIntent(StrEnum):
    general = "general"
    query = "query"
    visualization = "visualization"


initial_intent_parser = EnumOutputParser(enum=InitialIntent)
