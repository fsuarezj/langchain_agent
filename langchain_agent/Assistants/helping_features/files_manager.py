from langchain_community.document_loaders import PyPDFLoader
#from langchain_community.document_loaders import Docx2txtLoader
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
import filetype
import pandas as pd

class FilesManager:
    def __init__(self):
        #self._loader = None
        #self._pages = []
        self._document_loaded = False
        self._content = ""

    def _parse_doc(self, file_path):
        document = Document(file_path)
        print(dir(document))
        content = ""
        for element in document.iter_inner_content():
            #print(element)
            if type(element) == Paragraph:
                content += element.text + '\n\n'
            elif type(element) == Table:
                data = [[cell.text for cell in row.cells] for row in element.rows]
                df = pd.DataFrame(data)
                df = df.rename(columns=df.iloc[0]).drop(df.index[0]).reset_index(drop=True)
                #content += df.to_string(index=False)
                content += df.to_markdown(index=False)
        return content
    
    def load_file(self, file, type = None) -> None:
        print(file)
        if not type:
            type = filetype.guess_mime(file).split("/")[1]
        print(type)
        match type:
            # .pdf
            case "pdf":
                print("pdf found")
                #self._loader = PyPDFLoader(file)
                #self._pages = self._loader.load_and_split()
                self._content = "\n".join([i.page_content for i in self._pages])
            # .docx
            case "vnd.openxmlformats-officedocument.wordprocessingml.document":
                print("word doc found")
                self._content = self._parse_doc(file)
                if self._content != "":
                    self._document_loaded = True
                #self._pages = self._loader.load_and_split()
            case _:
                print("File not supported")
    
#    def get_pages(self) -> list[str]:
#        return self._pages
    
    def whole_content(self) -> str:
        return self._content

#    def get_page_document(self, int) -> str:
#        return self._pages[int]
#
#    def get_page_content(self, int) -> str:
#        return self._pages[int].page_content