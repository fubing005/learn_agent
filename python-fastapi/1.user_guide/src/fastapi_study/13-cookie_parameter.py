from fastapi import Cookie, FastAPI
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()

@app.get("/items/")
async def read_items(ads_id: Annotated[str | None, Cookie()] = None):
    return {"ads_id": ads_id}

