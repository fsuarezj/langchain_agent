from enum import Enum
from typing import List, Optional
#from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field
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

class Option(BaseModel, Nameable):
    label: str = Field(description="option name")
    #name: str = Field(description="internal name of the option, in camelCase, one or two words not starting with numbers, meaningful and without special characters")

    def to_xlsform(self, list_name: str, choices: pd.DataFrame):
        row = {
            'list_name': list_name,
            'name': self.get_name(),
            'label': self.label
        }
        choices = pd.concat([choices, pd.Series(row).to_frame().T], ignore_index=True)
        return choices

class Item(BaseModel, Nameable):
    type: ItemType = Field(description="type of the question, note or section")
    question_num: Optional[int] = Field(default = None, description="Mandatory, number of the question in the form. If it doesn't exist in the original form, it has to be created. Only defined if the item type is not a note or a section. Auto-generated and unique for the whole questionnaire and starting with 1. Remove for notes and sections")
    label: str = Field(description="question statement, note content or section title")
    hint: Optional[str] = Field(default = None, description="Any hint given to explain the question/note or how to ask or read it, if existing. It could also be some meaningful information about the section")
    content: Optional[List['Item']] = Field(default = None, description="Mandatory and only existing if type is a section, nested content of the section")
    options: Optional[List[Option]] = Field(default = None, desctiption="Mandatory and only existing if it's a select_one or select_multiple question, it is list of options")

    def _create_row(self):
        if self.type == 'note':
            survey_row = {
                'type': self.type.split(".", 1)[0],
                'name': self.get_name(),
                'label': self.label,
                'hint': self.hint
            }
        elif self.type in ['text', 'integer', 'decimal']:
            survey_row = {
                'type': self.type.split(".", 1)[0],
                'name': self.get_name(),
                'label': str(self.question_num) + '. ' + self.label,
                'hint': self.hint
            }
        elif self.type in ['select_one', 'select_multiple']:
            survey_row = {
                'type': self.type + " " + self.get_name(),
                'name': self.get_name(),
                'label': str(self.question_num) + '. ' + self.label,
                'hint': self.hint
            }
        elif self.type == 'section':
            survey_row = {
                'type': 'begin_group',
                'name': self.get_name(),
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
                print("NEW")
                choices_dict[self.get_name()] = options
                for opt in self.options:
                    choices = opt.to_xlsform(self.get_name(), choices)
            else:
                print("EXISTING")
                key = list(filter(lambda x: choices_dict[x] == options, choices_dict))[0]
                print(key)
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
            survey.to_excel(writer, sheet_name='survey', index=False)
            choices.to_excel(writer, sheet_name='choices', index=False)