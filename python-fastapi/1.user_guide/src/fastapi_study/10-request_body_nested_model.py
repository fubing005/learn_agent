from fastapi import Body, FastAPI
from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated

# 请求体 - 嵌套模型
app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list = []  #  list[str] = [] | set[str] = set()

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

# --------------------------------------------

# 嵌套模型
# {
#     "name": "Foo",
#     "description": "The pretender",
#     "price": 42.0,
#     "tax": 3.2,
#     "tags": ["rock", "metal", "bar"],
#     "image": {
#         "url": "http://example.com/baz.jpg",
#         "name": "The Foo live"
#     }
# }
class Image(BaseModel):
    url: str
    name: str
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

# --------------------------------------------

# 特殊的类型和校验
class Image(BaseModel):
    url: HttpUrl # 该字符串将被检查是否为有效的 URL，并在 JSON Schema / OpenAPI 文档中进行记录
    name: str
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

# --------------------------------------------

# 带有一组子模型的属性
class Image(BaseModel):
    url: HttpUrl
    name: str
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

# --------------------------------------------

# 深度嵌套模型
class Image(BaseModel):
    url: HttpUrl
    name: str
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None
class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]
@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer

# --------------------------------------------

# 纯列表请求体
# [
#   {
#     "url": "https://example.com/",
#     "name": "string"
#   }
# ]
class Image(BaseModel):
    url: HttpUrl
    name: str
@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images

# --------------------------------------------

# 任意 dict 构成的请求体
@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights
