import os
from dotenv import load_dotenv
from langchain.schema import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.func import START, END
from langgraph.graph.state import Command
from langgraph.graph import MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from typing import Literal, TypedDict


from server.agents import FileCategorizerAgent, FileSummarizerAgent, MethodNameSearcherAgent
from server.agents.method_documenter_agent import MethodDocumenterAgent


load_dotenv()

model = ChatOpenAI()
memory = MemorySaver()


class Router(TypedDict):
    next_agent: Literal["file_categorizer", "file_summarizer", "FINISH"]


def supervisor_system_prompt():
    return """You are a supervisor tasked with managing a team of four workers: a file_categorizer, a method_name_searcher, a method_documenter and a file_summarizer.
        Given the following text content, you will first ask the file categorizer to categorize the content.
        If it is not source code, you will finish.
        If it is source_code you will do these four steps: 
        1. Ask the method_name_searcher to search for method and function names in the content.
        2. For each of the found method names you will ask the method_documenter to document that particular method.
        3. Ask the file_summarizer to collect all the method documentations and add a summary.
        4. Respond with the final summary.
        When finished, you will respond with FINISH.
        """


# Agents
categorizer_agent = FileCategorizerAgent("file_categorizer", model)
summarizer_agent = FileSummarizerAgent("file_summarizer", model)
method_name_searcher_agent = MethodNameSearcherAgent(
    "method_name_searcher", model)
method_documenter_agent = MethodDocumenterAgent(
    "method_documenter", model)


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
builder.add_node(method_name_searcher_agent.name,
                 method_name_searcher_agent.invoke)
builder.add_node(method_documenter_agent.name, method_documenter_agent.invoke)

# Add edges
builder.add_edge(START, "supervisor")

graph = builder.compile(checkpointer=memory)

config: RunnableConfig = {"configurable":  {"thread_id": "1"}}


def stream_graph_updates(user_input: str) -> None:
    for event in graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values"):
        last_message = event["messages"][-1]
        last_message.pretty_print()


while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit", "q", "bye"]:
        print("Goodbye!")
        break
    stream_graph_updates(user_input)

os._exit(0)
