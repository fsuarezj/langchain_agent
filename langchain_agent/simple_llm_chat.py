from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from global_conf import GPT_MODEL

load_dotenv()
#api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(model=GPT_MODEL)

messages = [
    SystemMessage(content="Translate the following to Spanish"),
    HumanMessage(content="Hi, how are you? I am good, thanks"),
]

system_template = "Translate the following into {language}"
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

parser = StrOutputParser()

chain = prompt_template | model | parser

#result = chain.invoke(messages)
result = chain.invoke({"language": "italian", "text": "Hi, how is the people?"})

print(result)