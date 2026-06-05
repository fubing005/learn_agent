
import os
from dotenv import load_dotenv
import uvicorn
from fastapi import Body, FastAPI
from pydantic import BaseModel, Field
from typing import Annotated

# 可以在设置 OpenAPI 规范和自动 API 文档 UI 中使用的以下字段
description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

app = FastAPI(
    title="ChimichangApp",
    description=description,
    summary="Deadpool's favorite app. Nuff said.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

@app.get("/items/")
async def read_items():
    return [{"name": "Katana"}]

# --------------------------------------------

# 创建标签元数据
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]
app = FastAPI(openapi_tags=tags_metadata)

@app.get("/users/", tags=["users"])
async def get_users():
    return [{"name": "Harry"}, {"name": "Ron"}]

@app.get("/items/", tags=["items"])
async def get_items():
    return [{"name": "wand"}, {"name": "flying broom"}]

# --------------------------------------------

#OpenAPI URL
app = FastAPI(openapi_url="/api/v1/openapi.json")
@app.get("/items/")
async def read_items():
    return [{"name": "Foo"}]

# --------------------------------------------

# 设置 Swagger UI 服务于 /documentation 并禁用 ReDoc
app = FastAPI(docs_url="/documentation", redoc_url=None)
@app.get("/items/")
async def read_items():
    return [{"name": "Foo"}]

