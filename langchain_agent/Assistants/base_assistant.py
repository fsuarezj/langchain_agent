from .assistance_interface import AssistantInterface
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader

import random
import time

class BaseAssistant(AssistantInterface):
    def __init__(self):
        self._mock_responses = [
            "Hello, this is response 1",
            "Now I'm giving you response 2",
            "This is not other than response 3"
        ]
    
    def load_file(self, file, filetype) -> None:
        print(file)
        print(filetype)
        match filetype:
            # .pdf
            case "pdf":
                print("pdf found")
                self._loader = PyPDFLoader(file)
                self._pages = self._loader.load_and_split()
            # .docx
            case "vnd.openxmlformats-officedocument.wordprocessingml.document":
                print("word doc found")
                self._loader = Docx2txtLoader(file)
                self._pages = self._loader.load_and_split()
            case _:
                print("File not supported")
    
    def read_first_page(self):
        return self._pages[0]
    
    def generate_stream_response(self, input):
        for word in random.choice(self._mock_responses).split():
            yield word + " "
            time.sleep(0.05)