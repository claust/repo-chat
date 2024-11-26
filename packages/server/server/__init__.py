import getpass
import os

def _set_env(var: str):
  if not os.environ.get(var):
    os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
  messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo")

def chatbot(state: State):
  return {"messages": llm.invoke(state["messages"])}

# Add nodes
graph_builder.add_node("chatbot", chatbot)

# Add edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

def stream_graph_updates(user_input: str):
  for event in graph.stream({"messages": [("user", user_input)]}):
    for value in event.values():
      print("Assistant:", value["messages"][-1].content)

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


