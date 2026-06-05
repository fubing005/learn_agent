from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Field, Session, SQLModel, create_engine
import time

app = FastAPI()

# “可调用”的实例
# 检查 bar 是否存在于 q 查询参数中
class FixedContentQueryChecker:
    def __init__(self, fixed_content: str):
        self.fixed_content = fixed_content

    def __call__(self, q: str = ""):
        if q:
            return self.fixed_content in q
        return False
    
checker = FixedContentQueryChecker("bar")  # checker(q="somequery")

@app.get("/query-checker/")
async def read_query_check(fixed_content_included: Annotated[bool, Depends(checker)]):
    return {"fixed_content_in_query": fixed_content_included}

# --------------------------------------------------------------------

# 带 yield 的依赖项、HTTPException、except 与后台任务¶
engine = create_engine("postgresql+psycopg://postgres:postgres@localhost/db")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

def get_session():
    with Session(engine) as session: # Session(engine) 处理数据库连接
        yield session

def get_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")
    # session.close() # 如果你使用的是 SQLModel（或 SQLAlchemy）并碰到这种特定用例，你可以在不再需要时显式关闭会话

def generate_stream(query: str): # 不使用数据库会话
    for ch in query:
        yield ch
        time.sleep(0.1)

@app.get("/generate", dependencies=[Depends(get_user)])
def generate(query: str):
    return StreamingResponse(content=generate_stream(query))


