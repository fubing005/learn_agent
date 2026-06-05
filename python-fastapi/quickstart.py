import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

required_env_vars = ["ENVIROMENT"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

if os.getenv("ENVIROMENT") == 'production':
     # 生产环境 uvicorn
    # python main.py
    if __name__ == "__main__":
        uvicorn.run(app,host="0.0.0.0",port=8080)
elif os.getenv("ENVIROMENT") == 'local':
   # fastapi dev main.py --port 8080
   pass

