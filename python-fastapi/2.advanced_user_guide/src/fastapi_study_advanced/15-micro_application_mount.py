from fastapi import Body, FastAPI
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()     # http://127.0.0.1:8080/docs#/
subapi = FastAPI()  # http://127.0.0.1:8080/subapi/docs#/
app.mount("/subapi", subapi)  

# 如果需要两个独立的 FastAPI 应用，拥有各自独立的 OpenAPI 与文档，
# 则需设置一个主应用，并挂载一个（或多个）子应用
# 挂载 FastAPI 应用
@app.get("/app")
def read_main():
    return {"message": "Hello World from main app"}

@subapi.get("/sub")
def read_sub():
    return {"message": "Hello World from sub API"}

