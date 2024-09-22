from dotenv import load_dotenv
import json

import unittest
from langchain_agent.assistants.form_parser import FormParser
from langchain_agent.assistants.helping_features.files_manager import FilesManager

form_name = "test_form2"

class State:
    def __init__(self, file_content):
        self.values = {"source_questionnaire": file_content}

class FormParserTests(unittest.TestCase):

    def testBasicDivide(self):
        fm = FilesManager()
        fm.load_file("./tests/tmp/" + form_name + ".docx")
        print("File loaded")
        state = State(fm.whole_content())
        print(state.values)
        agent = FormParser()
        result = agent.run("Ignore", state)
        print(json.dumps(result["messages"], indent=4))
        #print(fm.whole_content())
        with open("langchain_agent/assistants/examples/" + form_name + ".out", 'w') as file:
            file.write(json.dumps(result["messages"], indent=4))
        with open("langchain_agent/assistants/examples/form_parser1.out", 'r') as file:
            form_parser1_out = json.load(file)
        self.assertEqual(result["messages"], form_parser1_out)


if __name__ =='__main__':
    load_dotenv()
    unittest.main()
