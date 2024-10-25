from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages

class BaseState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    source_questionnaire: str
    parsed_questionnaire: bool
