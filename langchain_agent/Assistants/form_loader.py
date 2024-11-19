from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from ..global_conf import GPT_MODEL
from .base_state import BaseState

system_prompt = (
    "You are the first step of a helpful assistant that creates forms in xlsform, given a questionnaire designed by the user. "
    "To start the process, the user is to upload a file with the questionnaire"
    "Do not create any questionnaire, just use the one uploaded by the user."
    "You can chat with the user but don't respond to questions not related to your task, if the form has not been uploaded,"
    "remind them to upload it"
)

class FormLoader:

    def __init__(self):
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages")
            ]
        )
        self._llm = ChatOpenAI(model=GPT_MODEL)
        self._runnable = self._prompt | self._llm
    
    def __call__(self, state: BaseState, config: RunnableConfig):
        print("CALL FormLoader")
        result = self._runnable.invoke(state)
        state["messages"] = state["messages"] + [result]
        print(result)
        return {"messages": result}

#members = ["formParser"]
#complex_system_prompt = (
#    "You are a helpful assistant that creates forms in xlsform, given a questionnaire designed by the user. "
#    "To do that, you have one agent that can help you if necessary: {members}. If you need the help of that agent"
#    " respond AGENT: and the name of the agent"
#    "The first step for the user is to upload a file with the questionnaire"
#    "You will not create a questionnaire, you can just use the one uploaded by the user."
#    "You can also chat with the user and respond to their questions, but if the form has not been uploaded,"
#    " remind them to upload it."
#    "Once the questionnaire is uploaded, follow the next steps:"
#    "1. Parse the questionnaire"
#    "2. Show the questionnaire and ask if it's valid"
#)
