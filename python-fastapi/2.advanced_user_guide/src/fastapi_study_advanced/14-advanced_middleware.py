from unicorn import UnicornMiddleware
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Annotated
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# 添加 ASGI 中间件: 异步服务器网关接口
app = SomeASGIApp()
new_app = UnicornMiddleware(app, some_config="rainbow")
app = FastAPI()
app.add_middleware(UnicornMiddleware, some_config="rainbow")

# ----------------------------------------------------------

# 集成中间件
# HTTPSRedirectMiddleware： 强制所有传入请求必须是 https 或 wss
app.add_middleware(HTTPSRedirectMiddleware)

@app.get("/")
async def main_1():
    return {"message": "Hello World"}

# TrustedHostMiddleware
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"]
)
@app.get("/")
async def main_2():
    return {"message": "Hello World"}

# GZipMiddleware: 提高数据传输效率
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
@app.get("/")
async def main():
    return "somebigcontent"

