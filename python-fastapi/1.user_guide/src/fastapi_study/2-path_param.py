from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

# --------------------------------------------

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}

# --------------------------------------------

# 声明路径参数的类型
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# --------------------------------------------

# 路径顺序
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

# --------------------------------------------

# 导入 Enum 并创建继承自 str 和 Enum 的子类。
# 通过从 str 继承，API 文档就能把值的类型定义为字符串，并且能正确渲染。
# 路径参数的值是一个枚举成员
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    # model_name 本质就是 ModelName.alexnet 这个对象本身
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    # 使用 ModelName.lenet.value 也能获取值 "lenet"。
    if model_name.value == "lenet":
        # FastAPI 会非常智能地自动读取它[model_name]的 .value（即 "lenet"），并把这个纯字符串塞进 JSON 吐给浏览器
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

# --------------------------------------------

# 包含路径的路径参数[myfile.txt]
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


