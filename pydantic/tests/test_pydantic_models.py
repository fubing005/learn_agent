# ./tests/test_pydantic_models.py
import pytest
from pydantic import ValidationError

from models import User  # 从业务模块导入需要测试的Pydantic模型

# ---------------------- 测试用户模型 ----------------------
class TestUserModel:
    # 合法用例：正常实例化，验证字段值正确
    def test_user_valid(self):
        user = User(id=1001, name="张三", age=25, email="zhangsan@example.com")
        assert user.id == 1001
        assert user.name == "张三"
        assert user.age == 25
        assert user.email == "zhangsan@example.com"

    # 非法用例：id小于1，验证报错
    def test_user_invalid_id(self):
        with pytest.raises(ValidationError) as e:
            User(id=0, name="张三", age=25, email="zhangsan@example.com")
        # 断言错误类型为greater_than_or_equal
        assert "greater_than_or_equal" in str(e.value)
        # 断言错误字段为id
        assert "id" in str(e.value)

    # 非法用例：name长度不足，验证报错
    def test_user_invalid_name_length(self):
        with pytest.raises(ValidationError) as e:
            User(id=1002, name="A", age=30, email="lisi@example.com")
        assert "string_min_length" in str(e.value)
        assert "name" in str(e.value)

    # 非法用例：邮箱格式错误，验证报错
    def test_user_invalid_email(self):
        with pytest.raises(ValidationError) as e:
            User(id=1003, name="李四", age=35, email="lisi.example.com")
        assert "value_error" in str(e.value)
        assert "email" in str(e.value)

# python -m pytest ./tests/test_pydantic_models.py -v

