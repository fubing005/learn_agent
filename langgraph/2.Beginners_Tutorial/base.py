import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from typing import TypedDict,NotRequired

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")


try:
    model = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini"))


except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))