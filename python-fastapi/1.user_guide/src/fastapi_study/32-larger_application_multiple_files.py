import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
from fastapi import FastAPI, Depends
from .larger_application_multiple_files.app.internal import admin
from .larger_application_multiple_files.app.routers import items, users
from .larger_application_multiple_files.app.dependencies import  get_query_token, get_token_header

app = FastAPI(dependencies=[Depends(get_query_token)])

# 使用 APIRouter 的路径操作
# 核心：将 router 注册到 app 中
app.include_router(users.router)

# 其他使用 APIRouter 的模块
app.include_router(items.router)

app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
