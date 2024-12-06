from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from typing import Annotated

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


memory = MemorySaver()

# Tools
searchTool = DuckDuckGoSearchRun()
# result = searchTool.invoke("Ballerupcentrets åbningstider?")
tools = [searchTool]
tool_node = ToolNode(tools=tools)

# LLM
llm = ChatOpenAI(model="gpt-3.5-turbo")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": llm_with_tools.invoke(state["messages"])}


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

config = {"configurable":  {"thread_id": "1"}}


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values"):
        for value in event["messages"]:
            # messages = value["messages"]
            if isinstance(value, list):
                message = value[-1]
            else:
                message = value
            print("Assistant:", message.pretty_print())


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        user_input = "What do you know about Denmark?"
        print("User:", user_input)
        stream_graph_updates(user_input)
        break
