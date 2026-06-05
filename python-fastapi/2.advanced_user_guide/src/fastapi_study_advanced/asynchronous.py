from fastapi import Body, FastAPI
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()

#异步测试 
@app.get("/")
async def root():
    return {"message": "Tomato"}
