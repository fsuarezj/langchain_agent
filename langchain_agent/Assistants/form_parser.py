from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers.string import StrOutputParser
from langchain_openai import ChatOpenAI
from ..global_conf import GPT_MODEL

class FormParser:
    def __init__(self):
        self._prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant that divide questionnaires into individual questions
                    Given the questionnaire below, you will return a json with a list of the questions 
                    and their options, if there are close questions. Do not create or add anything to the 
                    questionnaire, just work with the questionnaire provided below.
                    If the text below does not look like a questionnaire, you will return a message saying:
                    "ERROR: THE DOCUMENT YOU UPLOADED DOES NOT SEEM TO BE A QUESTIONNAIRE"

                    Questionnaire:
                    {source_questionnaire}
                    """
                )
            ]
        )
        self._llm = ChatOpenAI(model=GPT_MODEL)
        self._runnable = (
            {"source_questionnaire": RunnablePassthrough()}
            | self._prompt 
            | self._llm
        #    | StrOutputParser()
        )

    def run(self, input, state):
        print("ENTRA")
        result = {"messages": self._runnable.invoke(state.values["source_questionnaire"])}
        print("Divided questions is: ")
        print(result["messages"])
        state.values["parsed_questionnaire"] = True
        #for i in divided["messages"].content:
            #print("-- QUESTION --\n")
            #print(i)
        return result