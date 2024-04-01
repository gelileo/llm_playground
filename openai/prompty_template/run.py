from langchain_openai import ChatOpenAI

# from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.prompts.chat import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

chat_model = ChatOpenAI(openai_api_key=api_key)

template = (
    "You are a helpful assistant that translates {input_language} to {output_language}."
)
human_template = "{text}"

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", template),
        ("human", human_template),
    ]
)


src = """
Stock futures rose slightly on Sunday evening as Wall Street prepared for the start of the second quarter.

Futures tied to the Dow Jones Industrial Average
 added 110 points, or 0.3%, while S&P 500 futures
 and Nasdaq-100 futures
 gained 0.3% and 0.5%, respectively.

The personal consumption expenditures price index, released Friday during the market closure for Good Friday, showed inflation rose 2.8% in February, which is in line with expectations. The inflation gauge closely watched by the Federal Reserve also rose 0.3% from a month ago, the Commerce Department said.
"""
messages = chat_prompt.format_messages(
    input_language="English", output_language="Chinese", text=src
)
# result = chat_model.predict_messages(messages)
result = chat_model.invoke(messages)
print(result.content)
