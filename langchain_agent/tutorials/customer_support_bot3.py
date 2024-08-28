
from dotenv import load_dotenv

from langchain_core.runnables import RunnableLambda
from langchain_core.messages import ToolMessage, HumanMessage

from langgraph.prebuilt import ToolNode

from .tools_travel_example import fetch_user_flight_information, search_flights, lookup_policy, update_ticket_to_new_flight, cancel_ticket, search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental, search_hotels, book_hotel, update_hotel, cancel_hotel, search_trip_recommendations, book_excursion, update_excursion, cancel_excursion
from ..assistants.assistance_interface import AssistantInterface

load_dotenv()
local_file = "travel2.sqlite"
db = local_file
backup_file = "travel2.backup.sqlite"

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print(f"Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)

########### State ###########

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph.message import AnyMessage, add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str

############## Agent ##############
from langchain_openai import ChatOpenAI
from langchain_community.tools. tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from datetime import datetime

from ..global_conf import GPT_MODEL

class Assistant:
    def __init__(self, runnable: Runnable) -> None:
        self.runnable = runnable
    
    def __call__(self, state: State, config: RunnableConfig):
        while True:
            passenger_id = config.get("passenger_id", None)
            result = self.runnable.invoke(state)
            if not result.tool_calls and (
                not result.content or isinstance(result.content, list) and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

llm = ChatOpenAI(model=GPT_MODEL)

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful customer support assistant for Swiss Airlines. "
            " Use the provided tools to search for flights, company policies, and other information to assist the user's queries. "
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            " If a search comes up empty, expand your search before giving up."
            "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
#).partial(time=datetime.now())
).partial(time=datetime(2024,4,1))

safe_tools = [
    TavilySearchResults(max_results=1),
    fetch_user_flight_information,
    search_flights,
    lookup_policy,
    search_car_rentals,
    search_hotels,
    search_trip_recommendations,
]

sensivite_tools = [
    update_ticket_to_new_flight,
    cancel_ticket,
    book_car_rental,
    update_car_rental,
    cancel_car_rental,
    book_hotel,
    update_hotel,
    cancel_hotel,
    book_excursion,
    update_excursion,
    cancel_excursion,
]

sensivite_tools_names = {t.name for t in sensivite_tools}

assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    safe_tools + sensivite_tools
)

############# Define Graph ############
from typing import Literal
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

builder = StateGraph(State)

def user_info(state: State):
    return {"user_info": fetch_user_flight_information.invoke({})}

builder.add_node("fetch_user_info", user_info)
builder.add_node("assistant", Assistant(assistant_runnable))
builder.add_node("safe_tools", create_tool_node_with_fallback(safe_tools))
builder.add_node("sensitive_tools", create_tool_node_with_fallback(sensivite_tools))

builder.set_entry_point("fetch_user_info")
builder.add_edge("fetch_user_info", "assistant")

def route_tools(state: State) -> Literal["safe_tools", "sensitive_tools", "__end__"]:
    next_node = tools_condition(state)
    if next_node == END:
        return END
    ai_message = state["messages"][-1]
    first_tool_call = ai_message.tool_calls[0]
    if first_tool_call["name"] in sensivite_tools_names:
        return "sensitive_tools"
    return "safe_tools"


builder.add_conditional_edges(
    "assistant",
    route_tools
)

builder.add_edge("safe_tools", "assistant")
builder.add_edge("sensitive_tools", "assistant")

memory = SqliteSaver.from_conn_string(":memory:")
graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["sensitive_tools"]
)

print(graph.get_graph().draw_ascii())

from IPython.display import Image, display

try:
    display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
except:
    # This requires some extra dependencies and is optional
    pass

############## Run Agent ##############
import shutil
import uuid

# Let's create an example conversation a user might have with the assistant
tutorial_questions = [
    "Hi there, what time is my flight?",
    "Am i allowed to update my flight to something sooner? I want to leave later today.",
    "Update my flight to sometime next week then",
    "The next available option is great",
    "what about lodging and transportation?",
    "Yeah i think i'd like an affordable hotel for my week-long stay (7 days). And I'll want to rent a car.",
    "OK could you place a reservation for your recommended hotel? It sounds nice.",
    "yes go ahead and book anything that's moderate expense and has availability.",
    "Now for a car, what are my options?",
    "Awesome let's just get the cheapest option. Go ahead and book for 7 days",
    "Cool so now what recommendations do you have on excursions?",
    "Are they available while I'm there?",
    "interesting - i like the museums, what options are there? ",
    "OK great pick one and book it for my second day there.",
]

