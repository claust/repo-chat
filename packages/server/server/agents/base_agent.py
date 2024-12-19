
from abc import ABC, abstractmethod

from langchain.schema import AIMessage
from langchain_core.language_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph
from langgraph.graph.state import Command
from langgraph.prebuilt import create_react_agent


class BaseAgent(ABC):
    def __init__(self, name: str, model: BaseChatModel) -> None:
        self.name = name
        self.model = model
        self.agent = create_react_agent(
            self.model,
            self.tools,
            state_modifier=self.system_prompt,
        )

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        pass

    @property
    @abstractmethod
    def tools(self) -> list:
        pass

    def invoke(self, state) -> dict:
        response = self.agent.invoke(state)
        return Command(
            goto="supervisor",
            update={"messages": [AIMessage(
                content=response["messages"][-1].content, name=self.name)]}
        )
