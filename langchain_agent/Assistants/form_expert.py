from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig, RunnablePassthrough

from ..global_conf import GPT_MODEL
from .base_state import BaseState
from .json_form import Questionnaire
from .agents_features.cost_calculator import CostCalculator

system_prompt = (
    """
    You are a helpful assistant that responds to questions about a questionnaire designed by the user.
    
    The form will always in the following json format:
    {format_questionnaire}

    The form uploaded by the user is here below:
    {source_questionnaire}

    Do not create any questionnaire, just use the one uploaded by the user.
    You can chat with the user but don't respond to questions not related to the questionnaire, if the 
    form has not been uploaded, remind them to upload it.

    If you respond with a question, format it as follows:
    - Use the numeration of the question defined in the variable "question_num"
    - Write the question label in bold
    - Write the question type in italic
    - If existing, write the options as bullet points
    
    This is the conversation with the user:
    """
)

class FormExpert(CostCalculator):

    def __init__(self):
        self._parser = JsonOutputParser(pydantic_object=Questionnaire)
        #runnable_args = {"source_questionnaire": RunnablePassthrough(), "messages": RunnablePassthrough()}
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages")
            ]
        ).partial(format_questionnaire=self._parser.get_format_instructions())
        self._llm = ChatOpenAI(model=GPT_MODEL)
        self._runnable = (
            self._prompt | self._llm
        )
    
    def __call__(self, state: BaseState, config: RunnableConfig):
        print("CALL FormExpert")
        print(state)
        #result = {"messages": self._runnable.invoke(
                #state["messages"],
                #state["source_questionnaire"],
        #)}
        result = self._costs_invoke_OpenAI(state['costs'], state) #["source_questionnaire"], state["messages"])
        state["messages"] = state["messages"] + [result]
        return {"messages": result}
