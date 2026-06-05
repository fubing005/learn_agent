from fastapi import Header, FastAPI
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()

# 声明 Header 参数
@app.get("/items/")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent} # 获取请求的浏览器信息

# 自动转换 ： Header 比 Path、Query 和 Cookie 提供了更多功能
# convert_underscores=True: 将 strange_header 自动转换为浏览器的 strange-header
# convert_underscores=False: 关闭后，FastAPI 就不会把下划线变减号了，它会老老实实去请求头里寻找一模一样带下划线的参数
@app.get("/items/")
async def read_items(
    strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
):
    return {"strange_header": strange_header}

# --------------------------------------------

# 重复的请求头
@app.get("/items/")
async def read_items(x_token: Annotated[list[str] | None, Header()] = None):
    return {"X-Token values": x_token}

