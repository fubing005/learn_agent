import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import getpass

load_dotenv()

# 激活 LangChain 官方的“可视化调试与监控服务”（称为 LangSmith），并安全地输入你的服务秘钥
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = getpass.getpass()


required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

def tagging_prompt():
    tagging_prompt = ChatPromptTemplate.from_template(
        """
    Extract the desired information from the following passage.

    Only extract the properties mentioned in the 'Classification' function.

    Passage:
    {input}
    """
    )
    return tagging_prompt

class Classification(BaseModel):
    sentiment: str = Field(description="The sentiment of the text")
    aggressiveness: int = Field(
        description="How aggressive the text is on a scale from 1 to 10"
    )
    language: str = Field(description="The language the text is written in")

def tagging_prompt_meticulous():
    """
    Extract the desired information from the following passage.

    Only extract the properties mentioned in the 'Classification' function.

    Passage:
    {input}
    """
    return tagging_prompt

class ClassificationMeticulous(BaseModel):
    sentiment: str = Field(..., enum=["happy", "neutral", "sad"])
    aggressiveness: int = Field(
        ...,
        description="describes how aggressive the statement is, the higher the number the more aggressive",
        enum=[1, 2, 3, 4, 5],
    )
    language: str = Field(
        ..., enum=["spanish", "english", "french", "german", "italian"]
    )

try:
    # model = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini")).with_structured_output(
    #     Classification
    # )

    # tagging_chain = tagging_prompt() | model

    # inp = "Estoy increiblemente contento de haberte conocido! Creo que seremos muy buenos amigos!"
    # response = tagging_chain.invoke({"input": inp})
    # print(response)

    # inp = "Estoy muy enojado con vos! Te voy a dar tu merecido!"
    # response = tagging_chain.invoke({"input": inp})
    # print(response.dict())

    # -------------------------------------------------

    # 更细致的控制
    model_meticulous = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini")).with_structured_output(
        ClassificationMeticulous
    )
    tagging_chain_meticulous = tagging_prompt() | model_meticulous

    # inp_meticulous = "Estoy increiblemente contento de haberte conocido! Creo que seremos muy buenos amigos!"
    # response_meticulous = tagging_chain_meticulous.invoke({"input": inp_meticulous})
    # print(response_meticulous)

    # inp_meticulous = "Estoy muy enojado con vos! Te voy a dar tu merecido!"
    # tagging_chain_meticulous.invoke({"input": inp_meticulous})

    inp_meticulous = "Weather is ok here, I can go outside without much more than a coat"
    tagging_chain_meticulous.invoke({"input": inp_meticulous})

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))