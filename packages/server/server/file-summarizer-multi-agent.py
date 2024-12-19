import os
from dotenv import load_dotenv
from langchain.schema import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.func import START, END
from langgraph.graph.state import Command
from langgraph.graph import MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from typing import Literal, TypedDict

from langgraph.prebuilt import create_react_agent

load_dotenv()

model = ChatOpenAI()
memory = MemorySaver()


class Router(TypedDict):
    next_agent: Literal["file_categorizer", "file_summarizer", "FINISH"]


def supervisor_system_prompt():
    return """You are a supervisor tasked with managing a conversation between two workers: a file_categorizer and a file_summarizer.
        Given the following text content, you will first ask the file categorizer to categorize the content.
        If it is source_code you will ask the file_summarizer to summarize the content.
        Otherwise you will finish.
        When finished, you will respond with FINISH.
        """


def file_categorizer_system_prompt():
    return """You are an expert programmer specialised in deciding if content is source code or configuration or something else.
        If it source code, you will respond with source_code.
        If it is configuration, you will respond with configuration_file.
        Otherwise, you will respond with something_else.
        """


def summerizer_system_prompt():
    return """You are an expert programmer specialised in analyzing source code.
        You will read the following source code and extract the exported public classes, interfaces etc. from the file.
        You will respond with a list of the exported public classes, interfaces including their exact method signatures. 
        """


# Agents
categorizer_agent = create_react_agent(
    model,
    [],
    state_modifier=file_categorizer_system_prompt()
)
summarizer_agent = create_react_agent(
    model,
    [],
    state_modifier=summerizer_system_prompt()
)


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


def file_categorizer(state: MessagesState) -> Command[Literal["supervisor"]]:
    response = categorizer_agent.invoke(state)
    return Command(
        goto="supervisor",
        update={"messages": [AIMessage(
            content=response["messages"][-1].content, name="file_categorizer")]}
    )


def file_summarizer(state: MessagesState) -> Command[Literal["supervisor"]]:
    response = summarizer_agent.invoke(state)
    return Command(
        goto="supervisor",
        update={"messages": [AIMessage(
            content=response["messages"][-1].content, name="file_summarizer")]}
    )


# LLM
model = ChatOpenAI(model="gpt-3.5-turbo")

# Setup graph
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("supervisor", supervisor)
builder.add_node("file_categorizer", file_categorizer)
builder.add_node("file_summarizer", file_summarizer)

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
