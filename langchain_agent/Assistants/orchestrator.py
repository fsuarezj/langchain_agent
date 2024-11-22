from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel
from typing import Literal

from ..global_conf import GPT_MODEL
from .base_state import BaseState

workers = {
    "formBuilder": "A worker that will modify the form as requested by the user",
    "formExpert": "A worker that will respond any question about the form",
    #"formBuilder": "A worker that will build the xlsform, only when the form is finished and confirmed by the user"
}

#options = ["end"] + list(workers.keys())
options = list(workers.keys())

class routeResponse(BaseModel):
#    messages: Annotated[list[AnyMessage], add_messages]
    next: Literal[*options]

system_prompt = (
    """
    You are a helpful assistant that creates forms in xlsform, given a questionnaire uploaded by the user.

    You have several workers that help you with that. These are your workers:
    {workers}

    This is the conversation with the user:
    """
)

system_instruction = (
    """
    Given the conversation above, select the worker that should act next
    Respond with a json with the key "next" with the name of the worker that should respond.
    The next step is one of: {options}
    """
    #Respond with a json with the key "next" with the name of the worker that should respond or "end" if you have finished
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

        self._parser = JsonOutputParser(pydantic_object=routeResponse)
        self._llm = ChatOpenAI(model=GPT_MODEL)
        self._runnable = self._prompt | self._llm | self._parser
    
    def __call__(self, state: BaseState, config: RunnableConfig):
        print("CALL Orchestrator")
        print(state)
        result = self._runnable.invoke(state)
        print("Orchestrator output:")
        print(result)
        return result
        #state.update(result)
        #return state