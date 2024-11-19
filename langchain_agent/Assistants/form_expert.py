from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig, RunnablePassthrough

from ..global_conf import GPT_MODEL
from .base_state import BaseState
from .json_form import Questionnaire

system_prompt = (
    "You are a helpful assistant that improves forms in json, given a questionnaire designed by the user. "
    "You can answer and respond questions about the form."
    "You can also modify things or question in the form if necessary, but always ask the user to confirm before doing it"
    "The form will have to be always in the following format:"
    "{format_questionnaire}"
    "You can chat with the user but don't respond to questions not related to your task."
    "The form uploaded by the user is this one:"
    "{source_questionnaire}"
    "This is the conversation with the user:"
)

class FormExpert:

    def __init__(self):
        self._parser = JsonOutputParser(pydantic_object=Questionnaire)
        runnable_args = {"source_questionnaire": RunnablePassthrough(), "messages": RunnablePassthrough()}
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages")
            ]
        ).partial(format_questionnaire=self._parser.get_format_instructions())
        self._llm = ChatOpenAI(model=GPT_MODEL)
        self._runnable = (
            runnable_args | self._prompt | self._llm
        )
    
    def __call__(self, state: BaseState, config: RunnableConfig):
        print("CALL FormExpert")
        print(state)
        #result = {"messages": self._runnable.invoke(
                #state["messages"],
                #state["source_questionnaire"],
        #)}
        result = self._runnable.invoke(state["messages"])
        state["messages"] = state["messages"] + [result]
        return {"messages": result}
