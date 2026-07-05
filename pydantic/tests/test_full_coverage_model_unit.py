# 安装依赖：pip install pytest
import pytest
from pydantic import BaseModel, PositiveInt


class Product(BaseModel):
    id: PositiveInt  # 大于 0 的整数
    name: str
    price: float = 0.0


# 单元测试用例
def test_product_valid():
    # 合法数据
    prod = Product(id=1, name="手机", price=1999.9)
    assert prod.id == 1


# 非法id（非正整数），触发校验报错
def test_product_invalid_id():
    # pytest.raises(ValueError) 的作用是：期望代码抛出 ValueError 异常。
    with pytest.raises(ValueError) as ex:
        Product(id=0, name="耳机")
    # 错误信息包含"Input should be greater than 0"，成功捕获到了异常，所以测试通过
    assert "Input should be greater than 0" in str(ex.value)


# 缺少必填字段name，触发报错
def test_product_missing_name():
    # pytest.raises(ValueError) 的作用是：期望代码抛出 ValueError 异常。
    with pytest.raises(ValueError) as ex:
        Product(id=2, price=99.9)
    # 错误信息包含"Field required"，成功捕获到了异常，所以测试通过
    assert "Field required" in str(ex.value)

#python -m pytest ./tests/test_full_coverage_model_unit.py -v
