from enum import Enum
from typing import List, Optional
from langchain_core.pydantic_v1 import BaseModel, Field

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
    question_num: Optional[int] = Field("number of the question in the questionnaire. Only defined if the item is a question, not for notes or sections. Unique for the whole questionnaire and starting with 1. Notes and sections do not have a number")
    label: str = Field(description="question statement, note content or section title")
    hint: str = Field(description="Any hint given to explain the question/note or how to ask or read it, if existing. It could also be some meaningful information about the section")
    content: Optional[List['Item']] = Field(description="Only existing if type is a section, nested content of the section")
    options: Optional[List[Option]] = Field(desctiption="if it's a select_one or select_multiple question, list of options")

class Questionnaire(BaseModel):
    title: Optional[str] = Field(description="title of the questionnaire, must be short (3 or 4 words) and meaningful, showing the content of the questionnaire and providing information to differenciate the questionnaire of other similar ones, for example the location, the project title and/or the disaster")
    description: Optional[str] = Field(description="description of the questionnaire")
    content: Optional[List[Item]] = Field(description="content of the questionnaire")
    error: Optional[str] = Field(description="Only filled if there is an error in the form")