
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

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
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

try:
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )

    db = SQLDatabase.from_uri("sqlite:///Chinook.db")
    
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )

    execute_query = QuerySQLDataBaseTool(db=db)
    write_query_clean = create_sql_query_chain(llm, db) | StrOutputParser() | parse_and_extract_sql
    chain = (
    RunnablePassthrough.assign(query=write_query_clean).assign(
            result=itemgetter("query") | execute_query
        )
        | answer_prompt
        | llm
        | StrOutputParser()
    )

    response_text = chain.invoke({"question": "How many employees are there"})
    print(response_text) # There are 8 employees.

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))

