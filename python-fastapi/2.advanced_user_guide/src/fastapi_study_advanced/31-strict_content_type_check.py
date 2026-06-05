from fastapi import Body, FastAPI
from pydantic import BaseModel, Field
from typing import Annotated

# 允许无 Content-Type 的请求
app = FastAPI(strict_content_type=False)

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item
