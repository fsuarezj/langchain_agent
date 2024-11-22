from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig, RunnablePassthrough
from langchain_core.messages.ai import AIMessage
from pydantic import BaseModel
from typing import Optional

from ..global_conf import GPT_MODEL
from .base_state import BaseState
from .json_form import Questionnaire

class builderResponse(BaseModel):
    messages: str
    source_questionnaire: Optional[Questionnaire]

system_prompt = (
    """
    You are a helpful assistant that improves forms in json, given an original form designed by the user and a request.
    You can modify things or question in the form if necessary, but always ask the user to confirm before doing it and
    don't do it until you receive the confirmation.
    You must keep the rest of the form as the original and only change or modify what the user asks.
    The form will have to be always in the following format:

    {format_questionnaire}

    The original form uploaded by the user is this one:

    {source_questionnaire}
    
    You can chat with the user to clarify their request but don't respond to questions not related to your task.
    If the form has not been uploaded, remind them to upload it.

    This is the conversation with the user:
    """
) 

system_instruction = (
    """
    Given the conversation above, if you have enough information, modify or improve what the user requests and provide the new
    whole form with the modifications. If you need more information to modify the form, ask the user and do not provide any new form.
    Respond with a json with one or two keys:
    - The key 'messages' is your response
    - The key 'source_questionnaire' is optional and has the new questionnaire, only if it has been modified.
    """
    #Respond with a json with the key "next" with the name of the worker that should respond or "end" if you have finished
)


class FormBuilder:

    def __init__(self):
        formParser = JsonOutputParser(pydantic_object=Questionnaire)
        self._parser = JsonOutputParser(pydantic_object=builderResponse)
        runnable_args = {"source_questionnaire": RunnablePassthrough(), "messages": RunnablePassthrough()}
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                ("system", system_instruction)
            ]
        ).partial(format_questionnaire=formParser.get_format_instructions())
        self._llm = ChatOpenAI(model=GPT_MODEL)
        self._runnable = (
            runnable_args | self._prompt | self._llm | self._parser
        )
    
    def __call__(self, state: BaseState, config: RunnableConfig):
        print("CALL FormBuilder")
        print(state)
        #result = {"messages": self._runnable.invoke(
                #state["messages"],
                #state["source_questionnaire"],
        #)}
        result = self._runnable.invoke(state["messages"], state["source_questionnaire"])
        state["messages"] = state["messages"] + [AIMessage(result["messages"])]
        result["messages"] = AIMessage(result["messages"])
        print("FormBuilder output:")
        print(result)
        print("State")
        print(state)
        return result
