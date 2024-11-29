from enum import Enum
from typing import List, Optional
from typing_extensions import Self
#from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field, model_validator, ValidationError
import pandas as pd
from re import sub

class ItemType(str, Enum):
    note = 'note'
    text = 'text'
    integer = 'integer'
    decimal = 'decimal'
    select_one = 'select_one'
    select_multiple = 'select_multiple'
    section = 'section'

class Nameable:
    def get_name(self):
        result = sub(r"(_|-)+", " ", self.label).title().replace(" ", "")
        max = min(len(result), 10)
        return ''.join([result[0].lower(), result[1:max]])

class Option(BaseModel): #, Nameable):
    label: str = Field(description="option name")
    name: str = Field(description="A variable name in camelCase, should be unique, simple, meaningful and related to the label. It should not have any special characters")

    def to_xlsform(self, list_name: str, choices: pd.DataFrame):
        row = {
            'list_name': list_name,
            'name': self.name, #self.get_name(),
            'label': self.label
        }
        choices = pd.concat([choices, pd.Series(row).to_frame().T], ignore_index=True)
        return choices

class Item(BaseModel): #, Nameable):
    type: ItemType = Field(description="type of the question, note or section")
    question_num: Optional[int] = Field(default="", description="Mandatory, number of the question in the form. If it doesn't exist in the original form, it has to be created. Only defined if the item type is not a note or a section. Auto-generated and unique for the whole questionnaire and starting with 1. Remove for notes and sections")
    label: str = Field(description="question statement, note content or section title")
    name: str = Field(description="A variable name in camelCase, should be unique, simple, meaningful and related to the label. If it's a select question with 2 or 3 options it should be related to the options. It should not start with a number and shouldn't have any special characters")
    hint: Optional[str] = Field(default="", description="Optional, any hint given to explain the question/note or how to ask or read it, if existing. It could also be some meaningful information about the section")
    content: Optional[List['Item']] = Field(default = None, description="Mandatory and only existing if type is a section, nested content of the section")
    list_name: Optional[str] = Field(default=None, description="Mandatory and only existing if it's a select_one or select_multiple question. It's a variable name in camelCase, should be unique, simple, meaningful and related to the label or, if there are only 2 or 3 options, related to the options. It should not start with a number, and shouldn't have any special characters")
    options: Optional[List[Option]] = Field(default = None, desctiption="Mandatory and only existing if it's a select_one or select_multiple question, it is list of options")

    @model_validator(mode='after')
    def check_optional_fields(self) -> Self:
        if self.type not in ['section', 'note'] and not self.question_num:
            raise ValueError('question number not defined')
        elif self.type == 'section' and not self.content:
            raise ValueError('section content not defined')
        if self.type in ['select_one', 'select_multiple']:
            if not self.options:
                raise ValueError('options should be defined')
            if not self.list_name:
                raise ValueError('list_name should be defined')
        return self

    def _create_row(self):
        if self.type == 'note':
            survey_row = {
                'type': self.type.split(".", 1)[0],
                'name': self.name, #self.get_name(),
                'label': self.label,
                'hint': self.hint
            }
        elif self.type in ['text', 'integer', 'decimal']:
            survey_row = {
                'type': self.type.split(".", 1)[0],
                'name': self.name, #self.get_name(),
                'label': str(self.question_num) + '. ' + self.label,
                'hint': self.hint
            }
        elif self.type in ['select_one', 'select_multiple']:
            survey_row = {
                'type': self.type + " " + self.name, #self.get_name(),
                'name': self.name, #self.get_name(),
                'label': str(self.question_num) + '. ' + self.label,
                'hint': self.hint
            }
        elif self.type == 'section':
            survey_row = {
                'type': 'begin_group',
                'name': self.name, #self.get_name(),
                'label': self.label,
                'hint': self.hint
            }
        return survey_row

    def to_xlsform(self, survey: pd.DataFrame, choices: pd.DataFrame, choices_dict: dict):
        row = self._create_row()
        survey = pd.concat([survey, pd.Series(row).to_frame().T], ignore_index=True)
        if self.type == 'section':
            for i in self.content:
                (survey, choices) = i.to_xlsform(survey, choices, choices_dict)
            survey = pd.concat([survey, pd.Series({'type': 'end_group'}).to_frame().T], ignore_index=True)
        elif self.type in ['select_one', 'select_multiple']:
            #options = [opt.label for opt in self.options].sort()
            options = []
            for opt in self.options:
                options.append(opt.label.lower())
            options.sort()
            if options not in choices_dict.values():
                list_name = self.list_name if self.list_name else self.name
                choices_dict[list_name] = options
                for opt in self.options:
                    choices = opt.to_xlsform(list_name, choices)
            else:
                key = list(filter(lambda x: choices_dict[x] == options, choices_dict))[0]
                survey.iloc[-1, survey.columns.get_loc('type')] = self.type + " " + key
        return (survey, choices)

class Questionnaire(BaseModel):
    title: Optional[str] = Field(default = None, description="title of the questionnaire, must be short (3 or 4 words) and meaningful, showing the content of the questionnaire and providing information to differenciate the questionnaire of other similar ones, for example the location, the project title and/or the disaster")
    description: Optional[str] = Field(default = None, description="description of the questionnaire")
    content: Optional[List[Item]] = Field(default = None, description="content of the questionnaire")
    error: Optional[str] = Field(default = None, description="Only filled if there is an error in the form")

    def to_xlsform(self, filename):
        survey = pd.DataFrame()
        choices = pd.DataFrame()
        choices_dict = {}
        for i in self.content:
            (survey, choices) = i.to_xlsform(survey, choices, choices_dict)
        with pd.ExcelWriter(filename) as writer:
            print("Writing file")
            survey.to_excel(writer, sheet_name='survey', index=False)
            choices.to_excel(writer, sheet_name='choices', index=False)