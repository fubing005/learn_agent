import sys
from dotenv import load_dotenv
load_dotenv()

import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

try:
    model = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini"))

    # 定义系统提示提
    prompt = ChatPromptTemplate.from_messages(
        [("system", "Write a concise summary of the following:\\n\\n{context}")]
    )

    loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
    docs = loader.load()

    # webpage_text = """
    # Summary of areas that need clarification:\n1. Specifics of the Super Mario game (e.g. level design, characters, gameplay mechanics)\n2. Details about the MVC components (e.g. which components are in each file)\n3. Keyboard control implementation (e.g. which keys to use, how to handle input)\n\nClarifying question:\nCan you provide more details about the Super Mario game, such as level design, characters, and gameplay mechanics?
    # """
    # docs = [Document(page_content=webpage_text)]

    # 实例化链
    chain = create_stuff_documents_chain(model, prompt)

    #调用链
    # result = chain.invoke({"context": docs})
    # print(result)

    # 流式处理
    for token in chain.stream({"context": docs}):
        print(token, end="|")

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))