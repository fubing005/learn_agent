
import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_classic.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
import ast
from langchain_classic.tools.retriever import create_retriever_tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL","LLM_EMBEDDING_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")


# 1. 🎯 核心武器：写一个哪怕模型吐出一万字废话，也能精准把 SQL 抠出来的硬核清洗函数
def parse_and_extract_sql(text: str) -> str:
    """提取大段文本中被 ```sql 块包裹的内容；如果没包，就用正则抓取 SELECT 核心语句"""
    if not text:
        return ""
    
    # 尝试提取 ```sql ... ``` 里面的核心内容
    markdown_match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if markdown_match:
        return markdown_match.group(1).strip()
        
    # 如果大模型连 ```sql 都没加，直接用正则从 SELECT 到分号或结尾抓取
    sql_match = re.search(r"(SELECT\s+.*)", text, re.DOTALL | re.IGNORECASE)
    if sql_match:
        # 去掉结尾可能粘连的 Markdown 符号
        return sql_match.group(1).replace("```", "").strip()
        
    # 如果实在什么都没匹配到，交由原字符串兜底
    return text.strip()

def sql_prefix ():
    SQL_PREFIX = """You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the below tools. Only use the information returned by the below tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    To start you should ALWAYS look at the tables in the database to see what you can query.
    Do NOT skip this step.
    Then you should query the schema of the most relevant tables."""

    sql_prefix = SystemMessage(content=SQL_PREFIX)

    return sql_prefix

def query_as_list(db, query):
    res = db.run(query)
    res = [el for sub in ast.literal_eval(res) for el in sub if el]
    res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
    return list(set(res))

try:
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )

    db = SQLDatabase.from_uri("sqlite:///Chinook.db")
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    # agent_executor = create_agent(llm, tools, system_prompt=sql_prefix())

    # 代理如何回应以下问题
    # for s in agent_executor.stream(
    #     {"messages": [HumanMessage(content="Which country's customers spent the most?")]}
    # ):
    #     print(s)
    #     print("----")

    # 代理可以处理定性问题
    # for s in agent_executor.stream(
    #     {"messages": [HumanMessage(content="Describe the playlisttrack table")]}
    # ):
    #     print(s)
    #     print("----")

    # 处理高基数列
    artists = query_as_list(db, "SELECT Name FROM Artist")
    albums = query_as_list(db, "SELECT Title FROM Album")
    # print(albums[:5])

    # 1. 组合数据
    all_texts = artists + albums
    # 2. 🌟 本地Debug测试：先只切前 10 条，看看卡不卡住！
    # 如果前 10 条秒过，说明代码和网络没问题，单纯是数据量太大的网络延迟
    print(f"从数据库捞出数据完毕。Artist: {len(artists)} 条, Album: {len(albums)} 条，总计: {len(all_texts)} 条。")

    test_texts = all_texts[:10] 
    vector_db = FAISS.from_texts(test_texts, OpenAIEmbeddings())
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    description = """Use to look up values to filter on. Input is an approximate spelling of the proper noun, output is \
    valid proper nouns. Use the noun most similar to the search."""
    retriever_tool = create_retriever_tool(
        retriever,
        name="search_proper_nouns",
        description=description,
    )
    # print(retriever_tool.invoke("Alice Chains"))

    # 结合使用
    tools.append(retriever_tool)
    agent_executor = create_agent(llm, tools, system_prompt=sql_prefix())
    for s in agent_executor.stream(
        {"messages": [HumanMessage(content="How many albums does alis in chain have?")]}
    ):
        print(s)
        print("----")

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))

