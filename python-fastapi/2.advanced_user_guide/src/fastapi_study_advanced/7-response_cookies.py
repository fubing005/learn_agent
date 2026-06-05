from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI()

# 使用 Response 参数
@app.post("/cookie-and-object/")
def create_cookie(response: Response):
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return {"message": "Come to the dark side, we have cookies"}

# --------------------------------------------------------------------

# 直接响应 Response
@app.post("/cookie/")
def create_cookie():
    content = {"message": "Come to the dark side, we have cookies"}
    response = JSONResponse(content=content)
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return response
