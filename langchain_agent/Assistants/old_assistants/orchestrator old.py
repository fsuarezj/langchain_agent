from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph.message import AnyMessage, add_messages
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig, RunnablePassthrough
from pydantic import BaseModel
from typing import Literal, Annotated

from ..global_conf import GPT_MODEL
from .base_state import BaseState

workers = {
    "formExpert": "A worker that will modify the form as requested by the user",
    #"formBuilder": "A worker that will build the xlsform, only when the form is finished and confirmed by the user"
}

options = ["end"] + list(workers.keys())

class routeResponse(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    next: Literal[*options]

system_prompt = (
    "You are a helpful assistant that creates forms in xlsform, given the following questionnaire uploaded by the user:"
    ""
    "{source_questionnaire}"
    ""
    "You can chat with the user about the questionnaire, to understand better what needs to be modified or if they think that "
    "the questionnaire is ready. Once the user thinks the questionnaire is ready, you can convert it "
    "You have several workers that help you with that. These are your workers:"
    "{workers}."
    "Each worker will perform a task and respond with their results and status. When finished,"
    " respond with 'end'."
    #"Ask the user what do they want to improve in the form or if they want "
)

system_instruction = (
    "Given the conversation above, respond to the user and select the worker that should act next or orchestrator if you want to"
    "continue chatting with the user"
    "Respond with a json with two keys:"
    "- The key 'messages' is your response"
    "- The key 'next' is the next step"
    "The next step is one of: {options}"
)

class Orchestrator():

    def __init__(self):
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                ("system", system_instruction)
                #("placeholder", "{messages}")
            ]
        ).partial(
            workers=str(workers),
            options=", ".join(options)
        )

        #runnable_args = {"source_questionnaire": RunnablePassthrough(), "messages": RunnablePassthrough()}
        self._parser = JsonOutputParser(pydantic_object=routeResponse)
        self._llm = ChatOpenAI(model=GPT_MODEL)
        #self._runnable = runnable_args | self._prompt | self._llm | self._parser #.with_structured_output(routeResponse) | self._parser
        self._runnable = self._prompt | self._llm | self._parser #.with_structured_output(routeResponse) | self._parser
    
    def __call__(self, state: BaseState, config: RunnableConfig):
        print("CALL Orchestrator")
        print(state)
        result = self._runnable.invoke(state)#["source_questionnaire"], state["messages"])
        print("Orchestrator output:")
        print(result)
        return result
        #state.update(result)
        #return state