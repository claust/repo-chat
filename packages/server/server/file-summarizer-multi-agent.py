import os
from dotenv import load_dotenv
from langchain.schema import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.func import START, END
from langgraph.graph.state import Command
from langgraph.graph import MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from typing import Literal, LiteralString, TypedDict

from server.agents import FileCategorizerAgent, FileSummarizerAgent

load_dotenv()

model = ChatOpenAI()
memory = MemorySaver()


class Router(TypedDict):
    next_agent: Literal["file_categorizer", "file_summarizer", "FINISH"]


def supervisor_system_prompt() -> LiteralString:
    return """You are a supervisor tasked with managing a conversation between two workers: a file_categorizer and a file_summarizer.
        Given the following text content, you will first ask the file categorizer to categorize the content.
        If it is source_code you will ask the file_summarizer to summarize the content.
        Otherwise you will finish.
        When finished, you will respond with FINISH.
        """


# Agents
categorizer_agent = FileCategorizerAgent("file_categorizer", model)
summarizer_agent = FileSummarizerAgent("file_summarizer", model)


def supervisor(state: MessagesState) -> Command[Literal["file_summarizer", "__end__"]]:
    messages = [
        SystemMessage(
            content=supervisor_system_prompt()),
    ] + state["messages"]
    response = model.with_structured_output(Router).invoke(messages)

    goto = response["next_agent"]
    if goto == "FINISH":
        goto = END
    return Command(goto=goto)


# LLM
model = ChatOpenAI(model="gpt-3.5-turbo")

# Setup graph
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("supervisor", supervisor)
builder.add_node(categorizer_agent.name, categorizer_agent.invoke)
builder.add_node(summarizer_agent.name, summarizer_agent.invoke)

# Add edges
builder.add_edge(START, "supervisor")

graph = builder.compile(checkpointer=memory)

config: RunnableConfig = {"configurable":  {"thread_id": "1"}}


def stream_graph_updates(user_input: str) -> None:
    for event in graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values"):
        for value in event["messages"]:
            if isinstance(value, list):
                message = value[-1]
            else:
                message = value
            # print("Assistant:", message)
            message.pretty_print()


while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit", "q", "bye"]:
        print("Goodbye!")
        break
    stream_graph_updates(user_input)

os._exit(0)
