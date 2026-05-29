import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
import getpass
from langchain_document import documents
from langchain_core.runnables import RunnableLambda
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# 激活 LangChain 官方的“可视化调试与监控服务”（称为 LangSmith），并安全地输入你的服务秘钥
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = getpass.getpass()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

try:
    model = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )

    # 调用 .from_documents 将把文档添加到向量存储中
    vectorstore = Chroma.from_documents(
        documents,
        #model=os.getenv("LLM_EMBEDDING_MODEL","")
        embedding=OpenAIEmbeddings(), 
    )

    # 自己创建一个简单版本，而无需继承 Retriever
    # retriever = RunnableLambda(vectorstore.similarity_search).bind(k=1)  # select top result
    # print(retriever.batch(["cat", "shark"]))

    #向量存储实现了一个 as_retriever 方法，该方法将生成一个检索器，特别是一个 VectorStoreRetriever。
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 1},
    )
    print(retriever.batch(["cat", "shark"]))
except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))