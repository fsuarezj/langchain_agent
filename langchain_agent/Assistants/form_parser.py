from enum import Enum
from typing import List, Optional
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

from ..global_conf import GPT_MODEL
from .base_state import BaseState

class ItemType(str, Enum):
    note = 'note'
    text = 'text'
    integer = 'integer'
    decimal = 'decimal'
    select_one = 'select_one'
    select_multiple = 'select_multiple'
    section = 'section'

class Option(BaseModel):
    label: str = Field(description="option name")
    #name: str = Field(description="internal name of the option, in camelCase, one or two words not starting with numbers, meaningful and without special characters")

class Item(BaseModel):
    type: ItemType = Field(description="type of the question, note or section")
    num: Optional[int] = Field("number of the question in the questionnaire. Only defined if the item is a question, not for notes or sections")
    label: str = Field(description="question statement, note content or section title")
    hint: str = Field(description="any hint given to explain the question or how to ask it, if existing. Or any aditional meaningful information about the note or section")
    content: Optional[List['Item']] = Field(description="content of the section, if type is a section")
    options: Optional[List[Option]] = Field(desctiption="if it's a select_one or select_multiple question, list of options")

class Questionnaire(BaseModel):
    title: Optional[str] = Field(description="title of the questionnaire, must be short (3 or 4 words) and meaningful, showing the content of the questionnaire and providing information to differenciate the questionnaire of other similar ones, for example the location, the project title and/or the disaster")
    description: Optional[str] = Field(description="description of the questionnaire")
    content: Optional[List[Item]] = Field(description="content of the questionnaire")
    error: Optional[str] = Field(description="Only filled if there is an error in the form")

class FormParser:
    def __init__(self):
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
                    {form_parser1_in}
                    A:
                    {form_parser1_out}

                    Q:
                    {source_questionnaire}
                    A:
                    """
                )
            ]
        )
        self._llm = ChatOpenAI(model=GPT_MODEL)
        self._parser = JsonOutputParser(pydantic_object=Questionnaire)
        self._runnable = (
            {
                "source_questionnaire": RunnablePassthrough(),
                "format_instructions": RunnablePassthrough(),
                "form_parser1_in": RunnablePassthrough(),
                "form_parser1_out": RunnablePassthrough()
            }
            | self._prompt 
            | self._llm
            | self._parser
        )

    def __call__(self, state: BaseState, config: RunnableConfig):
        print("CALL FormParser")
        # Opening One-shot examples
        with open("langchain_agent/assistants/examples/form_parser1.in", 'r', encoding="utf-8") as file:
            form_parser1_in = ""#file.read()
        with open("langchain_agent/assistants/examples/form_parser1.out", 'r') as file:
            form_parser1_out = ""#json.load(file)
        
        # Calling the LLM
        result = {"messages": self._runnable.invoke(
            {
                "source_questionnaire": state["source_questionnaire"],
                "format_instructions": self._parser.get_format_instructions(),
                "form_parser1_in": form_parser1_in,
                "form_parser1_out": form_parser1_out
                }
            )}
        parsed_questionnaire = result["messages"]
        return {"messages": "Form parsed", "source_questionnaire": parsed_questionnaire, "parsed_questionnaire": True}

    def run(self, input, state):
        print("ENTRA")
        with open("langchain_agent/assistants/examples/form_parser1.in", 'r', encoding="utf-8") as file:
            form_parser1_in = ""#file.read()
        with open("langchain_agent/assistants/examples/form_parser1.out", 'r') as file:
            form_parser1_out = ""#json.load(file)
        
        print("QUESTIOOOOON")
        print(state.values["source_questionnaire"])

        result = {"messages": self._runnable.invoke(
            {
                "source_questionnaire": state.values["source_questionnaire"],
                "format_instructions": self._parser.get_format_instructions(),
                "form_parser1_in": form_parser1_in,
                "form_parser1_out": form_parser1_out
                }
            )}
        #print("Divided questions is: ")
        #print(result["messages"])
        state.values["parsed_questionnaire"] = True
        #for i in divided["messages"].content:
            #print("-- QUESTION --\n")
            #print(i)
        return result