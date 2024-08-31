from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader

class FilesManager:
    def __init__(self):
        self._loader = None
        self._pages = []
    
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
    
    def get_pages(self) -> list[str]:
        return self._pages

    def get_page(self, int) -> str:
        return self._pages[int]