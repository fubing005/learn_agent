from fastapi import Body, FastAPI
from pydantic import BaseModel, Field
from typing import Annotated
from contextlib import asynccontextmanager

app = FastAPI()

ml_models = {}
def fake_answer_to_everything_ml_model(x: float):
    return x * 42
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行 (原 startup)
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    yield
     # 关闭时执行 (原 shutdown)
    ml_models.clear()
app = FastAPI(lifespan=lifespan)
@app.get("/predict")
async def predict(x: float):
    result = ml_models["answer_to_everything"](x)
    return {"result": result}

# ----------------------------------------------------------

# startup 事件: 使用事件 "startup" 声明一个在应用启动前运行的函数
items = {}

#startup: 过时了： 现在使用lifespan
@app.on_event("startup")
async def startup_event():
    items["foo"] = {"name": "Fighters"}
    items["bar"] = {"name": "Tenders"}
@app.get("/items/{item_id}")
async def read_items_1(item_id: str):
    return items[item_id]

#shutdown: 过时了： 现在使用lifespan
@app.on_event("shutdown")
def shutdown_event():
    with open("log.txt", mode="a") as log:
        log.write("Application shutdown")
@app.get("/items/")
async def read_items_2():
    return [{"name": "Foo"}]

# ----------------------------------------------------------

# startup 和 shutdown 一起使用
'''
startup 和 shutdown 一起使用
启动和关闭的逻辑很可能是连接在一起的，你可能希望启动某个东西然后结束它，获取一个资源然后释放它等等。
在不共享逻辑或变量的不同函数中处理这些逻辑比较困难，因为你需要在全局变量中存储值或使用类似的方式。
因此，推荐使用上面所述的 lifespan。
'''
'''
子应用¶
🚨 请注意，这些生命周期事件（startup 和 shutdown）只会在主应用上执行，
不会在子应用 - 挂载上执行
'''