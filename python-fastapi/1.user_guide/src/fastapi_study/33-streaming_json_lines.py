from collections.abc import AsyncIterable, Iterable
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
ise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None

items = [
    Item(name="Plumbus", description="A multi-purpose household device."),
    Item(name="Portal Gun", description="A portal opening device."),
    Item(name="Meeseeks Box", description="A box that summons a Meeseeks."),
]

# 使用 StreamingResponse 返回 JSON Lines (推荐)
# 1. 编写一个生成字符串/字节流的异步生成器
async def item_generator() -> AsyncIterable[str]:
    for item in items:
        # 将 Pydantic 模型转换为 JSON 字符串，并加上换行符
        yield item.model_dump_json() + "\n"

@app.get("/items/stream")
async def stream_items():
    return StreamingResponse(item_generator(), media_type="application/x-ndjson")

@app.get("/items/stream-no-async")
def stream_items_no_async() -> Iterable[Item]:
    for item in items:
        yield item

@app.get("/items/stream-no-annotation")
async def stream_items_no_annotation():
    for item in items:
        yield item

@app.get("/items/stream-no-async-no-annotation")
def stream_items_no_async_no_annotation():
    for item in items:
        yield item