# Update with the backup file so we can restart from the original place in each section
shutil.copy(backup_file, db)
thread_id = str(uuid.uuid4())

config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information
        "passenger_id": "3442 587242",
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}

def term_io():
    _printed = set()
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q", "bye"]:
            print("Goodbye!")
            break
        events = graph.stream(
            {"messages": ("user", user_input)}, config, stream_mode="values"
        )
        for event in events:
            _print_event(event, _printed)
        snapshot = graph.get_state(config)
        while snapshot.next:
            user_input = input(
                "Do you approve of the above actions? Type 'y' to continue;"
                " otherwise, explain your requested changed.\n\n"
            )
            if user_input.strip() == "y":
                # Just continue
                result = graph.invoke(None, config)
            else:
                # Satisfy the tool invocation by
                # providing instructions on the requested changes / change of mind
                result = graph.invoke(
                    {
                        "messages": [
                            ToolMessage(
                                tool_call_id=event["messages"][-1].tool_calls[0]["id"],
                                content=f"API call denied by user. Reasoning: '{user_input}'. Continue assisting, accounting for the user's input.",
                            )
                        ]
                    },
                    config,
                )
            snapshot = graph.get_state(config)
    #for question in tutorial_questions:
    #    events = graph.stream(
    #        {"messages": ("user", question)}, config, stream_mode="values"
    #    )
    #    for event in events:
    #        _print_event(event, _printed)

class SupportBotIO3(AssistantInterface):
    def __init__(self):
        self._graph = graph
        self._unthemed_diagram = []
        self._set_diagram()
    
    def _pretty_message(self, event, graph_state):
        result = ""
        message = event.get("messages")
        if isinstance(message, list):
            message = message[-1]
        msg_repr = message.pretty_repr(html=False)
        if not isinstance(message, HumanMessage):
            result += "================================= State: "
            result += graph_state
            result += ' =================================\n\r'
            result += msg_repr
            result += '\n\r'
            #yield f":red[{message.content}]\n\r"
        return result
    
    def _set_diagram(self, active = "__start__"):
        diagram = self._graph.get_graph().draw_mermaid()
        diagram = diagram.splitlines()
        theme = "%%{init: {'theme':'base'}}%%"
        diagram[0] = theme
        diagram = diagram[:-3]
        diagram.append("\tclassDef default fill:#EEE,stroke:#000,stroke-width:1px")
        diagram.append("\tclassDef active fill:#EAA,stroke:#000,stroke-width:3px")
        self._unthemed_diagram = "\n".join(diagram)
        #return theme + diagram
    
    def get_diagram(self, active = "__start__") -> str:
        diagram = self._unthemed_diagram.splitlines()
        diagram.append("\tclass " + active + " active")
        diagram = "\n".join(diagram)
        print("GRAPH: ")
        print(diagram)
        return diagram

    def generate_stream_response(self, input, state):
        print(f"Calling generate_stream_response with input={input} and state={state}")
        if state.graph_state != "waiting_for_input":
            # If no tool is called
            events = self._graph.stream({"messages": ("user", input)}, config, stream_mode="values")
            for event in events:
                state.graph_state = self._graph.get_state(config).next[0]
                yield self._pretty_message(event, state.graph_state)
        else:
            # If tool is called
            if input.strip() == "y":
                # If tool is accepted
                events = self._graph.stream(None, config, stream_mode="values")
                for event in events:
                    state.graph_state = self._graph.get_state(config).next[0]
                    yield self._pretty_message(event, state.graph_state)
            else:
                # If tool is rejected
                state.graph_state = "assistant"
                print(f"Rejecting use of tool with id {state.snapshot.values['messages'][-1].tool_calls[0]['id']}")
                event = graph.invoke(
                    {
                        "messages": [
                            ToolMessage(
                                tool_call_id=state.snapshot.values["messages"][-1].tool_calls[0]["id"],
                                content=f"API call denied by user. Reasoning: '{input}'. Continue assisting, accounting for the user's input.",
                            )
                        ]
                    },
                    config,
                )
                yield self._pretty_message(event, state.graph_state)
        snapshot = graph.get_state(config)

        #If there is man-in-the-loop request
        if snapshot.next:
            print("Setting waiting_for_input status")
            state.graph_state = "waiting_for_input" 
            yield "Do you approve of the above actions? Type 'y' to continue; otherwise, explain your requested changed.\n\r\n\r"
        state.snapshot = snapshot
#term_io()