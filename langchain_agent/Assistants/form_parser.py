from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from pydantic_core import from_json

from ..global_conf import GPT_MODEL
from .json_form import Questionnaire
from .base_state import BaseState

class FormParser:
    def __init__(self):
        self._llm = ChatOpenAI(model=GPT_MODEL)
        self._parser = JsonOutputParser(pydantic_object=Questionnaire)
        self._examples = []
        self._load_examples()
        self._prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant that divide questionnaires into individual questions.
                    Given the questionnaire below, you will return a json with a list of all the questions. 
                    Include the questions in the introduction also.
                    Some questions in the questionnaire or in the introduction can be open, a number, or in the form
                    of a sentence, requiring the user to fill a text or a number, in that case add them as the type "text",
                     or "integer" or "decimal", depending the type of response expected. Also include notes to the enumerator 
                     or to the respondant if existing in the questionnaire, in that case add them with the type "note".
                    The questions have to be in the following format:
                    {format_instructions}
                    Do not create or add anything to the questionnaire, just work with the questionnaire provided below.

                    Q:
                    {example1_in}
                    A:
                    {example1_out}

                    Q:
                    {source_questionnaire}
                    A:
                    """
                )
            ]
        ).partial(format_instructions=self._parser.get_format_instructions(),
                  example1_in=self._examples[0][0],
                  example1_out=self._examples[0][1]
        )
        runnable_args = {"source_questionnaire": RunnablePassthrough()}
        self._runnable = (
            runnable_args | self._prompt | self._llm | self._parser
        )

    def __call__(self, state: BaseState, config: RunnableConfig):
        print("CALL FormParser")
        print(state)
        # Calling the LLM
        result = {"messages": self._runnable.invoke(
            {
                "source_questionnaire": state["source_questionnaire"]
                }
            )}
        parsed_questionnaire = result["messages"]
        form_str = str(parsed_questionnaire)
        print(form_str)
        form_str = from_json(form_str)
        print(form_str)
        form = Questionnaire.model_validate(from_json(form_str, allow_partial=True))
        form.to_xlsform('formulario.xlsx')
        return {"source_questionnaire": parsed_questionnaire, "parsed_questionnaire": True}
    
    def _load_examples(self):
        # Load examples for one-shot or few-shots
        with open("langchain_agent/assistants/examples/form_parser1.in", 'r', encoding="utf-8") as file:
            form_parser1_in = ""#file.read()
        with open("langchain_agent/assistants/examples/form_parser1.out", 'r') as file:
            form_parser1_out = ""#json.load(file)
        self._examples.append((form_parser1_in, form_parser1_out))