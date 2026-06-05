from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

items = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    items["foo"] = {"name": "Fighters"}
    items["bar"] = {"name": "Tenders"}
    yield
    # clean up items
    items.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/items/{item_id}")
async def read_items(item_id: str):
    return items[item_id]

def test_read_items():
    # Before the lifespan starts, "items" is still empty
    assert items == {}

    with TestClient(app) as client:
        # Inside the "with TestClient" block, the lifespan starts and items added
        assert items == {"foo": {"name": "Fighters"}, "bar": {"name": "Tenders"}}

        response = client.get("/items/foo")
        assert response.status_code == 200
        assert response.json() == {"name": "Fighters"}

        # After the requests is done, the items are still there
        assert items == {"foo": {"name": "Fighters"}, "bar": {"name": "Tenders"}}
    # The end of the "with TestClient" block simulates terminating the app, so
    # the lifespan ends and items are cleaned up
    assert items == {}
    return items

# ----------------------------------------------------------

# 对于已弃用的 startup 和 shutdown 事件，可以按如下方式使用 TestClient：
items = {}

# 当应用启动的时候，自动执行下面这个函数
@app.on_event("startup")
async def startup_event():
    items["foo"] = {"name": "Fighters"}
    items["bar"] = {"name": "Tenders"}

@app.get("/items/{item_id}")
async def read_items(item_id: str):
    return items[item_id]

def test_read_items():
    # 启动应用（同时触发 startup 事件，填充数据）
    with TestClient(app) as client:
        #模拟发送一个 GET 请求到 /items/foo
        response = client.get("/items/foo")
        # 验证响应状态码是 200（即请求成功）
        assert response.status_code == 200
        # 验证返回的数据内容是否正确
        assert response.json() == {"name": "Fighters"}

'''
整体流程总结:
启动应用 → 自动填充 items → 发请求查询 /items/foo → 返回 {"name": "Fighters"} → 验证通过 ✅

为什么要做这个测试:
这个测试的核心目的是验证 startup 事件（或 lifespan）是否正确执行，以及接口是否能正常使用启动时准备好的数据。
1. 确认启动事件真的被触发了:
startup 事件负责在应用启动时初始化数据。如果它没有被正确触发，items 字典就会是空的，接口就会报错。
测试通过 with TestClient(app) as client 这种写法，模拟了应用的完整启动过程，确保 startup 事件被执行。[Testing Events]
2. 确认接口能正确读取启动时准备的数据:
response = client.get("/items/foo")
assert response.status_code == 200
assert response.json() == {"name": "Fighters"}
这两行断言验证了：
接口能正常访问（状态码 200）
接口返回的数据是正确的（内容符合预期）
3. 防止代码改动后出现意外问题:
如果以后有人修改了 startup 事件的逻辑，或者修改了接口代码，测试会自动发现问题，避免上线后才出错。
[总结一句话]:
这个测试是为了保证：应用启动 → 数据初始化 → 接口查询 这整条链路是完整且正确的。[Testing Events]
'''
