from fastapi import Body, FastAPI
from typing import Union

app = FastAPI()

# 使用 Union 或 Optional
# 声明某个值可以是 str 或 None
def say_hi(name: Union[str, None]): # 或者 Optional[SomeType]
        print(f"Hi {name}!")

