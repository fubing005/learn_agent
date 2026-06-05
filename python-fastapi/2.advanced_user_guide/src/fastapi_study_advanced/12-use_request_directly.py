from fastapi import FastAPI, Request

app = FastAPI()

# 直接使用 Request 对象
@app.get("/items/{item_id}")
def read_root(item_id: str, request: Request):
    client = request.client
    if client:
        client_host = client.host
    else:
        client_host = "Unknown"  # 或者根据实际需要给一个默认值
    return {"client_host": client_host, "item_id": item_id}
