from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from datetime import datetime

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    country: str

@tool
def get_country():
    """Gets the country of the project"""
    return "Ask the user about the country of the project"

@tool
def set_country(state: State, country: str):
    state.country = country

class SimpleAssistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            user_id = config.get("user_id", None)
            state = {**state, "user_info": user_id}
            result = self.runnable.invoke(state)

            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

system_prompt = f"You are a helpful assistance aimed to create registration forms for the 121 platform. \
    The 121 platform is a system to manage cash projects developed by 510, the data and \
    digital unit of Netherlands Red Cross.\
    You can use knowledge from the Red Cross Red Crescent Movement or the humanitarian world, \
    But if the user asks anything not related to the registration form you are doing, you will \
    respond that you have been created only for this purpose.\
    Use the provided tools to gather information about the project."

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system_prompt
        ),
        ("placeholder", "{messages}")
    ]
).partial(time=datetime.now())

tools1 = [
    get_country,
    set_country
]

Follow tutorial: https://langchain-ai.github.io/langgraph/tutorials/customer-support/customer-support/#part-1-zero-shot-agent

Create simple assistant and write graph in langGraph chatbot with tools to get and set the country