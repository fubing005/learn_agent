from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()

# 定义 File 与 Form 参数
@app.post("/files/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }
