from fastapi import Body, FastAPI, status
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()

@app.post("/items/", status_code=201)
async def create_item(name: str):
    return {"name": name}

# --------------------------------------------

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}
