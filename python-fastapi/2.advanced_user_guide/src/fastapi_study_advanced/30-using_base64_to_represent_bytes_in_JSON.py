from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()

# 如果你的应用需要接收和发送 JSON 数据，但其中需要包含二进制数据，可以将其编码为 base64。
# Pydantic bytes
class DataInput(BaseModel):
    description: str
    data: bytes

    model_config = {"val_json_bytes": "base64"}

class DataOutput(BaseModel):
    description: str
    data: bytes

    model_config = {"ser_json_bytes": "base64"}

class DataInputOutput(BaseModel):
    description: str
    data: bytes

    model_config = {
        "val_json_bytes": "base64", # 用于接收数据的 Pydantic bytes：接收json 字段自动关联data字段
        "ser_json_bytes": "base64", # 用于输出数据的 Pydantic bytes：发送json 字段自动关联data字段
    }

@app.post("/data")
def post_data(body: DataInput):
    content = body.data.decode("utf-8")
    return {"description": body.description, "content": content}

@app.get("/data")
def get_data() -> DataOutput:
    data = "hello".encode("utf-8")
    return DataOutput(description="A plumbus", data=data)

@app.post("/data-in-out")
def post_data_in_out(body: DataInputOutput) -> DataInputOutput:
    return body
