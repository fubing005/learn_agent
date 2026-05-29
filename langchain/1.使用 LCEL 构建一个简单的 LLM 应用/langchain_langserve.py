from dotenv import load_dotenv
import os
from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langserve import add_routes

load_dotenv()

# 1. 创建提示提模板
system_prompt = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages([
    ('system', system_prompt),
    ('user', '{text}')
])

# 2. 创建 model
model = ChatOpenAI(
    model=os.getenv("LLM_MODEL","gpt-4o-mini")
)

# 3. Create parser
parser = StrOutputParser()

# 4. 创建 LECL
chain = prompt_template | model | parser

# 4. 定义APP
app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple API server using LangChain's Runnable interfaces",
)

# 5. 增加 LECL 到路由
# http://localhost:9000/chain/playground/
add_routes(
    app,
    chain,
    path="/chain",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)