import pytest
from httpx import ASGITransport, AsyncClient

# import sys
# import os
# # 动态添加 src 到 sys.path
# sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from fastapi_study_advanced.asynchronous import app

# '''
# pdm run pytest tests/test_asynchronous.py -v
# pdm run pytest tests/test_asynchronous.py -s
# '''

@pytest.mark.anyio
async def test_root():
    async with AsyncClient(
        # 为什么 base_url 设置成 "http://test" 而不是 "http://127.0.0.1"
        # 这是因为这里使用的是 ASGITransport，请求根本不会真正发送到网络上，所以 base_url 填什么地址都不影响实际连接。
        # ASGITransport(app=app) 的意思是：直接在内存中调用你的 FastAPI 应用，完全绕过网络和 socket
        # 请求不会经过 127.0.0.1，也不会经过任何真实的网络端口
        # base_url 只是一个格式上的占位符，让 HTTPX 构造合法的 HTTP 请求头用的，填 "http://test" 或者 "http://localhost" 效果完全一样
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Tomato"}