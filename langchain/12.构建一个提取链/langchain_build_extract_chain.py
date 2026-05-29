import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
from typing import Optional,List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI

load_dotenv()

# required_env_vars = ["MISTRAL_API_KEY", "MISTRAL_BASE_URL", "MISTRAL_LLM_MODEL"]
# missing_vars = [var for var in required_env_vars if not os.getenv(var)]

required_env_vars = ["OPENAI_API_KEY", "OPENAI__BASE_URL", "OPENAI_LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

# if missing_vars:
#     raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

# 使用Pydantic定义一个提取个人信息的模式
class Person(BaseModel):
    """Information about a person."""

    # ^ Doc-string for the entity Person.
    # This doc-string is sent to the LLM as the description of the schema Person,
    # and it can help to improve extraction results.

    # Note that:
    # 1. Each field is an `optional` -- this allows the model to decline to extract it!
    # 2. Each field has a `description` -- this description is used by the LLM.
    # Having a good description can help improve extraction results.
    # 允许大型语言模型在不知道答案时输出 None
    name: Optional[str] = Field(default=None, description="The name of the person")
    hair_color: Optional[str] = Field(
        default=None, description="The color of the person's hair if known"
    )
    height_in_meters: Optional[str] = Field(
        default=None, description="Height measured in meters"
    )

class Data(BaseModel):
    """Extracted data about people."""

    # Creates a model so that we can extract multiple entities.
    people: List[Person]

def build_prompt():
    # Define a custom prompt to provide instructions and any additional context.
    # 1) You can add examples into the prompt template to improve extraction quality
    # 2) Introduce additional parameters to take context into account (e.g., include metadata
    #    about the document from which the text was extracted.)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.",
            ),
            # Please see the how-to about improving performance with
            # reference examples.
            # MessagesPlaceholder('examples'),
            ("human", "{text}"),
        ]
    )
    return prompt

try:
    # llm = ChatMistralAI(model=os.getenv("MISTRAL_LLM_MODEL","mistral-large-latest"), temperature=0)

    llm = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini"))

    prompt = build_prompt()
    # runnable = prompt | llm.with_structured_output(schema=Person)
    # text = "Alan Smith is 6 feet tall and has blond hair."
    # response = runnable.invoke({"text": text})
    # print(response)

    #多个实体
    runnable = prompt | llm.with_structured_output(schema=Data)
    text = "My name is Jeff, my hair is black and i am 6 feet tall. Anna has the same color hair as me."
    response = runnable.invoke({"text": text})
    print(response) #people=[Person(name='Jeff', hair_color='black', height_in_meters='1.83'), Person(name='Anna', hair_color='black', height_in_meters=None)]

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))