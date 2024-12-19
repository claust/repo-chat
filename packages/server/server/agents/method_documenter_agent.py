

from typing import LiteralString

from server.agents import BaseAgent


class MethodDocumenterAgent(BaseAgent):

    @property
    def system_prompt(self) -> LiteralString:
        return """You are an expert programmer specialised in analyzing source code and methods and functions.
            You will read the following source code and the provided method or function named.
            You will document the mentionend method or function by writing a summary of the purpose of the method.
            You will respond with the documentation.
            """

    @property
    def tools(self) -> list:
        return []
