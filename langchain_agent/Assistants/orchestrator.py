from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel
from typing import Literal

from ..global_conf import GPT_MODEL
from .base_state import BaseState

workers = {
    "formExpert": "A worker that will respond any question about the form and modify it if necessary, as per the request given by the user",
    "formBuilder": "A worker that will build the xlsform, only when the form is finished and confirmed by the user"
}

options = ["END"] + list(workers.keys())

class routeResponse(BaseModel):
    next: Literal[*options]

system_prompt = (
    "You are a helpful assistant that creates forms in xlsform, given a questionnaire designed by the user."
    "To do that, you have several workers that help you with that. These are your workers:"
    "{workers}."
    "Each worker will perform a task and respond with their results and status. When finished,"
    " respond with END."
    #"Ask the user what do they want to improve in the form or if they want "
)

system_instruction = (
    "Given the conversation above, who should act next?"
    "Or should we END? Select one of: {options} abd respond with a json where the key is 'next'"
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
        self._runnable = self._prompt | self._llm | self._parser #.with_structured_output(routeResponse) | self._parser
    
    def __call__(self, state: BaseState, config: RunnableConfig):
        print("CALL Orchestrator")
        result = self._runnable.invoke(state)
        print("Orchestrator output:")
        print(result)
        return result
        #state.update(result)
        #return state