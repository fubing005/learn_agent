from fastapi import FastAPI, Query
from pydantic import BaseModel
from enum import Enum
from typing import Any
from typing import Annotated
import random
from pydantic import AfterValidator, BeforeValidator

app = FastAPI()

@app.get("/items/")
async def read_items(q: str | None = None):
    results: dict[str, Any] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 额外校验
# Annotated 是 Python 3.9+ 引入的类型元数据注解工具
# 允许你在声明变量类型（如 str | None）的同时，在后面附带一些额外的“备注信息”或“验证规则”。
# 默认值 ： Annotated[str, Query()] = "rick"
@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
    results: dict[str, Any] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 添加更多校验
@app.get("/items/")
async def read_items(
    q: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
):
    results: dict[str, Any] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------
    
# 添加正则表达式
@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")
    ] = None,
):
    results: dict[str, Any] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 默认值
@app.get("/items/")
async def read_items(q: Annotated[str, Query(min_length=3)] = "fixedquery"):
    results: dict[str, Any] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 必填参数 q: str, 而不是 q: str | None = None 
@app.get("/items/")
async def read_items(q: Annotated[str, Query(min_length=3)]):
    results: dict[str, Any] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 必填，但可以为 None
@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(min_length=3)]):
    results: dict[str, Any] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 查询参数列表 / 多个值 [http://localhost:8000/items/?q=foo&q=bar]
# {
#   "q": [
#     "foo",
#     "bar"
#   ]
# }
@app.get("/items/")
async def read_items(q: Annotated[list[str] | None, Query()] = None):
    query_items = {"q": q}
    return query_items

# --------------------------------------------

# 具有默认值的查询参数列表 / 多个值
@app.get("/items/")
async def read_items(q: Annotated[list[str], Query()] = ["foo", "bar"]):
    query_items = {"q": q}
    return query_items

# --------------------------------------------

# 只使用 list
@app.get("/items/")
async def read_items(q: Annotated[list, Query()] = []):
    query_items = {"q": q}
    return query_items

# --------------------------------------------

# 声明更多元数据
@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None,
        Query(
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
        ),
    ] = None,
):
    results: dict[str, Any] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 别名参数
@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(alias="item-query")] = None):
    results: dict[str, Any] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 弃用参数
# 现在假设你不再喜欢这个参数了
# 由于还有客户端在使用它，你不得不保留一段时间，但你希望文档清楚地将其展示为已弃用
@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None,
        Query(
            alias="item-query",
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True,
        ),
    ] = None,
):
    results: dict[str, Any] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 从 OpenAPI 中排除参数
# 要把某个查询参数从生成的 OpenAPI 模式中排除（从而也不会出现在自动文档系统中），将 Query 的参数 include_in_schema 设为 False
@app.get("/items/")
async def read_items(
    hidden_query: Annotated[str | None, Query(include_in_schema=False)] = None,
):
    if hidden_query:
        return {"hidden_query": hidden_query}
    else:
        return {"hidden_query": "Not found"}
    
# --------------------------------------------

# 自定义校验
# 有些情况下你需要做一些无法通过上述参数完成的自定义校验
# 在这些情况下，你可以使用自定义校验函数，该函数会在正常校验之后应用（例如，在先校验值是 str 之后）
data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}
def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id
@app.get("/items/")
async def read_items(
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {"id": id, "name": item}
