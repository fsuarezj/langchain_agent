from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from ..global_conf import GPT_MODEL
from .base_state import BaseState

class Orchestrator:
    def __init__(self):
        self._prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that creates forms in xlsform, given a questionnaire designed by the user. "
                    "The first step for the user is to upload a file with the questionnaire"
                    "Do not create a questionnaire, just use the one uploaded by the user."
                    "You can chat with the user and respond their questions, but if the form has not been uploaded, remind them"
                     " to upload it"
                ),
                ("placeholder", "{messages}")
            ]
        )
        self._llm = ChatOpenAI(model=GPT_MODEL)
        self._runnable = self._prompt | self._llm
    
    def __call__(self, state: BaseState, config: RunnableConfig):
        print("ENTRY STATE IS ")
        print(state)
        result = self._runnable.invoke(state)
        print("INTERNAL AFTER STATE IS ")
        state["messages"] = state["messages"] + [result]
        print(state)
        return {"messages": result}