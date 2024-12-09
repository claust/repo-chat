from dotenv import load_dotenv
from langchain.agents import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages.base import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from typing import Annotated, List

from server.code_repo import CodeRepository

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


memory = MemorySaver()

# Tools
searchTool = DuckDuckGoSearchRun()
code_repo = CodeRepository()


@tool
def code_searcher(query: str) -> List[List[str]] | None:
    """ Searches the source code repository for the given query. """
    return code_repo.search(query)


tools = [searchTool, code_searcher]
tool_node = ToolNode(tools=tools)

# LLM
llm = ChatOpenAI(model="gpt-3.5-turbo")
llm_with_tools = llm.bind_tools(tools)
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an AI assistant that knows a lot about the DIMS code repository. 
                To answer the user's questions you will look up the code and the documentation provided by the tools.
                You will base your answers on the information you find.
                You can help with all code-related questions.
                """,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


def chatbot(state: State) -> dict[str, BaseMessage]:
    prompt = prompt_template.invoke(state)
    response = llm_with_tools.invoke(prompt)
    return {"messages": response}


# Graph
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

# Add edges
# graph_builder.add_edge(START, "chatbot")
graph_builder.set_entry_point("chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile(checkpointer=memory)

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
    try:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit", "q", "bye"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        user_input = "What do you know about Denmark?"
        print("User:", user_input)
        stream_graph_updates(user_input)
        break
