from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import AnyMessage, add_messages

from langchain_openai import ChatOpenAI

from global_conf import GPT_MODEL
from Assistants.simple_assistant import State, primary_assistant_prompt, tools1, SimpleAssistant

load_dotenv()

graph_builder = StateGraph(State)

llm = ChatOpenAI(model=GPT_MODEL)

tools1_assistante_runnable = primary_assistant_prompt | llm.bind_tools(tools1)

#def chatbot(state: State):
#    return {"messages": [llm.invoke(state["messages"])]}

#graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("assistant", SimpleAssistant(tools1_assistante_runnable))
graph_builder.add_node("tools", )

graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

graph = graph_builder.compile()

print(graph.get_graph().draw_ascii())

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q", "bye"]:
        print("Goodbye!")
        break
    for event in graph.stream({"messages": ("user", user_input)}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)