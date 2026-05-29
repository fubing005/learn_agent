import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_community.document_loaders import YoutubeLoader
import datetime
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from typing import Optional, List, cast
from langchain_core.documents import Document

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")


def youtube_docs():
    urls = [
        "https://www.youtube.com/watch?v=HAn9vnJy6S4",
        "https://www.youtube.com/watch?v=dA1cHGACXCo",
        "https://www.youtube.com/watch?v=ZcEMLz27sL4",
        "https://www.youtube.com/watch?v=hvAPnpSfSGo",
        "https://www.youtube.com/watch?v=EhlPDL4QrWY",
        "https://www.youtube.com/watch?v=mmBo8nlu2j0",
        "https://www.youtube.com/watch?v=rQdibOsL1ps",
        "https://www.youtube.com/watch?v=28lC4fqukoc",
        "https://www.youtube.com/watch?v=es-9MgxB-uc",
        "https://www.youtube.com/watch?v=wLRHwKuKvOE",
        "https://www.youtube.com/watch?v=ObIltMaRJvY",
        "https://www.youtube.com/watch?v=DjuXACWYkkU",
        "https://www.youtube.com/watch?v=o7C9ld6Ln-M",
    ]
    docs = []
    for url in urls:
        docs.extend(YoutubeLoader.from_youtube_url(url, add_video_info=True).load())
    return docs

class Search(BaseModel):
    """Search over a database of tutorial videos about a software library."""

    query: str = Field(
        ...,
        description="Similarity search query applied to video transcripts.",
    )
    publish_year: Optional[int] = Field(None, description="Year video was published")

def generate_query(llm):
    system = """You are an expert at converting user questions into database queries. \
    You have access to a database of tutorial videos about a software library for building LLM-powered applications. \
    Given a question, return a list of database queries optimized to retrieve the most relevant results.

    If there are acronyms or words you are not familiar with, do not try to rephrase them."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )
    structured_llm = llm.with_structured_output(Search)
    query_analyzer = {"question": RunnablePassthrough()} | prompt | structured_llm
    return query_analyzer

def retrieval(search: Search) -> List[Document]:
    if search.publish_year is not None:
        # This is syntax specific to Chroma,
        # the vector database we are using.
        _filter = cast(dict, {"publish_year": {"$eq": search.publish_year}})
    else:
        _filter = None
    return vectorstore.similarity_search(search.query, filter=_filter)


try:
    model = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )

    # 📚 文档加载：加载 Youtube 视频文档
    docs = youtube_docs()
    for doc in docs:
        doc.metadata["publish_year"] = int(
            datetime.datetime.strptime(
                doc.metadata["publish_date"], "%Y-%m-%d %H:%M:%S"
            ).strftime("%Y")
        )
    # print(docs[0].metadata)
    # print(docs[0].page_content[:500])

    # 索引文档
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
    chunked_docs = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        chunked_docs,
        embeddings,
    )

    # 无查询分析的检索
    search_results = vectorstore.similarity_search("how do I build a RAG agent")
    print(search_results[0].metadata["title"])
    print(search_results[0].page_content[:500])

    # 搜索特定时间段的结果
    search_results = vectorstore.similarity_search("videos on RAG published in 2023")
    print(search_results[0].metadata["title"])
    print(search_results[0].metadata["publish_date"])
    print(search_results[0].page_content[:500])

    # 查询模式
    query_analyzer = generate_query(model)
    query_analyzer.invoke("how do I build a RAG agent") # Search(query='build RAG agent', publish_year=None)
    query_analyzer.invoke("videos on RAG published in 2023") # Search(query='RAG', publish_year=2023)

    # 使用查询分析进行检索
    retrieval_chain = query_analyzer | retrieval
    results = retrieval_chain.invoke("RAG tutorial published in 2023")
    [(doc.metadata["title"], doc.metadata["publish_date"]) for doc in results]
    '''
        [
            ('Getting Started with Multi-Modal LLMs', '2023-12-20 00:00:00'),
            ('LangServe and LangChain Templates Webinar', '2023-11-02 00:00:00'),
            ('Getting Started with Multi-Modal LLMs', '2023-12-20 00:00:00'),
            ('Building a Research Assistant from Scratch', '2023-11-16 00:00:00')
        ]
    '''

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))