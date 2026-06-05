from fastapi import FastAPI, Path, Query
from pydantic import BaseModel
from typing import Annotated,Any

app = FastAPI()

# 声明元数据
@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get")],
    q: Annotated[str | None, Query(alias="item-query")] = None,
):
    results: dict[str, Any] = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 按需对参数排序
# 让没有默认值的参数（查询参数 q）放在最前面
@app.get("/items/{item_id}")
async def read_items(q: str, item_id: int = Path(title="The ID of the item to get")):
    results: dict[str, Any] = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 按需对参数排序的技巧
# Python 不会对这个 * 做任何事，但它会知道之后的所有参数都应该作为关键字参数（键值对）来调用，也被称为 kwargs。即使它们没有默认值
@app.get("/items/{item_id}")
async def read_items(*, item_id: int = Path(title="The ID of the item to get"), q: str):
    results: dict[str, Any] = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 使用 Annotated 更好
@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get")], q: str
):
    results: dict[str, Any] = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 数值校验：大于等于
@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=1)], q: str
):
    results: dict[str, Any] = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 数值校验：大于和小于等于
@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)],
    q: str,
):
    results: dict[str, Any] = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

# --------------------------------------------

# 数值校验：浮点数、大于和小于
@app.get("/items/{item_id}")
async def read_items(
    *,
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: str,
    size: Annotated[float, Query(gt=0, lt=10.5)],
):
    results: dict[str, Any] = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if size:
        results.update({"size": size})
    return results
