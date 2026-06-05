
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import Annotated

# pdm run fastapi dev --port 8080 --forwarded-allow-ips="*" --root-path /api/v1
app = FastAPI()
# app = FastAPI(root_path="/api/v1")

# 在很多情况下，你会在 FastAPI 应用前面使用像 Traefik 或 Nginx 这样的代理
# 这些代理可以处理 HTTPS 证书等事项。

# 查看当前的 root_path
# http://127.0.0.1:8080/app
@app.get("/app")
def read_main_1(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}

# ----------------------------------------------------------

# 附加的服务器
app = FastAPI(
    servers=[
        {"url": "https://stag.example.com", "description": "Staging environment"},
        {"url": "https://prod.example.com", "description": "Production environment"},
    ],
    root_path="/api/v1",
)

@app.get("/app")
def read_main_2(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}

# ----------------------------------------------------------

# 从 root_path 禁用自动服务器
app = FastAPI(
    servers=[
        {"url": "https://stag.example.com", "description": "Staging environment"},
        {"url": "https://prod.example.com", "description": "Production environment"},
    ],
    root_path="/api/v1",
    root_path_in_servers=False,
)

@app.get("/app")
def read_main(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}
