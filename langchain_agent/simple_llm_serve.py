#!/user/bin/env python
from typing import List

from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langserve import add_routes

from global_conf import GPT_MODEL

system_template = "Translate the following into {language}"
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

model = ChatOpenAI(model=GPT_MODEL)
parser = StrOutputParser()

chain = prompt_template | model | parser

app = FastAPI(
    title="LangChain test",
    version="0.1.0",
    description="A simple API server using LangChain"
)

add_routes(
    app,
    chain,
    path="/chain",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)