import os
from dotenv import load_dotenv
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from sqlalchemy import text

load_dotenv()

required_env_vars = ["ENVIROMENT"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

app = FastAPI()

# # 共享查询参数
# async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
#     return {"q": q, "skip": skip, "limit": limit}
# @app.get("/items/")
# async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
#     return commons
# @app.get("/users/")
# async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
#     return commons

# # 共享 Annotated 依赖项
# async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
#     return {"q": q, "skip": skip, "limit": limit}
# CommonsDep = Annotated[dict, Depends(common_parameters)]
# @app.get("/items/")
# async def read_items(commons: CommonsDep):
#     return commons
# @app.get("/users/")
# async def read_users(commons: CommonsDep):
#     return commons

# # 使用 yield 的子依赖项
# # 模拟资源 A
# class ResourceA:
#     def __init__(self):
#         self.name = "ResourceA"
#         print(f"{self.name} initialized")
#     def close(self):
#         print(f"{self.name} closed")
# # 模拟资源 B
# class ResourceB:
#     def __init__(self):
#         self.name = "ResourceB"
#         print(f"{self.name} initialized")
#     def close(self, resource_a):
#         print(f"{self.name} closed and cleaned up with {resource_a.name}")
# # 模拟资源 C
# class ResourceC:
#     def __init__(self):
#         self.name = "ResourceC"
#         print(f"{self.name} initialized")
#     def close(self, resource_b):
#         print(f"{self.name} closed and cleaned up with {resource_b.name}")
# # 生成 ResourceA 的函数
# def generate_dep_a():
#     return ResourceA()
# # 生成 ResourceB 的函数
# def generate_dep_b():
#     return ResourceB()
# # 生成 ResourceC 的函数
# def generate_dep_c():
#     return ResourceC()
# async def dependency_a():
#     dep_a = generate_dep_a()
#     try:
#         yield dep_a
#     finally:
#         dep_a.close()
# async def dependency_b(dep_a=Depends(dependency_a)):
#     dep_b = generate_dep_b()
#     try:
#         yield dep_b
#     finally:
#         dep_b.close(dep_a)
# async def dependency_c(dep_b=Depends(dependency_b)):
#     dep_c = generate_dep_c()
#     try:
#         yield dep_c
#     finally:
#         dep_c.close(dep_b)
# # 示例 API 路由
# @app.get("/use-resources")
# async def use_resources(dep_c=Depends(dependency_c)):
#     # 逻辑处理，比如直接返回依赖链的各个资源的名字
#     return {"message": f"Successfully accessed dependencies: {dep_c.name}"}

# # 同时使用 yield 和 HTTPException 的依赖项
data = {
    "plumbus": {"description": "Freshly pickled plumbus", "owner": "Morty"},
    "portal-gun": {"description": "Gun to create portals", "owner": "Rick"},
}
# class OwnerError(Exception):
#     pass
# def get_username():
#     try:
#         yield "Rick"
#     except OwnerError as e:
#         raise HTTPException(status_code=400, detail=f"Owner error: {e}")
# @app.get("/items/{item_id}")
# def get_item(item_id: str, username: Annotated[str, Depends(get_username)]):
#     if item_id not in data: # plumbu
#         raise HTTPException(status_code=404, detail="Item not found") # {"detail": "Item not found"}
#     item = data[item_id]
#     if item["owner"] != username:
#         raise OwnerError(username) # {"detail": "Owner error: Rick"}
#     return item

# # 同时使用 yield 和 except 的依赖项
# # 如果你在带有 yield 的依赖中使用 except 捕获了一个异常，并且你没有再次抛出它（或抛出一个新异常），FastAPI 将无法察觉发生过异常，就像普通的 Python 代码那样
class InternalError(Exception):
    pass
# def get_username():
#     try:
#         yield "Rick"
#     except InternalError as e:
#         print("Oops, we didn't raise again, Britney 😱")
# @app.get("/items/{item_id}")
# def get_item(item_id: str, username: Annotated[str, Depends(get_username)]):
#     if item_id == "portal-gun":
#         raise InternalError(
#             f"The portal gun is too dangerous to be owned by {username}"
#         ) # Internal Server Error
#     if item_id != "plumbus":
#         raise HTTPException(
#             status_code=404, detail="Item not found, there's only a plumbus here"
#         )
#     return item_id

# # 在带有 yield 和 except 的依赖中务必 raise
# # 现在客户端仍会得到同样的 HTTP 500 Internal Server Error 响应，但服务器日志中会有我们自定义的 InternalError
# def get_username():
#     try:
#         yield "Rick"
#     except InternalError:
#         print("We don't swallow the internal error here, we raise again 😎")
#         raise
# @app.get("/items/{item_id}")
# def get_item(item_id: str, username: Annotated[str, Depends(get_username)]):
#     if item_id == "portal-gun":
#         raise InternalError(
#             f"The portal gun is too dangerous to be owned by {username}"
#         )
#     if item_id != "plumbus":
#         raise HTTPException(
#             status_code=404, detail="Item not found, there's only a plumbus here"
#         )
#     return item_id

# # 提前退出与 scope
# # 通常，带有 yield 的依赖的退出代码会在响应发送给客户端之后执行。
# # 但如果你知道在从 路径操作函数 返回之后不再需要使用该依赖，你可以使用 Depends(scope="function") 告诉 FastAPI：应当在 路径操作函数 返回后、但在响应发送之前关闭该依赖
# def get_username():
#     try:
#         yield "Rick"
#     finally:
#         print("Cleanup up before response is sent")
# @app.get("/users/me")
# def get_user_me(username: Annotated[str, Depends(get_username, scope="function")]):
#     return username

# # 什么是“上下文管理器”
# # “上下文管理器”是你可以在 with 语句中使用的任意 Python 对象。
# # 在底层，open("./somefile.txt") 会创建一个“上下文管理器”对象。
# # 当 with 代码块结束时，它会确保文件被关闭，即使期间发生了异常。
# # 当你用 yield 创建一个依赖时，FastAPI 会在内部为它创建一个上下文管理器，并与其他相关工具结合使用。
# with open("./somefile.txt") as f:
#     contents = f.read()
#     print(contents)


# 在带有 yield 的依赖中使用上下文管理器
# 创建一个异步数据库引擎（此处使用 SQLite 示例，你可以替换为你的实际数据库 URL）
DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # 换成你的数据库连接字符串
engine = create_async_engine(DATABASE_URL, echo=True)

# 建立 SessionMaker，用于生成 AsyncSession
async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# DBSession 是与数据库连接的会话类
class DBSession:
    def __init__(self):
        # 创建一个会话实例（懒加载）
        self.session = async_session_maker()

    async def close(self):
        """关闭数据库连接"""
        await self.session.close()

    async def commit(self):
        """提交事务"""
        await self.session.commit()

    async def rollback(self):
        """回滚事务"""
        await self.session.rollback()

    # 方便在 DBSession 上直接调用查询
    def __getattr__(self, item):
        return getattr(self.session, item)

class MySuperContextManager:
    def __init__(self):
        self.db: DBSession | None = None

    async def __aenter__(self):
        """异步进入上下文，初始化和获取 DBSession"""
        self.db = DBSession()  # 创建数据库会话
        return self.db

    async def __aexit__(self, exc_type, exc_value, traceback):
        """异步退出上下文，处理资源清理"""
        if self.db is not None:  # 确保数据库会话已初始化
            if exc_type:  # 如果有异常，执行回滚
                await self.db.rollback()
            await self.db.close()  # 不管是否有异常，都要关闭会话

# get_db 函数使用 yield 返回数据库会话，作为 FastAPI 的依赖项。
async def get_db() -> AsyncGenerator[DBSession, None]:
    """获取数据库会话的异步生成器"""
    async with MySuperContextManager() as db:
        yield db

@app.get("/items/")
async def read_items(db: DBSession = Depends(get_db)):
    """从数据库中查询数据示例"""
    async with db.session.begin():  # 进入数据库事务
        result = await db.session.execute(text("SELECT * FROM items"))  # 示例查询
        items = result.fetchall()
    return {"items": items}


if os.getenv("ENVIROMENT") == 'production':
     # 生产环境 uvicorn
    # python main.py
    if __name__ == "__main__":
        uvicorn.run(app,host="0.0.0.0",port=8080)
elif os.getenv("ENVIROMENT") == 'local':
   # fastapi dev main.py --port 8080
   pass

