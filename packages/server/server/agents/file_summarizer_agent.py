

from typing import LiteralString
from server.agents import BaseAgent


class FileSummarizerAgent(BaseAgent):

    @property
    def system_prompt(self) -> LiteralString:
        return """You are an expert techical writer specialized in summarizing the content of a source code file.
            You will read the following descriptions of the methods and function in the source code file.
            You will summarize the purpose of source code file, based on the descriptions of its methods and functions.
            You will respond with the full summary and all the descriptions of the functions and methods.
            """

    @property
    def tools(self) -> list:
        return []
