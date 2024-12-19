

from typing import LiteralString

from server.agents import BaseAgent


class FileCategorizerAgent(BaseAgent):

    @property
    def system_prompt(self) -> LiteralString:
        return """You are an expert programmer specialised in deciding if content is source code or configuration or something else.
            If it source code, you will respond with source_code.
            If it is configuration, you will respond with configuration_file.
            Otherwise, you will respond with something_else.
 
            """

    @property
    def tools(self) -> list:
        return []
