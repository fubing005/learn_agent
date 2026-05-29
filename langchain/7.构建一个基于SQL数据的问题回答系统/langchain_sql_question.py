
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
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")


# sql 清洗函数
def parse_clean_sql(text: str) -> str:
    """极其硬核的 SQL 文本清洗函数，100% 剥离大模型自带的所有 Markdown 标签和提示词前缀"""
    if not text:
        return ""
    
    # 1. 去除两端的不可见空格和换行符
    sql = text.strip()
    
    # 2. 剥离 Markdown 代码块外壳 (如 ```sql ... ```)
    sql = re.sub(re.compile(r"^```sql\s*", re.IGNORECASE), "", sql)
    sql = re.sub(re.compile(r"^```\s*"), "", sql)
    sql = re.sub(re.compile(r"\s*```$"), "", sql)
    
    # 3. 🎯 彻底消灭图片中的罪魁祸首：清除大模型吐出的 "SQLQuery:", "SQL:" 等任意提示前缀
    sql = re.sub(re.compile(r"^(sqlquery|sql|query|answer):\s*", re.IGNORECASE), "", sql.strip())
    
    # 4. 返回绝对纯净的 SQL 字符串
    return sql.strip()


try:
    model = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )

    db = SQLDatabase.from_uri("sqlite:///Chinook.db")
    # print(db.dialect) # 打印数据库类型
    # print(db.get_usable_table_names()) # 列出数据库所有表名
    # db.run("SELECT * FROM Artist LIMIT 10;")

    # # 2. 🎯 用管道符 | 把【模型】、【字符串解析器】、【清洗函数】串联起来
    # # 数据流向：Prompt -> Model -> StrOutputParser(转字符串) -> parse_clean_sql(剥壳)
    # chain = create_sql_query_chain(model, db)  | StrOutputParser() | parse_clean_sql
    # response = chain.invoke({"question": "How many employees are there"})
    # print("SQL: ", response) 
    # result = db.run(response)
    # print("查询结果:", result)

    # # 3. 🎯 打印出链的各个组件
    # chain.get_prompts()[0].pretty_print()

    #使用 QuerySQLDatabaseTool 来轻松地将查询执行添加到我们的链中
    execute_query = QuerySQLDataBaseTool(db=db)
    write_query = create_sql_query_chain(model, db)  | StrOutputParser() | parse_clean_sql
    chain = write_query | execute_query
    response = chain.invoke({"question": "How many employees are there"})
    print(response)

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))

