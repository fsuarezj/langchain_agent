from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import AnyMessage, add_messages

from langchain_openai import ChatOpenAI

from global_conf import GPT_MODEL

load_dotenv()

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

graph_builder = StateGraph(State)

llm = ChatOpenAI(model=GPT_MODEL)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

graph = graph_builder.compile()

print(graph.get_graph().draw_ascii())

stateMessages = State()
stateMessages["messages"] = []
while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q", "bye"]:
        print("Goodbye!")
        break
    messages = stateMessages["messages"] + [("user", user_input)]
    stateMessages = {**stateMessages, "messages": messages}
    for event in graph.stream(stateMessages):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
            messages = stateMessages["messages"] + [("assistant", value["messages"][-1].content)]
            stateMessages = {**stateMessages, "messages": messages}
