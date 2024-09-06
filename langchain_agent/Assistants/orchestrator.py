from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from ..global_conf import GPT_MODEL

class Orchestrator:
    def __init__(self):
        self._prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that creates forms. To start with, the user should"
                    "upload a questionnaire, so request the user to do it"
                    "Do not create a questionnaire."
                    "If the user asks a question not related to what you have been created for, do not consider it "
                    "as part of the questionnaire and respond that you are only programmed to create forms"
                )
            ]
        )
        self._llm = ChatOpenAI(model=GPT_MODEL)
        self._runnable = self._prompt | self._llm

    def run(self, input, state):
        return {"messages": self._runnable.invoke(input)}