from fastapi import Body, FastAPI
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from typing import Any

app = FastAPI()

fake_db: dict[str, Any] = {
    "item_001": {
        "title": "破冰船项目计划书",
        "timestamp": "2026-06-02T14:30:00",
        "description": "关于下一代高性能 Web 服务的架构设计文档。"
    },
    "item_002": {
        "title": "每周团队例会总结",
        "timestamp": "2026-06-01T09:00:00",
        "description": None  # 对应 Pydantic 模型中的 str | None = None
    },
}

class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None

@app.put("/items/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
    return fake_db[id]
