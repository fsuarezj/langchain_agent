from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages

def add_cost(state: dict, costs: dict) -> object:
    print("UPDATING")
    print(state)
    print(costs)
    if state:
        new_costs = {i: state.get(i,0) + costs.get(i,0) for i in set(state).union(costs)}
        print("Updated existing")
        print(new_costs)
    else:
        new_costs = costs
    #if 'messages' in state: new_state['messages'] = state['messages']
    #if 'source_questionnaire' in state: new_state['source_questionnaire'] = state['source_questionnaire']
    #if 'parsed_questionnaire' in state: new_state['parsed_questionnaire'] = state['parsed_questionnaire']
    #if 'next' in state: new_state['next'] = state['next'] 
    return BaseState(new_costs)
    #    messages=messages,
    #    costs=new_costs,
    #    source_questionnaire=source_questionnaire,
    #    parsed_questionnaire=parsed_questionnaire,
    #    next=next

class BaseState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    costs: Annotated[dict,add_cost]
    source_questionnaire: str
    parsed_questionnaire: bool
    next: str
