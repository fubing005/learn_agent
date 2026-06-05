from fastapi import FastAPI, Response
from pydantic import BaseModel
# 接受文本或字节并返回纯文本响应
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, StreamingResponse, FileResponse
import anyio
import orjson
from typing import Any

app = FastAPI()

# 默认响应类
app = FastAPI(default_response_class=HTMLResponse)

# JSON 响应: JSON 性能, 简而言之，如果你想要获得最大性能，请使用响应模型，并且不要在 路径操作装饰器 中声明 response_class
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []

@app.post("/items/")
async def create_item(item: Item) -> Item:
    return item

@app.get("/items/")
async def read_items() -> list[Item]:
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),
    ]

# --------------------------------------------------------------------

# HTML 响应
def generate_html_response():
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/items/", response_class=HTMLResponse)
async def read_items():
    return generate_html_response()

# --------------------------------------------------------------------

# PlainTextResponse
@app.get("/legacy/")
def get_legacy_data():
    data = """<?xml version="1.0"?>
    <shampoo>
    <Header>
        Apply shampoo here.
    </Header>
    <Body>
        You'll have to use soap here.
    </Body>
    </shampoo>
    """
    return Response(content=data, media_type="application/xml")

@app.get("/", response_class=PlainTextResponse)
async def main_1():
    return "Hello World"

# --------------------------------------------------------------------

# RedirectResponse
@app.get("/typer")
async def redirect_typer():
    return RedirectResponse("https://typer.tiangolo.com")

@app.get("/fastapi", response_class=RedirectResponse)
async def redirect_fastapi():
    return "https://fastapi.tiangolo.com"

@app.get("/pydantic", response_class=RedirectResponse, status_code=302)
async def redirect_pydantic():
    return "https://docs.pydantic.dev/"

# --------------------------------------------------------------------

#StreamingResponse
# 一个 async 任务只有在到达 await 时才能被取消。如果没有 await，生成器（带有 yield 的函数）无法被正确取消，即使已请求取消也可能继续运行。
# 由于这个小示例不需要任何 await 语句，我们添加 await anyio.sleep(0)，给事件循环一个处理取消的机会。
# 对于大型或无限流，这一点更为重要。
async def fake_video_streamer():
    for i in range(10):
        yield b"some fake video bytes"
        await anyio.sleep(0)

@app.get("/")
async def main_2():
    return StreamingResponse(fake_video_streamer())

# --------------------------------------------------------------------

# FileResponse
some_file_path = "large-video-file.mp4"

@app.get("/")
async def main_3():
    return FileResponse(some_file_path)

@app.get("/", response_class=FileResponse)
async def main_4():
    return some_file_path

# --------------------------------------------------------------------

# 自定义响应类【orjson：格式化响应】
class CustomORJSONResponse(Response):
    media_type = "application/json"
    def render(self, content: Any) -> bytes:
        assert orjson is not None, "orjson must be installed"
        return orjson.dumps(content, option=orjson.OPT_INDENT_2)
@app.get("/", response_class=CustomORJSONResponse)
async def main():
    return {"message": "Hello World"}
