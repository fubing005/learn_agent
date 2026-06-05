from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

# 声明的参数不是路径参数时，路径操作函数会把该参数自动解释为“查询”参数。
# http://127.0.0.1:8000/items/?skip=0&limit=10
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit] # 0:10 分页

# --------------------------------------------

# 可选参数
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

# --------------------------------------------

# 查询参数类型转换
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q}) # item["q"] = q
    if not short: # short 被转换成了布尔值
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

# --------------------------------------------

# 多个路径和查询参数
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

# --------------------------------------------

# 必选查询参数
# 这里的查询参数 needy 是类型为 str 的必选查询参数
@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item

# --------------------------------------------

# 把一些参数定义为必选，为另一些参数设置默认值，再把其它参数定义为可选
@app.get("/items/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: int | None = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item

