import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_classic.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import WebBaseLoader
from bs4.filter import SoupStrainer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

# 对话式代理构造器
def proxy_constructor(model, tools, thread_id=None):
    # agent_executor = create_agent(model, tools)

    # 我们现在可以试一试。请注意，到目前为止它是无状态的（我们仍然需要添加内存）
    # query = "What is Task Decomposition?"
    # for s in agent_executor.stream(
    #     {"messages": [HumanMessage(content=query)]},
    # ):
    #     print(s)
    #     print("----")


    memory = MemorySaver()
    agent_executor = create_agent(model, tools,checkpointer=memory)
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    # 输入一个需要检索步骤的查询
    # for s in agent_executor.stream(
    #     {"messages": [HumanMessage(content="Hi! I'm bob")]}, config=config
    # ):
    #     print(s)
    #     print("----")

    # 输入一个需要检索步骤的查询
    # query = "What is Task Decomposition?"
    # for s in agent_executor.stream(
    #     {"messages": [HumanMessage(content=query)]}, config=config
    # ):
    #     print(s)
    #     print("----")

    # 允许代理在必要时使用对话的上下文
    query = "What according to the blog post are common ways of doing it? redo the search"
    for s in agent_executor.stream(
        {"messages": [HumanMessage(content=query)]}, config=config
    ):
        print(s)
        print("----")

try:
    model = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )

    loader = WebBaseLoader(
        web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
        bs_kwargs=dict(
            parse_only=SoupStrainer(
                class_=("post-content", "post-title", "post-header")
            )
        ),
    )
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()

    tool = create_retriever_tool(
        retriever,
        "blog_post_retriever",
        "Searches and returns excerpts from the Autonomous Agents blog post.",
    )
    tools = [tool]
    # response_text = tool.invoke("task decomposition")
    # print(response_text)

    # 代理构造器
    proxy_constructor(model, tools, "abc123")


except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))