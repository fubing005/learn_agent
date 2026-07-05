import re
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    id: int = Field(ge=1, description="用户 ID")
    name: str = Field(min_length=2, max_length=20, description="用户名，2-20 字符")
    age: Optional[int] = Field(default=None, ge=0, le=120, description="年龄，0-120")
    email: str = Field(description="合法邮箱格式")
    is_valid: bool = Field(default=True, description="用户状态")

    @classmethod
    @field_validator('email')
    def validate_email(cls, v: str) -> str:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('无效的邮箱格式')
        return v
