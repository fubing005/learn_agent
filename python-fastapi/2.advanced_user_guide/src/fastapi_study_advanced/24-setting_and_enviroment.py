from fastapi import Depends, FastAPI
# from pydantic_settings import BaseSettings, SettingsConfigDict
# from .config import Settings
from . import config
from functools import lru_cache
from typing import Annotated
from fastapi.testclient import TestClient

app = FastAPI()

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str | None = None
    items_per_user: int = 50

settings = Settings()

@app.get("/info")
async def info():
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_user": settings.items_per_user,
    }

# ----------------------------------------------------------

# 在依赖项中提供设置
# @lru_cache 是 Python 标准库 functools 中的装饰器，它的作用是：让函数只在第一次调用时真正执行，之后的调用直接返回缓存的结果，而不会重新执行函数体。
@lru_cache
def get_settings():
    return Settings()

@app.get("/info")
async def info(settings: Annotated[Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_user": settings.items_per_user,
    }

# ----------------------------------------------------------

#设置与测试
client = TestClient(app)

def get_settings_override():
    return Settings(admin_email="testing_admin@example.com")

app.dependency_overrides[get_settings] = get_settings_override

def test_app():
    response = client.get("/info")
    data = response.json()
    assert data == {
        "app_name": "Awesome API",
        "admin_email": "testing_admin@example.com",
        "items_per_user": 50,
    }

# ----------------------------------------------------------

# 读取 .env 文件
@lru_cache
def get_settings():
    return config.Settings()

@app.get("/info")
async def info(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_user": settings.items_per_user,
    }
