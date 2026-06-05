from fastapi import Body, FastAPI, Form
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()

# 定义 Form 参数
@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}
