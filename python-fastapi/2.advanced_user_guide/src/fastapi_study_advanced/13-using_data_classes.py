from fastapi import Body, FastAPI
from typing import Annotated
from dataclasses import dataclass, field  # (1)
from pydantic.dataclasses import dataclass  # (2)

app = FastAPI()

@dataclass
class Item:
    name: str
    price: float
    description: str | None = None
    tax: float | None = None

@app.post("/items/")
async def create_item(item: Item):
    return item

# --------------------------------------------------------------------

# 在 response_model 中使用数据类: 该数据类会被自动转换为 Pydantic 的数据类
@dataclass
class Item:
    name: str
    price: float
    tags: list[str] = field(default_factory=list)
    description: str | None = None
    tax: float | None = None

@app.get("/items/next", response_model=Item)
async def read_next_item():
    return {
        "name": "Island In The Moon",
        "price": 12.99,
        "description": "A place to be playin' and havin' fun",
        "tags": ["breater"],
    }

# --------------------------------------------------------------------

# 把标准的 dataclasses 替换为 pydantic.dataclasses
# 在嵌套数据结构中使用数据类
@dataclass
class Item:
    name: str
    description: str | None = None

@dataclass
class Author:
    name: str
    # default_factory=list 的作用是为 items 提供一个默认值：一个空列表 ([])。
    # default_factory 则能确保每个实例都有各自独立的列表，这种写法更安全
    items: list[Item] = field(default_factory=list)  # (3) #

@app.post("/authors/{author_id}/items/", response_model=Author)  # (4)
async def create_author_items(author_id: str, items: list[Item]):  # (5)
    return {"name": author_id, "items": items}  # (6)

@app.get("/authors/", response_model=list[Author])  # (7)
def get_authors():  # (8)
    return [  # (9)
        {
            "name": "Breaters",
            "items": [
                {
                    "name": "Island In The Moon",
                    "description": "A place to be playin' and havin' fun",
                },
                {"name": "Holy Buddies"},
            ],
        },
        {
            "name": "System of an Up",
            "items": [
                {
                    "name": "Salt",
                    "description": "The kombucha mushroom people's favorite",
                },
                {"name": "Pad Thai"},
                {
                    "name": "Lonely Night",
                    "description": "The mostests lonliest nightiest of allest",
                },
            ],
        },
    ]
