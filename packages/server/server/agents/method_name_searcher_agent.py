

from typing import LiteralString

from server.agents import BaseAgent


class MethodNameSearcherAgent(BaseAgent):

    @property
    def system_prompt(self) -> LiteralString:
        return """You are an expert programmer specialised in analyzing source code and extracting method and function names.
            You will read the following source code and extract the method and function names from the file.
            You will respond with a list of the method and function names including their exact method signatures. 
            """

    @property
    def tools(self) -> list:
        return []
