import pytest
from pydantic import ValidationError

from models import User

@pytest.mark.parametrize(
    "id, name, age, email, should_pass",
    [
        (1001, "张三", 25, "zhangsan@example.com", True),  # 合法
        (0, "张三", 25, "zhangsan@example.com", False),  # id<1，非法
        (1002, "A", 30, "lisi@example.com", False),  # name过短，非法
        (1003, "李四", 150, "wangwu@example.com", False),  # age>120，非法
        (1004, "王五", 35, "zhaoliu.example.com", False),  # 邮箱格式错误，非法
    ]
)
def test_user_parametrize(id, name, age, email, should_pass):
    if should_pass:
        # 合法用例，断言正常实例化
        user = User(id=id, name=name, age=age, email=email)
        assert user.id == id
        assert user.name == name
    else:
        # 非法用例，断言报错
        with pytest.raises(ValidationError):
            User(id=id, name=name, age=age, email=email)

# python -m pytest ./tests/test_pydantic_param.py -vs