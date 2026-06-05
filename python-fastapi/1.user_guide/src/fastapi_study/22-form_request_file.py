from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel, Field
from typing import Annotated
from fastapi.responses import HTMLResponse

app = FastAPI()

# 把用户上传的文件一股脑地全部读取到服务器的内存中，并将这串纯二进制数据赋值给 file 变量
@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]): # 把用户上传的文件一股脑地全部读取到服务器的内存中，并将这串纯二进制数据赋值给 file 变量
    return {"file_size": len(file)}

# 如果文件很小，它会呆在内存里
# 如果文件超过了内存上限（通常是 1 MB 左右），FastAPI 会自动在硬盘里创建一个临时文件，把数据流式（Stream）写入硬盘
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile): # 使用这个方法
    return {"filename": file.filename}

# --------------------------------------------

# 可选文件上传
@app.post("/files/")
async def create_file(file: Annotated[bytes | None, File()] = None):
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}
    
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile | None = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}

# --------------------------------------------

# 带有额外元数据的 UploadFile
@app.post("/files/")
async def create_file(file: Annotated[bytes, File(description="A file read as bytes")]):
    return {"file_size": len(file)}

@app.post("/uploadfile/")
# 将 File() 与 UploadFile 一起使用，例如，设置额外的元数据
async def create_upload_file(
    file: Annotated[UploadFile, File(description="A file read as UploadFile")],
):
    return {"filename": file.filename}

# --------------------------------------------

# 多文件上传
@app.post("/files/")
async def create_files(files: Annotated[list[bytes], File()]):
    return {"file_sizes": [len(file) for file in files]}

@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}

@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

# --------------------------------------------

# 带有额外元数据的多文件上传[swagger ui files 乱码]
@app.post("/files/")
async def create_files(
    files: Annotated[list[bytes], File(description="Multiple files as bytes")],
):
    return {"file_sizes": [len(file) for file in files]}

@app.post("/uploadfiles/")
async def create_upload_files(
    files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")],
):
    return {"filenames": [file.filename for file in files]}

@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
