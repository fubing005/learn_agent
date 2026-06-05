from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.routing import APIRoute

app = FastAPI()

# 本指南将带你为 FastAPI 后端生成一个 TypeScript SDK
# 开源 SDK 生成器
#一个功能多样的选择是 OpenAPI Generator，它支持多种编程语言，可以根据你的 OpenAPI 规范生成 SDK。
#对于 TypeScript 客户端，Hey API 是为 TypeScript 生态打造的专用方案，提供优化的使用体验。
#你还可以在 OpenAPI.Tools 上发现更多 SDK 生成器。

#创建一个 TypeScript SDK
class Item(BaseModel):
    name: str
    price: float

class ResponseMessage(BaseModel):
    message: str

@app.post("/items/", response_model=ResponseMessage)
async def create_item(item: Item):
    return {"message": "item received"}

@app.get("/items/", response_model=list[Item])
async def get_items():
    return [
        {"name": "Plumbus", "price": 3},
        {"name": "Portal Gun", "price": 9001},
    ]

# ----------------------------------------------------------

# 带有标签的 FastAPI 应用
# 很多情况下，你的 FastAPI 应用会更大，你可能会用标签来划分不同组的路径操作。
# 例如，你可以有一个 items 相关的部分和另一个 users 相关的部分，它们可以用标签来分隔
class Item(BaseModel):
    name: str
    price: float

class ResponseMessage(BaseModel):
    message: str

class User(BaseModel):
    username: str
    email: str

@app.post("/items/", response_model=ResponseMessage, tags=["items"])
async def create_item(item: Item):
    return {"message": "Item received"}

@app.get("/items/", response_model=list[Item], tags=["items"])
async def get_items():
    return [
        {"name": "Plumbus", "price": 3},
        {"name": "Portal Gun", "price": 9001},
    ]
@app.post("/users/", response_model=ResponseMessage, tags=["users"])
async def create_user(user: User):
    return {"message": "User received"}

# 自定义唯一 ID 生成函数
def custom_generate_unique_id(route: APIRoute):
    # {标签名} - {函数名}
    return f"{route.tags[0]}-{route.name}"

app = FastAPI(generate_unique_id_function=custom_generate_unique_id)

class Item(BaseModel):
    name: str
    price: float

class ResponseMessage(BaseModel):
    message: str

class User(BaseModel):
    username: str
    email: str

@app.post("/items/", response_model=ResponseMessage, tags=["items"])
async def create_item(item: Item):
    return {"message": "Item received"}

@app.get("/items/", response_model=list[Item], tags=["items"])
async def get_items():
    return [
        {"name": "Plumbus", "price": 3},
        {"name": "Portal Gun", "price": 9001},
    ]

@app.post("/users/", response_model=ResponseMessage, tags=["users"])
async def create_user(user: User):
    return {"message": "User received"}

# ----------------------------------------------------------

# 为客户端生成器预处理 OpenAPI 规范
'''
生成的代码中仍有一些重复信息。

我们已经知道这个方法与 items 有关，因为它位于 ItemsService（来自标签），但方法名里仍然带有标签名前缀。😕

通常我们仍然希望在 OpenAPI 中保留它，以确保操作 ID 的唯一性。

但对于生成的客户端，我们可以在生成之前修改 OpenAPI 的操作 ID，只是为了让方法名更美观、更简洁。

我们可以把 OpenAPI JSON 下载到 openapi.json 文件中，然后用如下脚本移除这个标签前缀：
'''
import json
from pathlib import Path

file_path = Path("./openapi.json")
openapi_content = json.loads(file_path.read_text())

for path_data in openapi_content["paths"].values():
    for operation in path_data.values():
        tag = operation["tags"][0]
        operation_id = operation["operationId"]
        to_remove = f"{tag}-"
        new_operation_id = operation_id[len(to_remove) :]
        operation["operationId"] = new_operation_id

file_path.write_text(json.dumps(openapi_content))
# 这样，操作 ID 会从 items-get_items 之类的名字重命名为 get_items，从而让客户端生成器生成更简洁的方法名。

