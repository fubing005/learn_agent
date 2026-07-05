'''
https://blog.csdn.net/inuex/article/details/159608645

一、基础准备：核心概念
Pydantic 是 Python 生态中数据验证与数据解析的标杆库，V2 版本核心基于 Rust 重写，在保持易用性的同时，性能比 V1 提升 5-50 倍，是 FastAPI 、数据处理、配置管理等场景的标配工具。 编程

1.核心定位
简单来说，Pydantic 的核心价值是：让输入数据 “符合预期” —— 它会严格验证数据的类型、格式、约束规则，自动将非标准数据转换为目标类型，同时清晰提示错误，解决了 Python 动态类型带来的 “数据不可控” 问题。
'''

'''
2.核心能力（核心场景）
'''

'''
（1）数据验证与类型转换
这是 Pydantic 最基础也最核心的能力：
基于 Python 类型注解定义数据模型，自动验证输入数据是否符合类型 / 规则
智能类型转换（如字符串转整数、ISO 字符串转 datetime、“true” 转布尔值）
验证失败时返回结构化的错误信息，便于定位问题
'''
# # 定义数据模型（规则）
# from pydantic import BaseModel, Field, ValidationError
# class User(BaseModel):
#     id: int = Field(ge=1, description="用户ID必须≥1")  # 数值约束
#     name: str = Field(min_length=2, max_length=20)     # 字符串长度约束
#     age: int | None = None                             # 可选字段
#     email: str | None = None

# # 合法数据：自动转换+验证
# user1 = User(id="1001", name="张三", age="25")  # 字符串自动转int
# print(user1.id, type(user1.id))  # 输出：1001 <class 'int'>

# #非法数据：抛出结构化错误
# try:
#     User(id=0, name="A", age="abc")
# except ValidationError as e:
#     print(e.json(indent=2))  # 输出清晰的错误详情

'''
（2）复杂数据类型支持
除了基础类型（int/str/float/bool），Pydantic 原生支持：

容器类型：list[int]、dict[str, str]、tuple[int, str]
特殊类型：datetime、UUID、EmailStr、UrlStr（需安装可选依赖 pydantic[email,url]）
枚举类型：结合 Python Enum 限制字段值范围
嵌套模型：模型内嵌套其他 Pydantic 模型，支持多层验证
'''
# from pydantic import BaseModel, EmailStr
# from datetime import datetime
# from typing import List
# from enum import Enum
# # 枚举类型
# class UserRole(str, Enum):
#     ADMIN = "admin"
#     USER = "user"

# # 嵌套模型
# class Address(BaseModel):
#     province: str
#     city: str

# class ComplexUser(BaseModel):
#     id: int
#     name: str
#     role: UserRole          # 枚举约束
#     email: EmailStr         # 邮箱格式验证
#     create_time: datetime   # 自动解析ISO时间字符串
#     addresses: List[Address]  # 嵌套模型列表

# # 验证复杂数据
# user = ComplexUser(
#     id=1002,
#     name="李四",
#     role="admin",  # 自动匹配枚举
#     email="lisi@example.com",
#     create_time="2026-03-23T12:00:00",
#     addresses=[{"province": "北京", "city": "北京"}, {"province": "上海", "city": "上海"}]
# )
# print(user.create_time)  # 输出：2026-03-23 12:00:00
# print(user.addresses[0].city)  # 输出：北京

'''
（3）自定义验证逻辑
通过 field_validator（V2 新增，替代 V1 的 validator）可以实现个性化验证规则，满足业务定制需求： 
'''
# from pydantic import BaseModel, field_validator
# class PasswordModel(BaseModel):
#     password: str

#     # 自定义验证器：密码必须包含字母+数字
#     @field_validator("password")
#     def validate_password(cls, v):
#         if len(v) < 8:
#             raise ValueError("密码长度不能少于8位")
#         if not (any(c.isdigit() for c in v) and any(c.isalpha() for c in v)):
#             raise ValueError("密码必须同时包含字母和数字")
#         return v

# # 合法示例
# pwd_model = PasswordModel(password="Pass123456")
# # 非法示例会抛出清晰的错误

'''
（4）配置管理（结合 pydantic-settings）
pydantic-settings（v2.13.1）是 Pydantic 官方的配置管理扩展，替代 V1 的 BaseSettings，支持从环境变量、.env 文件、配置文件加载配置，是项目配置管理的最佳实践：
'''
# from pydantic_settings import BaseSettings, SettingsConfigDict
# class AppSettings(BaseSettings):
#     # 配置字段（自动从环境变量/.env加载）
#     app_name: str = "MyApp"  # 默认值
#     app_port: int = 8000
#     database_url: str

#     # 配置加载规则
#     model_config = SettingsConfigDict(
#         env_file=".env",        # 指定.env文件路径
#         env_file_encoding="utf-8",
#         env_prefix="MYAPP_",    # 环境变量前缀（避免冲突）
#     )

# # 加载配置（自动读取 .env 文件中 MYAPP_DATABASE_URL 等字段）
# settings = AppSettings()
# print(settings.database_url)  # 输出从.env加载的数据库地址

'''
3.核心优势
性能极致：V2 基于 Rust 重写核心，验证速度比 V1 提升 5-50 倍，适合高频数据验证场景；
易用性高：完全基于 Python 类型注解，学习成本低，编辑器（如 VS Code）可提供完整提示；
生态完善：是 FastAPI 的默认数据验证库，与 Django、SQLAlchemy 等主流框架兼容；
错误友好：验证失败时返回结构化错误信息，包含错误位置、原因、输入值，便于调试；
扩展性强：支持自定义验证器、自定义类型、模型嵌套，满足复杂业务场景。

4.典型使用场景
API 开发：FastAPI/Starlette 中验证请求体、查询参数、路径参数；
数据清洗：处理外部数据（如 CSV/JSON/ 数据库返回值），确保数据符合业务规则；
配置管理：加载项目配置（环境变量、.env 文件、多环境配置）；
数据序列化 / 反序列化：模型与字典 / JSON 快速互转，替代手动解析；
CLI 工具：验证命令行参数，确保输入合法。

5.官方链接
5.1.官方主站与文档（英文，权威最新）
    Pydantic 官网：https://docs.pydantic.dev/
    最新稳定版文档（v2.12.x）：https://docs.pydantic.dev/latest/
    pydantic-settings 官方文档：https://docs.pydantic.dev/latest/concepts/pydantic_settings/Pydantic
    pydantic-settings API 参考：https://docs.pydantic.dev/latest/api/pydantic_settings/Pydantic
    GitHub 仓库（源码）：https://github.com/pydantic/pydantic
    PyPI 发布页：https://pypi.org/project/pydantic/
5.2.中文文档（国内镜像，便于阅读）
    Pydantic 中文文档：https://docs.pydantic.org.cn/latest/
    pydantic-settings 中文文档：https://docs.pydantic.org.cn/latest/concepts/pydantic_settings/
'''

'''
6.相关单词
单词	        音标	                中文释义	                    核心使用场景
Pydantic	    /paɪˈdæntɪk/	        派丹提克（Python 数据验证库名）	 Python 中数据校验、模型定义、序列化 / 反序列化
Validation	    /ˌvælɪˈdeɪʃn/	        验证、校验	                    Pydantic 的核心功能，如字段类型 / 规则校验
Model	        /ˈmɑːdl/	            模型	                        继承 BaseModel 定义数据模型，是 Pydantic 的基础
Field	        /fiːld/	                字段	                        定义模型中的数据字段，搭配 Field () 设置约束
Schema	        /ˈskiːmə/	            模式、架构	                    描述数据结构，Pydantic 可生成 JSON Schema
Serialization	/ˌsɪəriəlaɪˈzeɪʃn/	    序列化	                        将模型对象转为字典 / JSON（model_dump/model_dump_json）
Deserialization	/ˌdiːsɪəriəlaɪˈzeɪʃn/	反序列化	                    将字典 / JSON 转为模型对象（model_validate）
Validator	    /ˈvælɪdeɪtə®/	        校验器	                        自定义字段校验逻辑（field_validator/root_validator）
Settings	    /ˈsetɪŋz/	            配置	                        pydantic-settings 用于读取环境变量和配置文件
PydanticCore	/paɪˈdæntɪk kɔː®/	    Pydantic                        核心库	Pydantic v2 的底层核心，提供高性能校验
Annotated	    /ˈænəteɪtɪd/	        注解的	                        结合 Annotated 定义带校验的自定义类型
DefaultFactory	/dɪˈfɔːlt ˈfæktri/	    默认工厂	                    动态生成默认值（default_factory 参数）
StrictMode	    /strɪkt məʊd/	        严格模式	                    关闭隐式类型转换，强制严格的类型校验
Positive	    /ˈpɑːzətɪv/	            正的、积极的	                用于 Pydantic 的类型限定，如 PositiveInt（正整数）
'''

'''
二、入门篇：安装与数据验证
'''

'''
1.安装 Pydantic
首先确保安装正确版本：
# 基础安装（包含pydantic核心）
pip install pydantic==2.12.5

# 如需处理配置文件/环境变量，安装pydantic-settings
pip install pydantic-settings==2.13.1

# 一键安装所有依赖
pip install "pydantic==2.12.5" "pydantic-settings==2.13.1"

# Pydantic V2 已经不再使用 [url] / [uuid] 这种额外安装方式了！
# 只有 EmailStr 需要安装依赖
pip install pydantic[email]
# 或者
pip install email-validator==2.3.0
'''

'''
2.定义基础模型
'''

'''
2.1.用法示例
最基础的用法：定义模型 → 实例化 → 自动验证 
'''
# # 导入核心基类
# from pydantic import BaseModel
# # 1. 定义数据模型（类似数据结构模板）
# class User(BaseModel):
#     # 字段名: 类型注解（指定该字段必须是字符串）
#     name: str
#     # 字段名: 类型注解 + 默认值（可选字段）
#     age: int = 18
#     # 可选字段（| 表示可以是int或None）
#     height: int | None = None
# # 2. 正确实例化（符合类型要求）
# user1 = User(name="张三", age=25, height=180)
# print("✅ 正确实例化结果：")
# print(f"用户姓名：{user1.name}")
# print(f"用户年龄：{user1.age}")
# print(f"用户身高：{user1.height}")
# # 模型对象转字典（常用操作）
# print(f"模型转字典：{user1.model_dump()}")
# print(f"模型转json：{user1.model_dump_json()}")
# # 3. 错误实例化（类型不匹配）
# try:
#     print("\n开始错误实例化...")
#     user2 = User(name="李四", age="25", height="180cm")  # age 自动转换为int, height 传入字符串，而非int
#     print(f"用户姓名：{user2.name}")
# except Exception as e:
#     print("\n❌ 错误实例化结果：")
#     print(type(e)) # <class 'pydantic_core._pydantic_core.ValidationError'>
#     print(f"错误类型：{type(e).__name__}")
#     print(f"错误信息：{e}")

'''
2.2.核心知识点
模型必须继承 BaseModel
字段通过类型注解定义，Pydantic 会自动校验类型
带默认值的字段是可选字段，无默认值的是必填字段
model_dump() 是 Pydantic v2 中替代 v1 dict() 的方法，用于将模型转为字典
'''

'''
3.字段类型与验证
3.1.用法示例
Pydantic 支持所有 Python 原生类型，以下是最常用的示例： 脚本语言
'''
# from pydantic import BaseModel
# from typing import List, Dict, Tuple, Set
# # 定义包含多种基础类型的模型
# class DataModel(BaseModel):
#     # 字符串
#     username: str
#     # 整数
#     id: int
#     # 浮点数
#     score: float
#     # 布尔值
#     is_active: bool
#     # 列表（指定元素类型）
#     hobbies: List[str]
#     # 字典（指定键值类型）
#     info: Dict[str, int]
#     # 元组（固定长度+类型）
#     coords: Tuple[int, float]
#     # 集合
#     tags: Set[str]
#     # 可选字段（None表示允许为空）
#     remark: str | None = None

# # 正确实例化
# data = DataModel(
#     username="zhangsan",
#     id=1001,
#     score=98.5,
#     is_active=True,
#     hobbies=["篮球", "编程", "阅读"],
#     info={"level": 5, "experience": 1000},
#     coords=(100, 30.5),
#     tags={"python", "pydantic", "learning"}
# )

# print("✅ 多类型模型实例：")
# print(f"用户名：{data.username}")
# print(f"爱好列表：{data.hobbies}")
# print(f"坐标元组：{data.coords}")
# print(f"标签集合：{data.tags}")

# # 错误示例：列表元素类型不匹配
# try:
#     DataModel(
#         username="lisi",
#         id=1002,
#         score=89.0,
#         is_active=False,
#         hobbies=["游泳", 123],  # 列表混入整数，要求是字符串
#         info={"level": 3, "experience": 500},
#         coords=(200, 40.2),
#         tags={"java", "spring"}
#     )
# except Exception as e:
#     print("\n❌ 列表类型错误：")
#     print(e)

'''
3.2.类型验证规则
（1）基础类型验证规则（最常用）
类型	        验证规则	                    合法输入	非法输入
int	            必须能解析为整数自动转换合法值	123/“123”/123.0/True/False	“123.45”/123.99/“abc”/None
float	        必须能解析为浮点数	12.34/“12.34”/123/“123”	“abc”/None
str	            必须是字符串（或可转字符串）	“hello”/123/12.34/True	无（几乎都能转）
bool	        仅接受明确布尔值	True/False1/0"true"/“false”/“1”/“0”	“yes”/“no”/2/“abc”
None	        仅当声明为可选类型时允许	None	未声明可选时传 None
（2）可选类型验证规则
类型写法	    含义	        允许的值	    不允许的值
str | None	    字符串 或 None	“abc”/None	    123/True
int | None	    整数 或 None	123/None	    “abc”/12.34
float | None	浮点数 或 None	12.34/None	    “abc”
bool | None	    布尔 或 None	True/False/None	“yes”
（3）容器类型验证规则（列表 / 字典 / 元组）
类型	        验证规则
list[T]	        必须是列表 / 可迭代对象每个元素必须符合 T 类型
dict[K, V]	    必须是字典所有键必须符合 K****所有值必须符合 V
tuple[T1, T2]	固定长度、固定类型顺序长度必须一致每个位置类型必须匹配
tuple[T, …]	    任意长度，但所有元素必须是 T 类型
（4）特殊类型验证规则（高频实用）
类型	        验证规则	                合法示例	                            非法示例
datetime	    必须是标准 ISO 8601 格式	“2026-03-24T10:00:00”	                "2026-03-24 10:00"“2026/03/24”
date	        日期格式	                “2026-03-24”	                        “2026-03-24 10:00”
EmailStr	    必须符合邮箱格式	        test@example.com	                    test.example.comtest@.com
HttpUrl	        必须是有效 http/https URL	https://a.com	                        www.a.coma.com
UUID	        必须是 UUID 格式	        550e8400-e29b-41d4-a716-446655440000	普通字符串
（5）字段约束验证规则（搭配 Field 使用）
约束参数	    作用	        适用类型
gt	            大于	        int/float
ge	            大于等于	    int/float
lt	            小于	        int/float
le	            小于等于	    int/float
min_length	    最小长度	    str / list / tuple
max_length	    最大长度	    str / list / tuple
pattern	        正则匹配	    str
（6）总结
数字：能转就转，不能转报错
字符串：几乎万能接收
布尔：只认 true/false/1/0
可选：加 | None 才允许空值
容器：里面每个元素都要验证
时间：只认 ISO 格式
邮箱 / URL：必须符合标准格式
'''

'''
4.字段约束
仅验证类型不够，Pydantic 提供 Field 工具为字段添加精细的约束规则（如长度、范围、格式等）。 
'''
# from pydantic import BaseModel, Field, ValidationError
# class Product(BaseModel):
#     # Field 核心参数：
#     # ge=大于等于, le=小于等于, gt=大于, lt=小于
#     # min_length=最小长度, max_length=最大长度
#     # default=默认值, description=字段描述
#     id: int = Field(ge=1, description="商品ID必须≥1")
#     name: str = Field(min_length=2, max_length=50, description="商品名称2-50字符")
#     price: float = Field(gt=0, description="价格必须>0")
#     stock: int = Field(default=0, ge=0, description="库存默认0，≥0")

# # 合法示例
# product1 = Product(id=1001, name="手机", price=1999.99)
# print(product1)

# # 非法示例（价格≤0）
# try:
#     Product(id=1002, name="耳机", price=-99, stock=10)
# except ValidationError as e:
#     # 打印结构化错误信息
#     print(e.json(indent=2))

'''
4.2.常用约束参数
参数	    作用	                    适用类型
ge	        大于等于	                int/float
le	        小于等于	                int/float
gt	        大于	                    int/float
lt	        小于	                    int/float
min_length	最小长度	                 str
max_length	最大长度	                str
pattern	    正则表达式匹配	             str
default	    默认值	                    所有类型
alias	    字段别名（适配外部数据）	 所有类型
description	字段描述	                所有类型
'''

'''
4.3.正则约束示例
'''
# from pydantic import BaseModel, Field
# class User(BaseModel):
#     # 手机号正则：11位数字，以1开头
#     phone: str = Field(pattern=r"^1[3-9]\d{9}$")
#     # 密码正则：至少8位，包含字母和数字
#     password: str = Field(pattern=r"^[A-Za-z\d]{8,}$")
# # 合法示例
# user = User(phone="13800138000", password="Pass1234")
# print(user)
# # 非法示例（手机号位数不对）→ 抛出 ValidationError
# User(phone="123456", password="Pass1234")

'''
5.处理外部数据
外部数据（如 JSON 文件、API 响应、CSV 数据）通常是「原始字典 / 字符串」，Pydantic 能快速验证并转换为结构化数据。 编程
'''

'''
5.1.处理 JSON 文件数据
假设 users.json 内容：
'''
# import json
# from pydantic import BaseModel, EmailStr, ValidationError, Field
# # 1. 定义模型（匹配外部数据结构）
# class User(BaseModel):
#     id: int
#     name: str
#     age: int = Field(ge=0)
#     email: EmailStr  # 邮箱格式验证
# # 2. 读取JSON文件（原始外部数据）
# with open("users.json", "r", encoding="utf-8") as f:
#     raw_data = json.load(f)  # 原始数据：列表+字典
# # 3. 验证并解析数据
# try:
#     # 批量验证：将原始数据转为模型列表
#     validated_users = [User(**item) for item in raw_data]

#     # 4. 使用验证后的数据（类型安全）
#     for user in validated_users:
#         print(f"ID：{user.id}（类型：{type(user.id)}），邮箱：{user.email}")
# except ValidationError as e:
#     print("\n数据验证失败：")
#     # 解析错误详情
#     for error in e.errors():
#         print(f"位置：{error['loc']} → 原因：{error['msg']} → 输入值：{error['input']}")

'''
5.2.处理 API 响应数据
'''
# from typing import List
# import requests
# from pydantic import BaseModel, HttpUrl, ValidationError, Field
# # 1. 定义API响应模型
# class Product(BaseModel):
#     id: int
#     title: str
#     price: float = Field(gt=0)
#     images: List[HttpUrl]  # URL列表格式验证
#     thumbnail: HttpUrl  # URL格式验证
# class ApiResponse(BaseModel):
#     products: List[Product]
#     total: int
# # 2. 调用第三方API（获取外部数据）
# url = "https://dummyjson.com/products"
# raw_response = requests.get(url).json()
# # 3. 验证API响应
# try:
#     # 将 API 返回的原始字典数据（raw_response）解包并传递给 ApiResponse 模型
#     validated_data = ApiResponse(**raw_response)
#     # 使用数据
#     print(f"总商品数：{validated_data.total}")
#     print(f"第一个商品：{validated_data.products[0].title} → 价格：{validated_data.products[0].price}")
# except ValidationError as e:
#     print(f"API数据验证失败：{e}")

'''
5.3.处理不规范外部数据的技巧
外部数据常存在「字段名不一致」「冗余字段」等问题，Pydantic 提供灵活的适配方案：
'''
'''
技巧 1：忽略冗余字段
'''
# from pydantic import BaseModel
# class User(BaseModel):
#     id: int
#     name: str

#     # 配置：忽略模型中未定义的字段，Pydantic V2 默认值：你写不写 extra: "ignore"，效果现在是一样的。
#     model_config = {"extra": "ignore"}
#     # 🔥 改成 forbid 马上报错！
#     # model_config = {"extra": "forbid"}
#     # 多出来的字段 → 保留进模型，很少用
#     # model_config = {"extra": "allow"}

# # 原始数据包含冗余字段 gender → 自动忽略
# raw_data = {"id": 1, "name": "张三", "gender": "男"}
# user = User(**raw_data)
# print(user)  # id=1 name='张三'

'''
技巧 2：字段别名（适配不一致的字段名)
'''
# from pydantic import BaseModel, Field
# class User(BaseModel):
#     # 外部字段是 user_id，模型中是 id → 用 alias 映射
#     id: int = Field(alias="user_id")
#     full_name: str = Field(alias="name")
# # 原始数据字段名是 user_id/name
# raw_data = {"user_id": 1, "name": "张三"}
# # 抛出异常: ValidationError
# # raw_data = {"id": 1, "full_name": "张三"}
# user = User(**raw_data)
# print(user.id)  # 1
# print(user.full_name)  # 张三

'''
6.模型继承与字段复用
实际项目中会存在多个模型共用通用字段的场景（如创建时间、更新时间、主键 ID），Pydantic 支持模型的单继承 / 多继承，实现字段复用，减少重复代码。

核心特性： 操作系统

子模型会继承父模型的所有字段，可直接使用；
子模型可重写父模型字段（覆盖约束、默认值）；
支持动态默认值（default_factory），适合时间、随机值等动态生成的通用字段。
'''

'''
6.1.基础继承示例（通用字段复用）
'''
# from datetime import datetime
# from uuid import uuid4, UUID
# from pydantic import BaseModel, Field
# # 通用基础模型（所有业务模型都继承）
# class BaseModelMixin(BaseModel):
#     id: UUID = Field(default_factory=uuid4, description="唯一主键，自动生成UUID")
#     create_time: datetime = Field(default_factory=datetime.now, description="创建时间，自动生成")
#     update_time: datetime = Field(default_factory=datetime.now, description="更新时间，自动生成")
# # 业务模型：用户模型（继承基础模型）
# class User(BaseModelMixin):
#     name: str = Field(min_length=2, max_length=20, description="用户名")
#     age: int | None = Field(default=None, ge=0, description="年龄")
# # 业务模型：商品模型（继承基础模型）
# class Product(BaseModelMixin):
#     title: str = Field(min_length=2, max_length=50, description="商品名称")
#     price: float = Field(gt=0, description="商品价格")
# # 实例化子模型（自动包含父模型的所有字段）
# user = User(name="张三", age=25)
# product = Product(title="手机", price=1999.99)
# print("✅ 用户模型（含继承字段）：")
# print(f"ID：{user.id}，创建时间：{user.create_time}，用户名：{user.name}")
# print("✅ 商品模型（含继承字段）：")
# print(f"ID：{product.id}，创建时间：{product.create_time}，商品名：{product.title}")

'''
6.2.字段重写示例（覆盖父模型约束 / 默认值）
子模型可对父模型的字段进行重写，修改默认值、约束规则等，优先级高于父模型：
'''
# from datetime import datetime
# from pydantic import BaseModel, Field
# class BaseModelMixin(BaseModel):
#     id: int = Field(ge=1, description="主键ID，≥1")
#     create_time: datetime = Field(default_factory=datetime.now)
# # 重写父模型字段：修改id的默认值，增加update_time的显式传参要求
# class User(BaseModelMixin):
#     id: int = Field(default=1000, ge=1000, description="用户ID，从1000开始")  # 重写id约束+默认值
#     name: str
#     update_time: datetime  # 重写为必填字段，取消默认值
# # 实例化：id使用重写后的默认值1000，必须显式传update_time
# user = User(name="李四", update_time=datetime.now())
# print(f"✅ 重写字段后：ID={user.id}，更新时间={user.update_time}")

'''
6.3.模型多继承（Multiple Inheritance）
Pydantic v2 完全支持多继承，允许一个模型同时继承多个父类，合并所有父类的字段、验证器、配置，实现更灵活的字段复用。 

适合场景：

一个模型需要多组通用字段（如：日志字段 + 软删除字段 + 租户字段）
不同功能模块的字段组合
大型项目中切面式复用（不侵入业务逻辑）
核心规则（必须记住）

字段合并：所有父类的字段都会被子类继承，按从左到右顺序合并
字段覆盖：右边父类 > 左边父类 > 子类
验证器合并：所有父类的验证器都会保留并执行
配置合并：model_config 会被子类覆盖父类
不能有冲突的 Field 定义（类型不一致会报错）
完整示例代码（最常用实战写法）：
'''
# from datetime import datetime
# from uuid import uuid4, UUID
# from pydantic import BaseModel, Field
# # -------------------------- 父类1：基础ID与时间 --------------------------
# class BaseIDModel(BaseModel):
#     id: UUID = Field(default_factory=uuid4)
#     create_time: datetime = Field(default_factory=datetime.now)
# # -------------------------- 父类2：更新记录 --------------------------
# class UpdateModel(BaseModel):
#     update_time: datetime = Field(default_factory=datetime.now)
#     update_user: str | None = None
# # -------------------------- 父类3：软删除 --------------------------
# class SoftDeleteModel(BaseModel):
#     is_deleted: bool = False
#     delete_time: datetime | None = None
# # -------------------------- 子类：同时继承 3 个父类（多继承） --------------------------
# class User(BaseIDModel, UpdateModel, SoftDeleteModel):
#     name: str
#     age: int
# # 实例化
# user = User(name="张三", age=25)
# print(user.model_dump_json(indent=2))


'''
带验证器的多继承（验证器会合并）：
'''
# from pydantic import BaseModel, field_validator
# class NameValidator(BaseModel):
#     name: str
#     @field_validator("name")
#     def name_must_2_chars(cls, v):
#         assert len(v) >= 2
#         return v
# class AgeValidator(BaseModel):
#     age: int
#     @field_validator("age")
#     def age_must_positive(cls, v):
#         assert v >= 0
#         return v
# # 同时继承两个验证器
# class User(NameValidator, AgeValidator):
#     pass
# # 两个验证器都会执行！
# user = User(name="张三", age=20)  # 正常
# # user = User(name="张", age=20)  # 报错

'''
6.4.核心知识点
父模型需继承 BaseModel，子模型继承父模型即可实现字段复用；
default_factory：动态默认值函数，区别于固定默认值（如default=18），适合生成随时间 / 场景变化的值（时间、UUID、随机数）；
字段重写规则：子模型字段名与父模型一致时，子模型字段完全覆盖父模型（约束、默认值、描述均被替换）；
多继承：支持同时继承多个基础模型（class A(B, C): ...），字段按继承顺序合并（后继承的模型字段覆盖先继承的）。
'''

'''
7.严格模式校验（Strict Mode）
Pydantic 默认开启自动类型转换（如字符串"123"转整数123、浮点数123.0转整数123），适合大部分灵活的业务场景。

严格模式：关闭自动类型转换，强制输入数据与字段类型完全匹配，不允许任何隐式转换，适合金融、敏感数据、高精度验证等场景。
'''

'''
7.1.基础使用示例
通过 model_config 中的 strict=True 开启全局严格模式，也可对单个字段单独开启严格模式。
'''
# from pydantic import BaseModel, Field, ValidationError
# # 全局严格模式：所有字段都强制类型匹配
# class StrictUser(BaseModel):
#     id: int
#     age: float
#     name: str
#     is_active: bool
#     model_config = {"strict": True}  # 全局开启严格模式
# # 单个字段严格模式：仅id字段开启，其他字段保持默认自动转换
# class PartialStrictUser(BaseModel):
#     id: int = Field(strict=True)  # 单个字段开启严格模式
#     age: float
#     name: str
#     is_active: bool
# # 测试1：全局严格模式 - 合法输入（类型完全匹配）
# user1 = StrictUser(id=1001, age=25.0, name="张三", is_active=True)
# print("✅ 全局严格模式合法输入：", user1.model_dump())
# # 测试2：全局严格模式 - 非法输入（字符串"1002"无法转int）
# try:
#     StrictUser(id="1002", age=26, name="李四", is_active="true")
# except ValidationError as e:
#     print("\n❌ 全局严格模式类型不匹配：")
#     print(e.json(indent=2))
# # 测试3：单个字段严格模式 - id传字符串报错，age传整数自动转浮点数
# try:
#     PartialStrictUser(id="1003", age=27, name="王五", is_active="true")
# except ValidationError as e:
#     print("\n❌ 单个字段严格模式id错误：")
#     print(e.json(indent=2))

'''
7.2.严格模式核心规则
字段类型	 非严格模式（默认）	              严格模式
int	        支持"123"/123.0/True转 int	    仅支持纯整数123
float	    支持"123.45"/123转 float	    仅支持纯浮点数123.45
bool	    支持"true"/"1"/0转 bool	        仅支持True/False
str	        支持任意类型转字符串	         仅支持纯字符串
'''

'''
7.3.适用场景
✅ 推荐使用：金融系统（金额、交易数验证）、敏感数据接口（用户信息、身份验证）、高精度数据处理；
❌ 不推荐使用：普通 API 接口、外部松散数据处理（如爬虫、第三方 API 响应），会增加数据适配成本。
'''

'''
三、进阶篇：高级验证与配置
'''

'''
1.字段验证器（自定义验证规则）
1.1.用法示例
当内置类型验证不够用时，可通过 field_validator 自定义验证逻辑： 
'''
# from pydantic import BaseModel, field_validator, ValidationError
# class User(BaseModel):
#     name: str
#     age: int
#     email: str

#     # 自定义验证器：验证年龄范围
#     @field_validator('age')
#     def age_must_be_positive(cls, v):  # cls是模型类，v是字段值
#         if v < 0 or v > 120:
#             raise ValueError('年龄必须在0-120之间')
#         return v

#     # 自定义验证器：简单验证邮箱格式（实际用EmailStr更优）
#     @field_validator('email')
#     def email_must_contain_at(cls, v):
#         if '@' not in v:
#             raise ValueError('邮箱必须包含@符号')
#         return v

# # 正确实例化
# user1 = User(name="张三", age=25, email="zhangsan@example.com")
# print("✅ 验证通过：", user1.model_dump())

# # 错误实例1：年龄超出范围
# try:
#     User(name="李四", age=150, email="lisi@example.com")
# except ValidationError as e:
#     print("\n❌ 年龄验证失败：")
#     print(e)

# # 错误实例2：邮箱格式错误
# try:
#     User(name="王五", age=30, email="wangwu.example.com")
# except ValidationError as e:
#     print("\n❌ 邮箱验证失败：")
#     print(e)

'''
1.2.核心知识点
@field_validator 是 Pydantic v2 替代 v1 @validator 的装饰器
验证器函数第一个参数是 cls（模型类），第二个是字段值 v
验证失败时抛出 ValueError，Pydantic 会自动封装为 ValidationError
'''

'''
2.内置特殊类型（更精准的验证）
2.1.用法示例
安装依赖：
pip install pydantic-extra-types phonenumbers
'''
# from pydantic import BaseModel, EmailStr, HttpUrl, PositiveInt, NegativeFloat, ValidationError
# from pydantic_extra_types.phone_numbers import PhoneNumber
# # 定义包含特殊类型的模型
# class Contact(BaseModel):
#     # 邮箱（自动验证格式）
#     email: EmailStr
#     # URL（自动验证格式）
#     website: HttpUrl
#     # 正整数（必须>0）
#     age: PositiveInt
#     # 负浮点数（必须<0）
#     debt: NegativeFloat
#     # 电话号码（需安装 phonenumbers 库：pip install phonenumbers）
#     phone: PhoneNumber | None = None
# # 正确实例化
# contact = Contact(
#     email="user@example.com",
#     website="https://www.example.com",
#     age=28,
#     debt=-100.5,
#     phone="+8613800138000"  # 中国手机号需加国家码
# )
# print("✅ 特殊类型验证通过：")
# print(f"邮箱：{contact.email}")
# print(f"网址：{contact.website}")
# print(f"电话号码：{contact.phone}")
# # 错误实例：邮箱格式错误
# try:
#     Contact(
#         email="user.example.com",  # 缺少@
#         website="https://www.example.com",
#         age=28,
#         debt=-100.5
#     )
# except ValidationError as e:
#     print("\n❌ 邮箱格式错误：")
#     print(e)

'''
2.2.常用特殊类型清单
类型	            作用
EmailStr	        验证邮箱格式
HttpUrl	            验证 URL 格式（必须带 http/https）
PositiveInt	        正整数（>0）
NegativeInt	        负整数（<0）
PhoneNumber	        验证电话号码（需安装 phonenumbers）
IPvAnyAddress	    验证 IP 地址（v4/v6）
Json	            验证 JSON 字符串
'''

'''
3.自定义数据类型（Custom Types）
当 Pydantic 的内置类型 + 字段验证器无法满足复用性要求时（如多个模型需要验证「偶数」「手机号（无国家码）」「身份证号」），可通过自定义数据类型实现一次定义、全局复用的校验逻辑，比单独的field_validator更优雅，复用性更高。 

Pydantic v2 自定义类型核心基于 pydantic_core 的核心 schema 实现，支持基础类型扩展和全新类型定义。
'''

'''
3.1.基础自定义类型示例（偶数验证）
定义仅允许偶数的整数类型，所有使用该类型的字段都会自动执行偶数验证，无需重复写验证器。
'''
# from pydantic import BaseModel, GetCoreSchemaHandler
# from pydantic import ValidationError
# from pydantic_core import CoreSchema, core_schema
# # 自定义类型：仅允许偶数的整数
# class EvenInt(int):
#     """自定义整数类型，仅接受偶数"""

#     @classmethod
#     def __get_pydantic_core_schema__(
#             cls, source_type: type, handler: GetCoreSchemaHandler
#     ) -> CoreSchema:
#         # 步骤1：获取基础int类型的核心schema（继承int的基础验证）
#         int_schema = handler(int)
#         # 步骤2：定义自定义验证逻辑
#         def validate_even(v: int) -> int:
#             if v % 2 != 0:
#                 raise ValueError(f"输入值{v}不是偶数，仅支持偶数")
#             return cls(v)  # 转换为自定义EvenInt类型

#         # 步骤3：组合schema：基础int验证 + 自定义偶数验证
#         validate_schema = core_schema.no_info_plain_validator_function(validate_even)
#         return core_schema.chain_schema([int_schema, validate_schema])
# # 使用自定义类型
# class DataModel(BaseModel):
#     even_num: EvenInt  # 直接使用自定义类型，自动验证偶数
#     count: int  # 普通int类型，无额外验证
# # 测试1：合法输入（偶数）
# data1 = DataModel(even_num=4, count=3)
# print("✅ 合法自定义类型：", data1.model_dump())
# print(f"even_num类型：{type(data1.even_num)}")  # 类型为自定义EvenInt
# # 测试2：非法输入（奇数）
# try:
#     DataModel(even_num=5, count=2)
# except ValidationError as e:
#     print("\n❌ 自定义类型验证失败：")
#     print(e.json(indent=2))

'''
3.2.实战自定义类型示例（国内手机号验证）
定义专门验证国内 11 位手机号的自定义类型，全局复用，无需重复写正则验证器。 
'''
# import re
# from pydantic import BaseModel, GetCoreSchemaHandler
# from pydantic import ValidationError
# from pydantic_core import CoreSchema, core_schema
# # 自定义类型：国内11位手机号（以13/14/15/16/17/18/19开头）
# class ChinesePhone(str):
#     """自定义字符串类型，验证国内11位手机号"""
#     phone_pattern = re.compile(r"^1[3-9]\d{9}$")

#     @classmethod
#     def __get_pydantic_core_schema__(
#             cls, source_type: type, handler: GetCoreSchemaHandler
#     ) -> CoreSchema:
#         # 基础str类型schema
#         str_schema = handler(str)
#         # 自定义手机号验证逻辑
#         def validate_phone(v: str) -> str:
#             if not cls.phone_pattern.match(v):
#                 raise ValueError(f"输入{v}不是合法的国内11位手机号")
#             return cls(v)
#         # 组合schema
#         validate_schema = core_schema.no_info_plain_validator_function(validate_phone)
#         return core_schema.chain_schema([str_schema, validate_schema])
# # 多个模型复用自定义手机号类型
# class User(BaseModel):
#     name: str
#     phone: ChinesePhone  # 复用自定义类型
# class Order(BaseModel):
#     order_id: int
#     contact_phone: ChinesePhone  # 复用自定义类型
# # 测试合法输入
# user = User(name="张三", phone="13800138000")
# order = Order(order_id=10001, contact_phone="19900009999")
# print("✅ 合法手机号：", user.phone, order.contact_phone)
# # 测试非法输入（位数不足）
# try:
#     User(name="李四", phone="138001380")
# except ValidationError as e:
#     print("\n❌ 非法手机号验证失败：")
#     print(e.json(indent=2))

'''
3.3.核心知识点
自定义类型需继承基础 Python 类型（如int/str/float），实现基础类型的扩展；
核心方法__get_pydantic_core_schema__：Pydantic v2 自定义类型的入口，用于组合基础 schema和自定义验证 schema；
handler(source_type)：获取基础类型的核心 schema，继承基础类型的所有验证规则（如str的非空、int的数值验证）；
core_schema.chain_schema：按顺序执行多个 schema，先执行基础类型验证，再执行自定义验证；
复用性：自定义类型可在所有模型中直接使用，无需重复编写验证逻辑，适合项目中高频的统一校验规则。
'''

'''
4.模型配置（Model Config）
通过 model_config 自定义模型行为（Pydantic v2 替代 v1 的 Config 类）：
'''
# from pydantic import BaseModel, ValidationError, Field
# class User(BaseModel):
#     name: str = Field(..., alias="NAME")  # 别名
#     age: int = Field(..., alias="AGE")

#     # 模型配置（v2 新语法）
#     model_config = {
#         # 大小写不敏感
#         "populate_by_name": True,  # 允许同时使用原名/别名赋值
#         # 可选：去除字符串空格
#         "str_strip_whitespace": True,
#         # 允许额外的字段（默认会报错）
#         'extra': 'allow',
#         # 自动转换数据类型（如字符串转整数）
#         'coerce_numbers_to_str': False,
#         'str_to_bytes': False,
#         # 验证失败时的错误消息语言（暂只支持英文）
#         'locale': 'en_US',
#         # 输入时将字段名转换为小写
#         'alias_generator': lambda x: x.lower()
#     }
# # 1. 大小写不敏感
# try:
#     user1 = User(NAME="张三", AGE=25)
#     # user1 = User(**{"NAME": "小明", "AGE": 20})
#     print("\n✅ 大小写不敏感：", user1.model_dump())
# except ValidationError as e:
#     print("\n❌ 大小写不敏感：", e)
# # 2. 允许额外字段
# try:
#     user2 = User(name="李四", age=30, gender="男")  # gender是额外字段
#     print("\n✅ 允许额外字段：", user2.model_dump())
# except ValidationError as e:
#     print("\n❌ 允许额外字段：", e)
# # 3. 自动类型转换（字符串转整数）
# try:
#     user3 = User(name="王五", age="35")  # age传入字符串"35"，自动转int
#     print("\n✅ 自动类型转换：", user3.model_dump())
# except ValidationError as e:
#     print("\n❌ 自动类型转换：", e)

'''
5.嵌套模型（复杂数据结构）
Pydantic 支持模型嵌套，用于处理复杂的层级数据：
indent：JSON 格式化缩进参数
indent=2：每嵌套一级，就向右缩进 2 个空格
支持数字：1、2、3、4 都可以（常用 2 或 4）
'''
# from pydantic import BaseModel
# from typing import List
# # 子模型：地址
# class Address(BaseModel):
#     city: str
#     street: str
#     zipcode: str | None = None

# # 父模型：用户（包含地址模型）
# class User(BaseModel):
#     name: str
#     age: int
#     # 单个地址（嵌套模型）
#     primary_address: Address
#     # 多个地址（列表+嵌套模型）
#     other_addresses: List[Address] = []
# # 实例化嵌套模型
# user = User(
#     name="张三",
#     age=25,
#     primary_address=Address(city="北京", street="朝阳区XX路", zipcode="100000"),
#     other_addresses=[
#         Address(city="上海", street="浦东新区XX路", zipcode="200000"),
#         Address(city="广州", street="天河区XX路")
#     ]
# )
# print("✅ 嵌套模型实例：")
# print(f"主地址：{user.primary_address.city} - {user.primary_address.street}")
# print(f"其他地址数量：{len(user.other_addresses)}")
# print(f"第二个其他地址：{user.other_addresses[1].city}")
# # 嵌套模型转JSON（常用）
# print(f"\n嵌套模型转JSON：{user.model_dump_json(indent=2)}")


'''
四、高级篇：配置管理与实战技巧
'''

'''
1.Pydantic Settings（环境变量 / 配置文件）
pydantic-settings 是专门用于配置管理的扩展，支持从环境变量、.env 文件、配置文件中读取配置： 脚本语言
1.1.用法示例
第一步：创建 .env 文件（项目根目录）
'''
# from pydantic import Field
# from pydantic_settings import BaseSettings, SettingsConfigDict
# # 定义配置模型（继承BaseSettings而非BaseModel）
# class Settings(BaseSettings):
#     # 配置字段（支持默认值）
#     # .env 文件的优先级虽然高于默认值
#     app_name: str = Field(default="DefaultApp")
#     app_port: int = Field(default=80)
#     database_url: str = Field(default="")
#     debug: bool = False
#     secret_key: str = Field(default="DefaultKey")

#     # 配置读取规则
#     model_config = SettingsConfigDict(
#         # 从.env文件读取配置
#         # env_file=".env",  # 相对路径
#         env_file=r".env",  # 或者使用绝对路径
#         # .env文件编码
#         env_file_encoding="utf-8",
#         # 大小写不敏感
#         case_sensitive=False,
#         # 字段名与环境变量名映射（可选）
#         # env_prefix="APP_",  # 只读取以APP_开头的环境变量
#     )
# # 实例化配置（自动读取.env文件和环境变量）
# settings = Settings()
# print("✅ 配置读取结果：")
# print(f"应用名称：{settings.app_name}")
# print(f"应用端口：{settings.app_port}")
# print(f"数据库URL：{settings.database_url}")
# print(f"调试模式：{settings.debug}")
# print(f"密钥：{settings.secret_key}")
# # 覆盖环境变量（测试用）
# import os
# os.environ["APP_PORT"] = "9000"
# settings2 = Settings()
# print(f"\n✅ 覆盖环境变量后：{settings2.app_port}")

'''
1.2.核心知识点
配置模型需继承 BaseSettings（而非 BaseModel）
model_config 中 env_file 指定 .env 文件路径
环境变量优先级 > .env 文件 > 字段默认值
Field 可用于定义字段的额外属性（如默认值、描述等）
'''

'''
2.模型序列化与反序列化（模型/字典/JSON间转换）
Pydantic 提供丰富的方法处理模型与字典 / JSON / 字符串的转换： 软件实用程序
'''
# import json
# from pydantic import BaseModel
# class User(BaseModel):
#     name: str
#     age: int
#     is_active: bool = True
# # 1. 字典转模型（反序列化）
# user_dict = {"name": "张三", "age": 25}
# user = User(**user_dict)
# print("字典转模型：", user)
# # 2. 字典转JSON字符串
# # 直接用 json.dumps 或者 Pydantic 模型转都可以
# dict_to_json = json.dumps(user_dict, ensure_ascii=False, indent=2)
# print(f"字典转JSON字符串：\n{dict_to_json}")
# # 3. 模型转字典
# print(f"\n模型转字典：{user.model_dump()}")
# # 只包含非默认值的字段
# print(f"只包含非默认值：{user.model_dump(exclude_defaults=True)}")
# # 排除指定字段
# print(f"排除age字段：{user.model_dump(exclude={'age'})}")
# # 4. 模型转JSON字符串
# json_str = user.model_dump_json(indent=2)
# print(f"模型转JSON：\n{json_str}")
# # 5. JSON字符串转模型
# user2 = User.model_validate_json(json_str)
# print(f"\nJSON转模型：{user2.name} - {user2.age}")
# # 6. JSON字符串转字典
# # 用 json.loads 把 JSON 字符串转回字典
# json_to_dict = json.loads(json_str)
# print(f"JSON字符串转字典：{json_to_dict}")
# # 7. 模型更新（使用 model_validate 重新创建实例）
# # 方案 1：使用 model_validate() + model_dump() 组合（推荐）
# update_data = {"age": 26, "is_active": False}
# user = User.model_validate({**user.model_dump(), **update_data})
# print(f"\n方案 1：模型更新后：{user.model_dump()}")
# # 方案 2：直接属性赋值
# user.age = 27
# user.is_active = False
# print(f"方案 2：模型更新后：{user.model_dump()}")
# # 方案 3：使用 setattr() 批量更新
# update_data = {"age": 28, "is_active": False}
# for key, value in update_data.items():
#     setattr(user, key, value)
# print(f"方案 3：模型更新后：{user.model_dump()}")

'''
3.部分验证与模型增量更新
实际开发中增量更新场景（如 API 的 PUT 请求更新用户信息），通常只需传递需要修改的字段，无需传全量字段，Pydantic 的部分验证可实现仅对传入的字段做验证，未传入的字段跳过验证，完美适配更新场景。 编程

核心实现方式：

model_validate 结合 context 实现自定义部分验证；
model_construct 跳过验证直接构建模型（适合内部可信数据）；
结合 model_dump 实现模型字段增量更新。
'''

'''
3.1 基础部分验证示例（自定义实现）
'''
# from typing import Optional
# from pydantic import BaseModel, Field, field_validator, ValidationError
# # 定义用户模型（全量字段）
# class User(BaseModel):
#     id: int = Field(ge=1)
#     name: str = Field(min_length=2, max_length=20)
#     age: Optional[int] = Field(default=None, ge=0)
#     email: Optional[str] = None

#     # 全局验证器：仅当字段传入时才执行验证
#     @field_validator("name", "age", "email")
#     def validate_only_present(cls, v, info):
#         # 判断是否开启了部分验证模式
#         partial_models = (info.context or {}).get("partial", [])
#         if cls.__name__ in partial_models:
#             field_name = info.field_name
#             if field_name not in info.data:
#                 return v  # 未传入的字段，直接返回，不验证
#         return v
# # 模拟数据库中的原始用户数据
# original_user = User(id=1001, name="张三", age=25, email="zhangsan@example.com")
# print("✅ 原始用户数据：", original_user.model_dump())
# # 增量更新：仅修改name字段，传递部分数据
# update_data = {"name": "张三更新"}
# # 部分验证：传入context={"partial": ["User"]} 开启部分验证
# try:
#     # 步骤1：部分验证更新数据
#     validated_update = User.model_validate(
#         {**original_user.model_dump(), **update_data},  # 合并原始数据+更新数据
#         context={"partial": ["User"]}
#     )
#     print("✅ 增量更新后：", validated_update.model_dump())
# except ValidationError as e:
#     print("\n❌ 部分验证失败：", e.json(indent=2))
# # 非法增量更新：name长度不符合要求，验证报错
# invalid_update = {"name": "A"}
# try:
#     User.model_validate(
#         {**original_user.model_dump(), **invalid_update},
#         context={"partial": ["User"]}
#     )
# except ValidationError as e:
#     print("\n❌ 非法更新验证失败：")
#     print(e.json(indent=2))

'''
3.2.快速增量更新（model_construct，内部可信数据）
model_construct 是 Pydantic 提供的无验证构建模型的方法，跳过所有字段验证和类型转换，直接根据传入的参数构建模型，仅适合内部可信数据的增量更新（如数据库查询后的数据修改），性能远高于全量验证。 
'''
# from pydantic import BaseModel, Field
# class User(BaseModel):
#     id: int = Field(ge=1)
#     name: str = Field(min_length=2)
#     age: int | None = None
# # 原始模型
# original = User(id=1001, name="张三", age=25)
# # 内部可信的更新数据，直接构建模型（跳过验证）
# update_data = {**original.model_dump(), "name": "张三新名字"}
# updated = User.model_construct(**update_data)
# print("✅ model_construct 增量更新：", updated.model_dump())

'''
3.3.核心知识点
部分验证的核心：仅对传入的字段执行验证，未传入的字段跳过，避免更新时必须传全量字段；
info.context：验证器的上下文参数，用于传递全局标识（如是否开启部分验证），实现灵活的验证逻辑；
info.data：获取传入模型的原始数据，用于判断字段是否被传入；
model_construct 注意事项：无任何验证，传入非法数据会导致模型字段异常，仅用于内部可信数据处理；
实际 API 场景：结合 FastAPI 的 PUT 请求，接收部分更新数据，合并数据库原始数据后执行部分验证。
'''

'''
4.实战：API 数据验证（模拟 FastAPI 场景）
Pydantic 最常用的场景是 API 数据验证，以下是模拟示例： 编程
'''
# from typing import Optional
# from pydantic import BaseModel, field_validator, ValidationError
# # 请求体模型
# class CreateUserRequest(BaseModel):
#     username: str
#     email: str
#     password: str
#     age: Optional[int] = None   # 等同于 age: int | None = None
#     # 验证用户名长度
#     @field_validator('username')
#     def username_length(cls, v):
#         if len(v) < 3 or len(v) > 20:
#             raise ValueError('用户名长度必须在3-20之间')
#         return v
#     # 验证密码强度
#     @field_validator('password')
#     def password_strength(cls, v):
#         if len(v) < 8:
#             raise ValueError('密码长度至少8位')
#         if not any(char.isdigit() for char in v):
#             raise ValueError('密码必须包含至少一个数字')
#         return v
# # 模拟API处理函数
# def create_user(request_data: dict):
#     try:
#         # 验证请求数据
#         request = CreateUserRequest(**request_data)
#         # 模拟数据库操作
#         user_id = 1001
#         # 返回响应
#         return {
#             "success": True,
#             "message": "用户创建成功",
#             "data": {
#                 "user_id": user_id,
#                 "username": request.username,
#                 "email": request.email
#             }
#         }
#     except ValidationError as e:
#         # 返回验证错误
#         return {
#             "success": False,
#             "message": "数据验证失败",
#             "errors": e.errors()
#         }
# # 测试1：正确请求
# print("✅ 正确请求：")
# response1 = create_user({
#     "username": "zhangsan123",
#     "email": "zhangsan@example.com",
#     "password": "Password123",
#     "age": 25
# })
# print(response1)
# # 测试2：错误请求（密码强度不够）
# print("\n❌ 错误请求：")
# response2 = create_user({
#     "username": "zs",  # 长度不足
#     "email": "zhangsan@example.com",
#     "password": "1234567",  # 长度不足+无字母
#     "age": 25
# })
# print(response2)

'''
5.FastAPI 深度整合（请求体 + 响应模型）
Pydantic 是 FastAPI 的默认数据验证库，二者深度融合，FastAPI 可自动根据 Pydantic 模型：

验证请求体、查询参数、路径参数、请求头的合法性；

自动生成OpenAPI 文档（Swagger/ReDoc），包含字段约束、描述；

自动将ORM 对象、字典转换为 Pydantic 响应模型，限制返回字段；

自动处理验证错误，返回结构化的错误信息。

核心整合场景：请求体验证、响应模型限制、路径 / 查询参数验证、ORM 对象适配。 操作系统
'''

'''
5.1.前置准备
安装依赖：
pip install fastapi==0.135.2 uvicorn==0.42.0
'''
# from datetime import datetime
# from typing import Optional, List
# from fastapi import FastAPI, Path, Query, HTTPException
# from pydantic import BaseModel, Field, EmailStr
# # 初始化FastAPI应用
# app = FastAPI(title="Pydantic + FastAPI 整合示例", version="1.0")
# # ---------------------- 1. 定义Pydantic模型 ----------------------
# # 请求体模型：创建用户（含字段约束、描述）
# class UserCreateRequest(BaseModel):
#     name: str = Field(min_length=2, max_length=20, description="用户名，2-20字符")
#     age: Optional[int] = Field(default=None, ge=0, le=120, description="年龄，0-120")
#     email: EmailStr = Field(description="合法邮箱格式")
#     hobbies: Optional[List[str]] = Field(default=[], description="爱好列表")
# # 响应模型：返回用户信息（仅返回指定字段，隐藏敏感信息）
# class UserResponse(BaseModel):
#     id: int = Field(description="用户ID")
#     name: str = Field(description="用户名")
#     email: EmailStr = Field(description="邮箱")
#     create_time: datetime = Field(description="创建时间")

#     # 核心配置：支持将ORM对象、自定义对象转换为响应模型
#     model_config = {"from_attributes": True}
# # ---------------------- 2. 模拟数据库 ----------------------
# fake_db = [
#     {
#         "id": 1,
#         "name": "张三",
#         "email": "zhangsan@example.com",
#         "age": 25,
#         "hobbies": ["篮球", "编程"],
#         "create_time": datetime.now()
#     }
# ]
# # ---------------------- 3. API接口定义 ----------------------
# # 3.1 创建用户：请求体验证（Pydantic模型作为请求体）
# @app.post("/users/", response_model=UserResponse, summary="创建用户")
# async def create_user(user: UserCreateRequest):
#     # 模拟数据库插入
#     user_id = len(fake_db) + 1
#     user_data = {
#         "id": user_id,
#         **user.model_dump(),
#         "create_time": datetime.now()
#     }
#     fake_db.append(user_data)
#     return user_data  # FastAPI自动转换为UserResponse模型
# # 3.2 获取用户：路径参数+查询参数验证（结合Pydantic约束）
# @app.get("/users/{user_id}", response_model=UserResponse, summary="根据ID获取用户")
# async def get_user(
#         # 路径参数验证：ge=1，结合Field描述
#         user_id: int = Path(ge=1, description="用户ID，≥1"),
#         # 查询参数验证：可选，匹配用户名包含的字符串
#         name_like: Optional[str] = Query(default=None, min_length=1, description="用户名模糊匹配")
# ):
#     # 查找用户
#     for user in fake_db:
#         if user["id"] == user_id:
#             if name_like and name_like not in user["name"]:
#                 raise HTTPException(status_code=404, detail="用户名不匹配")
#             return user
#     raise HTTPException(status_code=404, detail="用户不存在")
# # ---------------------- 4. 运行服务 ----------------------
# # 命令行执行：uvicorn 文件名:app --port=8081 --reload
# # 访问文档：http://127.0.0.1:8000/docs（Swagger） / http://127.0.0.1:8000/redoc（ReDoc）

'''
5.4 核心知识点
response_model：FastAPI 的核心参数，指定接口的返回模型为 Pydantic 模型，自动实现数据转换 + 字段过滤；
model_config = {"from_attributes": True}：允许将ORM 对象、自定义对象、字典转换为 Pydantic 响应模型，解决 ORM 对象无法直接返回的问题；
Path/Query：FastAPI 中用于验证路径参数 / 查询参数的工具，可结合 Pydantic 的 Field 约束（如ge/min_length）；
自动错误处理：FastAPI 会自动捕获 Pydantic 的ValidationError，转换为 HTTP 422（Unprocessable Entity）错误，返回结构化的错误信息；
文档自动生成：基于 Pydantic 模型的字段注解和描述，自动生成符合 OpenAPI 规范的接口文档，无需手动编写。
'''

'''
6.ORM 模型互转（与 SQLAlchemy）
实际项目中，Pydantic 常与ORM 框架（如 SQLAlchemy）配合使用，实现数据库模型（ORM）与Pydantic 模型的双向互转： 数据管理

ORM → Pydantic：将数据库查询的 ORM 对象转换为 Pydantic 模型，用于 API 响应（字段过滤、类型验证）；

Pydantic → ORM：将 Pydantic 验证后的请求体数据转换为 ORM 对象，用于数据库插入 / 更新。

核心配置：model_config = {"from_attributes": True}（Pydantic v2），实现 ORM 对象到 Pydantic 模型的无缝转换。
'''

'''
6.1 前置准备
安装依赖：
pip install sqlalchemy==2.0.48 pydantic==2.12.5
'''

'''
6.2 核心互转示例
'''
# from datetime import datetime
# from typing import Optional
# from pydantic import BaseModel, Field, EmailStr
# from sqlalchemy import create_engine, Column, Integer, String, DateTime
# from sqlalchemy.orm import declarative_base, sessionmaker
# # ---------------------- 1. 初始化SQLAlchemy ----------------------
# # 数据库连接（SQLite内存数据库，无需实际文件）
# DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# # 会话工厂
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# # 基础ORM模型
# Base = declarative_base()
# # ---------------------- 2. 定义SQLAlchemy ORM模型 ----------------------
# class SQLUser(Base):
#     """数据库用户模型"""
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(50), nullable=False)
#     email = Column(String(100), unique=True, nullable=False)
#     age = Column(Integer, nullable=True)
#     create_time = Column(DateTime, default=datetime.now, nullable=False)
# # 创建数据库表
# Base.metadata.create_all(bind=engine)
# # ---------------------- 3. 定义Pydantic模型 ----------------------
# # 请求体模型：创建/更新用户（验证输入数据）
# class UserCreate(BaseModel):
#     name: str = Field(min_length=2, max_length=50)
#     email: EmailStr
#     age: Optional[int] = Field(default=None, ge=0)
# # 响应模型：返回用户信息（与ORM模型映射，支持ORM对象转换）
# class UserResponse(BaseModel):
#     id: int
#     name: str
#     email: EmailStr
#     age: Optional[int]
#     create_time: datetime
#     # 核心配置：支持从ORM对象的属性中读取数据（必选）
#     model_config = {"from_attributes": True}
# # ---------------------- 4. 数据库操作与模型互转 ----------------------
# # 依赖：获取数据库会话
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
# # 4.1 Pydantic → ORM：验证后的数据转换为ORM对象，插入数据库
# db = next(get_db())
# # 模拟FastAPI请求体验证后的Pydantic对象
# user_pydantic = UserCreate(name="张三", email="zhangsan@example.com", age=25)  # type: ignore
# # 将Pydantic模型转为字典，再创建ORM对象
# user_orm = SQLUser(**user_pydantic.model_dump())
# # 插入数据库
# db.add(user_orm)
# db.commit()
# db.refresh(user_orm)  # 刷新ORM对象，获取数据库自动生成的id/create_time
# print("✅ Pydantic → ORM 插入成功：", user_orm.id, user_orm.name)
# # 4.2 ORM → Pydantic：将数据库查询的ORM对象转换为Pydantic模型
# # 查询ORM对象：.filter(SQLUser.id == user_orm.id)：添加查询条件。相当于 SQL 语句中的 WHERE id = ?，意思是筛选出该表中 id 等于 user_orm.id 的记录。
# db_user = db.query(SQLUser).filter(SQLUser.id == user_orm.id).first()
# # 直接将ORM对象传入Pydantic模型（基于from_attributes=True）
# user_response = UserResponse.model_validate(db_user)
# print("✅ ORM → Pydantic 转换成功：")
# print(user_response.model_dump_json(indent=2))
# # 4.3 批量ORM → Pydantic：查询多个ORM对象，批量转换
# db_users = db.query(SQLUser).all()
# user_responses = [UserResponse.model_validate(user) for user in db_users]
# print("✅ 批量ORM → Pydantic：", len(user_responses), "条数据")

'''
6.3 核心知识点
Pydantic → ORM：通过model_dump()将 Pydantic 模型转换为字典，再将字典解包传入 ORM 模型构造函数，实现数据转换；
ORM → Pydantic：核心依赖model_config = {"from_attributes": True}，允许 Pydantic 模型从对象属性中读取数据（而非仅从字典），完美适配 SQLAlchemy 的 ORM 对象；
model_validate：Pydantic v2 中用于数据验证并创建模型的通用方法，支持字典、ORM 对象、自定义对象等多种输入；
字段映射：Pydantic 模型的字段名必须与 ORM 模型的属性名一致，否则无法自动映射（可通过Field(alias="xxx")解决字段名不一致问题）；
批量转换：通过列表推导式，将查询到的 ORM 对象列表批量转换为 Pydantic 模型列表，适合批量查询的 API 响应。
'''

'''
6.4 字段名不一致解决方案（alias 别名）
若 Pydantic 模型与 ORM 模型的字段名不一致，可通过 Pydantic 的alias别名实现映射：
'''
# from pydantic import BaseModel, Field
# from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import declarative_base

# Base = declarative_base()
# # ORM模型：字段名user_name
# class SQLUser(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     user_name = Column(String(50), nullable=False)
# # Pydantic模型：字段名name，通过alias映射到ORM的user_name
# class UserResponse(BaseModel):
#     id: int
#     name: str = Field(alias="user_name")  # 别名映射
#     model_config = {"from_attributes": True}
# # ORM → Pydantic：自动通过别名映射
# user_orm = SQLUser(id=1, user_name="张三")
# user_pydantic = UserResponse.model_validate(user_orm)
# print(user_pydantic.name)  # 输出：张三

'''
五、精进篇：实战优化与避坑
'''

'''
1.性能优化
Pydantic v2 基于 Rust 重写核心，性能比 v1 提升 5-50 倍，但在高频数据验证场景（如高并发 API、大数据量清洗）中，仍可通过以下技巧进一步优化性能，提升验证效率。 操作系统
'''

'''
1.1.核心性能优化技巧
（1）使用 pydantic.dataclasses 替代 BaseModel（简单场景）
对于无复杂嵌套、无自定义验证器的简单数据模型，使用 Pydantic 的dataclasses替代BaseModel，性能提升约30%-50%，因为dataclasses的底层实现更轻量。
'''
# from pydantic import dataclasses, Field
# from datetime import datetime
# # 轻量数据模型：使用pydantic.dataclasses
# @dataclasses.dataclass
# class SimpleUser:
#     id: int = Field(ge=1)
#     name: str = Field(min_length=2)
#     create_time: datetime = Field(default_factory=datetime.now)
# # 实例化与验证（用法与BaseModel一致）
# user = SimpleUser(id=1001, name="张三")
# print("✅ pydantic.dataclasses：", user.id, user.name)
# '''
# 适用场景：简单的纯数据模型、无嵌套、无自定义验证器的场景；
# 不适用场景：复杂嵌套模型、自定义验证器、模型继承、配置管理等场景。
# '''

'''
（2）预编译验证器（复用验证逻辑）
Pydantic 模型的__pydantic_validator__是预编译的验证器对象，可提前获取并复用，避免重复创建验证器，提升高频验证场景的性能。
'''
# from pydantic import BaseModel, Field
# class User(BaseModel):
#     id: int = Field(ge=1)
#     name: str = Field(min_length=2)
# # 预编译验证器（提前获取，全局复用）
# user_validator = User.__pydantic_validator__
# # 高频验证：直接使用预编译的验证器
# for i in range(3):
#     data = {"id": 1000 + i, "name": f"用户{i}"}
#     user = user_validator.validate_python(data)
#     print(f"✅ 预编译验证器：{user.id}，{user.name}")
#     # 输出:
#     # ✅ 预编译验证器：1000，用户0
#     # ✅ 预编译验证器：1001，用户1
#     # ✅ 预编译验证器：1002，用户2

'''
（3）关闭不必要的功能
通过model_config关闭 Pydantic 的不必要功能，减少验证开销：
str_strip_whitespace=False：无需去除字符串空格时关闭；
validate_default=False：默认值无需验证时关闭；
ignored_types：忽略无需验证的类型。
'''
# from pydantic import BaseModel
# class OptimizedUser(BaseModel):
#     id: int
#     name: str
#     model_config = {
#         "str_strip_whitespace": False,  # 关闭字符串去空格
#         "validate_default": False,      # 关闭默认值验证
#     }

'''
（4）使用 model_construct 处理内部可信数据
对于内部生成的可信数据（如数据库查询结果、内部计算数据），使用model_construct替代model_validate/ 直接实例化，跳过所有验证和类型转换，性能提升10 倍以上。
'''
# from pydantic import BaseModel
# class User(BaseModel):
#     id: int
#     name: str
# # 内部可信数据，直接构建模型（无验证）
# # 注意：model_construct无任何验证，仅用于内部可信数据，禁止用于外部输入数据。
# user = User.model_construct(id=1001, name="张三")
# print("✅ model_construct：", user.model_dump())  # 输出：{"id": 1001, "name": "张三"}

'''
（5）批量验证使用底层 pydantic_core API
处理大数据量批量验证（如十万 / 百万条数据）时，直接使用 Pydantic 的底层核心库pydantic_core的 API，绕过高层封装，提升验证效率。
'''
# from pydantic_core import SchemaValidator, core_schema
# # 定义底层 schema
# user_schema = core_schema.typed_dict_schema({
#     "id": core_schema.typed_dict_field(core_schema.int_schema(ge=1)),
#     "name": core_schema.typed_dict_field(core_schema.str_schema(min_length=2)),
# })
# # 创建底层验证器
# validator = SchemaValidator(user_schema)
# # 批量验证大数据量
# batch_data = [{"id": 1, "name": "张三"}, {"id": 2, "name": "李四"}, {"id": 3, "name": "王五"}]
# for data in batch_data:
#     result = validator.validate_python(data)
#     print("✅ 底层API批量验证：", result)
#     # 输出:
#     # ✅ 底层API批量验证： {'id': 1, 'name': '张三'}
#     # ✅ 底层API批量验证： {'id': 2, 'name': '李四'}
#     # ✅ 底层API批量验证： {'id': 3, 'name': '王五'}

'''
1.2.性能优化总结
优化方式	                            性能提升	适用场景	        注意事项
pydantic.dataclasses 替代 BaseModel	    30%-50%	    简单无嵌套模型	    不支持复杂验证 / 继承
预编译验证器	                        20%-30%	    高频单模型验证	    全局复用，避免重复创建
关闭不必要功能	                        10%-20%	    所有场景	        按需关闭，避免功能缺失
model_construct 无验证构建	            10 倍 +	    内部可信数据	    禁止用于外部输入
底层pydantic_core API	                50%-100%	大数据量批量验证	底层 API，使用成本较高
'''

'''
2.调试与测试
Pydantic 开发过程中，验证错误的快速定位和模型的单元测试是提升开发效率、保证代码质量的关键，以下是贴合实际项目的调试技巧和单元测试规范（基于 pytest）。
'''

'''
2.1.验证错误高级调试技巧
Pydantic 的ValidationError包含完整的错误信息（错误位置、原因、输入值、错误类型），通过解析这些信息，可快速定位问题，以下是实用的调试技巧。
'''

'''
（1）按字段分组错误（快速定位问题字段）
将验证错误按字段名分组，便于快速查看每个字段的所有错误，适合多字段验证失败的场景。
'''
# from pydantic import BaseModel, Field, ValidationError
# class User(BaseModel):
#     id: int = Field(ge=1)
#     name: str = Field(min_length=2, max_length=20)
#     age: int = Field(ge=0, le=120)
# # 模拟多字段验证失败
# try:
#     User(id=0, name="A", age=150)
# except ValidationError as e:
#     # 按字段分组错误
#     field_errors = {}
#     for err in e.errors():
#         field = err["loc"][0]  # 错误字段名
#         msg = err["msg"]       # 错误信息
#         field_errors[field] = field_errors.get(field, []) + [msg]
#     print("✅ 按字段分组错误：")
#     for field, msgs in field_errors.items():
#         print(f"字段{field}：{msgs}")

'''
（2）提取错误类型与输入值（精准排查）
从ValidationError中提取错误类型和原始输入值，便于精准排查问题（如类型转换失败、正则不匹配等）。
'''
# from pydantic import BaseModel, ValidationError
# class User(BaseModel):
#     id: int
#     name: str
# try:
#     User(id="abc", name=123)
# except ValidationError as e:
#     print("✅ 精准错误信息：")
#     for err in e.errors():
#         print(f"位置：{err['loc']} | 类型：{err['type']} | 输入值：{err['input']} | 原因：{err['msg']}")

'''
（3）打印格式化的 JSON 错误（接口调试）
在 API 开发中，将ValidationError转换为格式化的 JSON 字符串，便于前端 / 调用方解析错误信息。
'''
# from pydantic import BaseModel, Field, ValidationError
# class User(BaseModel):
#     id: int = Field(ge=1)
#     name: str = Field(min_length=2)
# try:
#     User(id=0, name="A")
# except ValidationError as e:
#     # 格式化JSON错误，带缩进
#     json_error = e.json(indent=2)
#     print("✅ 格式化JSON错误：")
#     print(json_error)

'''
2.2.Pydantic 模型单元测试（基于 pytest）
Pydantic 模型是项目的数据基础，对模型进行单元测试可保证验证规则的正确性，避免因规则修改导致的线上问题。
'''

'''
（1）前置准备
安装依赖：
pip install pytest==9.0.2
'''

'''
（2）单元测试规范示例
创建Pydantic模型文件user.py
python -m pytest ./tests/test_pydantic_models.py -v
'''
# # ./models/user.py
# import re
# from typing import Optional, List
# from pydantic import BaseModel, Field, field_validator
# class User(BaseModel):
#     id: int = Field(ge=1, description="用户 ID")
#     name: str = Field(min_length=2, max_length=20, description="用户名，2-20 字符")
#     age: Optional[int] = Field(default=None, ge=0, le=120, description="年龄，0-120")
#     email: str = Field(description="合法邮箱格式")
#     is_valid: bool = Field(default=True, description="用户状态")

#     @classmethod
#     @field_validator('email')
#     def validate_email(cls, v: str) -> str:
#         pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#         if not re.match(pattern, v):
#             raise ValueError('无效的邮箱格式')
#         return v
    
# # ./models/__init__.py
# from .user import User
# __all__ = ["User"]

# # ./tests/test_pydantic_models.py
# import pytest
# from pydantic import ValidationError
# from models import User  # 从业务模块导入需要测试的Pydantic模型
# # ---------------------- 测试用户模型 ----------------------
# class TestUserModel:
#     # 合法用例：正常实例化，验证字段值正确
#     def test_user_valid(self):
#         user = User(id=1001, name="张三", age=25, email="zhangsan@example.com")
#         assert user.id == 1001
#         assert user.name == "张三"
#         assert user.age == 25
#         assert user.email == "zhangsan@example.com"
#     # 非法用例：id小于1，验证报错
#     def test_user_invalid_id(self):
#         with pytest.raises(ValidationError) as e:
#             User(id=0, name="张三", age=25, email="zhangsan@example.com")
#         # 断言错误类型为greater_than_or_equal
#         assert "greater_than_or_equal" in str(e.value)
#         # 断言错误字段为id
#         assert "id" in str(e.value)
#     # 非法用例：name长度不足，验证报错
#     def test_user_invalid_name_length(self):
#         with pytest.raises(ValidationError) as e:
#             User(id=1002, name="A", age=30, email="lisi@example.com")
#         assert "string_min_length" in str(e.value)
#         assert "name" in str(e.value)
#     # 非法用例：邮箱格式错误，验证报错
#     def test_user_invalid_email(self):
#         with pytest.raises(ValidationError) as e:
#             User(id=1003, name="李四", age=35, email="lisi.example.com")
#         assert "value_error" in str(e.value)
#         assert "email" in str(e.value)

'''
（4）测试核心原则
全覆盖：覆盖模型的所有字段约束（如ge/min_length/ 正则 / 自定义验证器）；
合法 + 非法：每个字段都要测试合法输入和多种非法输入；
精准断言：不仅断言报错，还要断言错误类型和错误字段，避免误判；
独立测试：每个测试用例独立，不依赖其他用例的执行结果；
批量测试：使用@pytest.mark.parametrize实现批量参数化测试，减少重复代码。
'''

'''
（5）参数化测试（批量测试多种用例）
使用pytest.mark.parametrize实现批量参数化测试，一次性测试多种合法 / 非法用例，减少代码冗余。
python -m pytest ./tests/test_pydantic_param.py -vs
'''

'''
3.高频避坑指南 & 生产最佳实践
结合 Pydantic v2 的使用场景和版本特性，整理了开发中最易踩的坑和生产环境的最佳实践，帮助规避问题、规范代码。
'''

'''
1.1.高频避坑指南（Pydantic v2 重点）
（1）混淆 v1 和 v2 的 API（最常见）
Pydantic v2 对部分核心 API 进行了重命名 / 废弃，若沿用 v1 的 API 会导致报错，核心差异如下：

特性	    v1 废弃 API	      v2 替代 API	            注意事项
验证器	    @validator	      @field_validator	        验证器装饰器重命名，参数略有变化
转字典	    model.dict()	  model.model_dump()	    转字典必须使用新方法，dict () 已废弃
转 JSON	    model.json()	  model.model_dump_json()	转 JSON 必须使用新方法，json () 已废弃
数据验证	parse_obj()	      model_validate()	        数据验证并创建模型的通用方法
模型配置	class Config:	  model_config = {}	        模型配置从类改为字典，语法完全变化

避坑：开发前熟记核心 API 差异，v2 的 BaseModel 兼容 v1，但内部实现不同。
'''

'''
（2）忽略 default 和 default_factory 的区别
default：固定默认值，模型加载时一次性生成，适合常量（如default=18）；

default_factory：动态默认值函数，每次实例化模型时执行，适合动态值（如时间、UUID、随机数）。

踩坑示例：使用 default 生成时间，所有实例的创建时间都相同：

避坑：动态生成的值（时间、UUID、随机数）必须使用default_factory，禁止使用default。
'''
# from pydantic import BaseModel
# from datetime import datetime
# # 错误：固定默认值，所有实例create_time相同
# class BadUser(BaseModel):
#     create_time: datetime = datetime.now()
# # 正确：动态默认值，每次实例化生成新时间
# class GoodUser(BaseModel):
#     create_time: datetime = Field(default_factory=datetime.now)
# u1 = BadUser()
# u2 = BadUser()
# print(u1.create_time == u2.create_time)  # 输出：True（坑点）
# g1 = GoodUser()
# g2 = GoodUser()
# print(g1.create_time == g2.create_time)  # 输出：False（正确）

'''
（3）开启严格模式后期望自动类型转换
严格模式的核心是关闭所有隐式类型转换，若开启严格模式后仍传入非匹配类型（如int字段传字符串"123"），会直接报错，而非自动转换。

避坑：严格模式仅用于高精度验证场景，普通场景使用默认的非严格模式，避免不必要的类型适配成本。
'''
# from pydantic import BaseModel, ConfigDict
# # 开启严格模式的模型
# class User(BaseModel):
#     model_config = ConfigDict(strict=True)  # 严格模式核心配置
#     age: int  # 期望传入整数类型
# # 非严格模式下：传入字符串"25"会自动转为int(25)
# # 严格模式下：传入字符串会直接抛出类型错误
# try:
#     user = User(age="25")  # 错误：期望int，实际传了str
#     print(user.age)
# except ValueError as e:
#     print(f"报错信息：{e}")

'''
（4）模型继承时重写字段的默认值错误
子模型重写父模型字段时，若仅修改约束不指定默认值，会丢失父模型的默认值，导致字段变为必填。

避坑：子模型重写字段时，若需要保留父模型的默认值，必须显式指定，避免字段从可选变为必填。
'''
# from pydantic import BaseModel, Field
# class BaseUser(BaseModel):
#     age: int = Field(default=18, ge=0)  # 有默认值，可选字段
# # 错误：重写约束但未指定默认值，age变为必填字段
# class BadUser(BaseUser):
#     age: int = Field(ge=0, le=120)  # 丢失默认值18
# # 正确：重写约束并保留默认值
# class GoodUser(BaseUser):
#     age: int = Field(default=18, ge=0, le=120)
# # BadUser实例化必须传age，否则报错
# BadUser()  # 报错：missing required field 'age'
# # GoodUser()  # 正常，使用默认值18

'''
（5）使用 model_construct 处理外部输入数据
model_construct 是无任何验证的模型构建方法，若用于处理外部输入数据（如 API 请求体、爬虫数据），会导致非法数据进入模型，引发线上问题。 网络安全

避坑：model_construct 仅用于内部生成的可信数据（如数据库查询结果、内部计算数据），外部输入数据必须使用model_validate/ 直接实例化进行验证。
'''
# from pydantic import BaseModel, PositiveInt
# # 定义模型：age要求是正整数
# class User(BaseModel):
#     name: str
#     age: PositiveInt  # 必须是大于0的整数
# # 模拟外部不可信数据（如API请求体，age为负数，属于非法数据）
# external_data = {"name": "小明", "age": -18}
# # 错误用法：用 model_construct 处理外部数据，跳过校验
# bad_user = User.model_construct(**external_data)
# print(f"model_construct构建的模型：{bad_user}")
# print(f"age是否为正整数：{bad_user.age > 0}")  # 输出False，非法数据进入模型
# # 正确用法：用model_validate/直接实例化处理外部数据，触发校验
# try:
#     good_user = User.model_validate(external_data)  # 等价于 User(** external_data)
#     print(good_user)
# except ValueError as e:
#     print(f"校验报错：{e}")  # 捕获非法数据的校验错误

'''
（6）配置管理时忽略环境变量的优先级
使用pydantic-settings时，环境变量的优先级高于.env 文件，.env 文件高于字段默认值，若本地设置了环境变量，会覆盖.env 文件的配置，导致本地调试与生产环境不一致。

# 本地终端设置环境变量

# 1. Windows CMD（命令提示符）
# 设置临时环境变量（仅当前窗口有效）：
set APP_PORT=9000
# 查看是否生效：
echo %APP_PORT%

# 2. Windows PowerShell
# 设置临时环境变量（仅当前会话有效）
$env:APP_PORT=9000
# 查看是否生效：
$env:APP_PORT

# Linux/macOS终端
export APP_PORT=9000
'''
# from pydantic_settings import BaseSettings, SettingsConfigDict
# class Settings(BaseSettings):
#     app_port: int = 7000
#     model_config = SettingsConfigDict(env_file=".env")  # .env中APP_PORT=8000
# settings = Settings()
# print(settings.app_port)  # 输出：9000（被环境变量覆盖，坑点）

'''
1.2.生产环境最佳实践
（1）模型规范：统一基础模型，复用通用字段
所有业务模型都继承自定义的基础模型（如BaseModelMixin），复用通用字段（id、create_time、update_time）和全局配置，保证项目模型的一致性。
'''
# from pydantic import BaseModel, Field
# from datetime import datetime
# from uuid import uuid4, UUID
# # 项目统一基础模型
# class BaseModelMixin(BaseModel):
#     id: UUID = Field(default_factory=uuid4, description="全局唯一UUID主键")
#     create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
#     update_time: datetime = Field(default_factory=datetime.now, description="更新时间")
#     # 全局模型配置
#     model_config = {
#         "str_strip_whitespace": True,  # 全局去除字符串空格
#         "from_attributes": True,       # 全局支持ORM对象转换
#         "extra": "ignore",             # 全局忽略冗余字段
#     }
# # 业务模型继承基础模型
# class User(BaseModelMixin):
#     name: str = Field(min_length=2, max_length=20)
#     email: str

'''
（2）验证规范：自定义类型复用，避免重复验证器
项目中高频的验证规则（如手机号、身份证号、偶数、密码强度），通过自定义数据类型实现一次定义、全局复用，避免在多个模型中重复编写field_validator，提升代码可维护性。 网络安全

以手机号校验为例，演示如何通过自定义类型实现一次定义、全局复用，避免重复编写校验器。

以手机号校验为例，演示如何通过自定义类型实现一次定义、全局复用，避免重复编写校验器。
'''

'''
传统写法（重复校验器，弊端明显）
多个模型中重复写field_validator，代码冗余且维护成本高：
'''
# from pydantic import BaseModel, field_validator
# import re
# # 模型1：用户注册
# class UserRegister(BaseModel):
#     phone: str
#     @field_validator("phone")
#     def validate_phone(cls, v):
#         if not re.match(r"^1[3-9]\d{9}$", v):
#             raise ValueError("手机号格式错误")
#         return v
# # 模型2：订单通知
# class OrderNotice(BaseModel):
#     phone: str
#     # 重复编写相同的手机号校验器
#     @field_validator("phone")
#     def validate_phone(cls, v):
#         if not re.match(r"^1[3-9]\d{9}$", v):
#             raise ValueError("手机号格式错误")
#         return v

'''
优化写法（自定义类型，全局复用）
通过Annotated+AfterValidator自定义手机号类型，一次定义可在所有模型中使用：

核心优势
代码复用：无需在多个模型中重复编写相同校验逻辑；
维护便捷：若需修改校验规则（如新增手机号号段），仅需修改自定义类型的校验函数；
类型清晰：自定义类型名（如PhoneNumber）语义明确，提升代码可读性。
'''
# from pydantic import BaseModel, AfterValidator
# from typing import Annotated
# import re
# # 定义手机号校验函数
# def validate_phone(v: str) -> str:
#     if not re.match(r"^1[3-9]\d{9}$", v):
#         raise ValueError("手机号格式错误")
#     return v
# # 自定义可复用的手机号类型
# PhoneNumber = Annotated[str, AfterValidator(validate_phone)]
# # 模型1：用户注册（直接使用自定义类型）
# class UserRegister(BaseModel):
#     phone: PhoneNumber
# # 模型2：订单通知（直接复用，无需重复写校验器）
# class OrderNotice(BaseModel):
#     phone: PhoneNumber
# # 测试验证效果
# if __name__ == "__main__":
#     # 正确数据
#     user = UserRegister(phone="13800138000")
#     print(user.phone)  # 输出：13800138000
#     # 错误数据（触发校验报错）
#     try:
#         order = OrderNotice(phone="123456")
#     except ValueError as e:
#         print(f"报错：{e}")  # 输出校验错误信息

'''
（3）配置管理规范：分离多环境配置
使用pydantic-settings实现多环境配置分离（开发 / 测试 / 生产），通过环境变量指定加载的.env 文件，避免不同环境的配置混淆。

创建多环境配置文件：
.env.dev：开发环境配置
.env.test：测试环境配置
.env.prod：生产环境配置（敏感信息如数据库密码需通过配置中心管理，不直接写入文件）
'''
# from pydantic_settings import BaseSettings, SettingsConfigDict
# import os
# # 根据环境变量加载不同的.env文件
# env = os.getenv("ENV", "dev")  # 默认开发环境
# class Settings(BaseSettings):
#     app_name: str
#     app_port: int
#     database_url: str

#     model_config = SettingsConfigDict(
#         env_file=f".env.{env}",  # 加载.env.dev/.env.test/.env.prod
#         env_file_encoding="utf-8",
#         case_sensitive=False,
#     )
# settings = Settings()

'''
4）错误处理规范：统一验证错误返回格式
在 API 开发中，统一 Pydantic 验证错误的返回格式，增加业务错误码，便于前端 / 调用方统一解析，避免直接返回 Pydantic 的原始错误信息。
'''
# from fastapi import FastAPI, Request, HTTPException
# from fastapi.responses import JSONResponse
# from pydantic import ValidationError

# app = FastAPI()

# # 统一验证错误处理
# @app.exception_handler(ValidationError)
# async def validation_exception_handler(request: Request, exc: ValidationError):
#     return JSONResponse(
#         status_code=422,
#         content={
#             "code": 42200,  # 自定义业务错误码
#             "msg": "数据验证失败",
#             "data": exc.errors(),  # 结构化错误信息
#             "request_url": str(request.url)
#         }
#     )

'''
（5）性能规范：高频场景按需优化
根据项目的业务场景，按需使用性能优化技巧（如pydantic.dataclasses、model_construct、预编译验证器），避免过度优化：

高并发 API：使用pydantic.dataclasses（简单模型）、预编译验证器；
'''
# from pydantic import dataclasses, field_validator, TypeAdapter
# import datetime
# # 用dataclasses替代BaseModel，轻量且性能更高
# @dataclasses.dataclass
# class OrderRequest:
#     order_id: str
#     amount: float
#     create_time: datetime.datetime

#     # 预编译验证器（复用校验逻辑，减少重复计算）
#     @field_validator("amount")
#     def validate_amount(cls, v):
#         if v <= 0:
#             raise ValueError("金额必须大于0")
#         return v

# # 高并发场景下，dataclasses 比 BaseModel 初始化更快
# req = OrderRequest(order_id="OD123", amount=99.9, create_time=datetime.datetime.now())
# # 使用 TypeAdapter 进行序列化
# adapter = TypeAdapter(OrderRequest)
# print(adapter.dump_python(req)) # 输出: {'order_id': 'OD123', 'amount': 99.9, 'create_time': datetime.datetime(2026, 3, 29, 10, 5, 33, 156148)}

'''
内部数据处理：使用model_construct无验证构建；
'''
# from pydantic import BaseModel
# class User(BaseModel):
#     id: int
#     name: str

# # 内部可信数据（如数据库查询结果），用model_construct跳过校验提速
# db_data = {"id": 1, "name": "小明"}
# user = User.model_construct(**db_data)  # 无校验，性能提升约30%
# print(user.model_dump())    # 输出: {'id': 1, 'name': '小明'}

'''
大数据量清洗：使用底层pydantic_core API 批量验证
'''
# from pydantic_core import SchemaValidator, core_schema
# # 定义校验schema
# schema = core_schema.typed_dict_schema({
#     "id": core_schema.typed_dict_field(core_schema.int_schema(ge=1)),
#     "name": core_schema.typed_dict_field(core_schema.str_schema(min_length=1))
# })
# validator = SchemaValidator(schema)
# # 批量验证1000条数据（比循环实例化BaseModel快10倍+）
# batch_data = [{"id": i, "name": f"用户{i}"} for i in range(1, 1001)]
# validated_data = [validator.validate_python(data) for data in batch_data]
# print(f"批量验证完成，共{len(validated_data)}条")    # 输出: 批量验证完成，共1000条

'''
（6）测试规范：全覆盖模型单元测试
对所有 Pydantic 模型编写单元测试，覆盖所有字段约束和验证规则，使用 CI/CD 工具（如 GitLab CI、GitHub Actions）自动运行测试，避免因模型规则修改导致的线上问题。

用pytest编写 Pydantic 模型单元测试，覆盖字段约束和验证规则：
'''

'''
（7）文档规范：为所有字段添加描述
为 Pydantic 模型的所有字段添加description描述，FastAPI 会自动将描述同步到接口文档，提升接口的可维护性和可读性，便于团队协作。
'''
# from fastapi import FastAPI
# from pydantic import BaseModel, Field

# app = FastAPI(title="医院互联网医院接口")

# class Patient(BaseModel):
#     id: int = Field(..., description="患者唯一标识，自增主键")
#     name: str = Field(..., min_length=2, description="患者姓名，至少2个字符")
#     age: int = Field(None, ge=0, le=150, description="患者年龄，0-150岁")
#     phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="患者手机号，11位有效号码")

# @app.post("/patient/add", summary="新增患者")
# def add_patient(patient: Patient):
#     return {"code": 200, "data": patient}

# # 启动后访问 http://127.0.0.1:8000/docs 可看到带描述的接口文档
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

'''
（8）离线文档包：解决 FastAPI Swagger UI 加载问题
在阿里云 PyPI 镜像源（https://mirrors.aliyun.com/pypi/simple/）中，按易用性优先级推荐如下：

包名	                    功能特点	                                                          安装命令	                                适用场景
fastapi-offline	            官方推荐的离线文档包，自动内置 Swagger/Redoc 静态资源，无需手动下载文件	 pip install fastapi-offline	          快速解决 CDN 加载失败，追求极简配置
fastapi-swagger	            集成最新版 Swagger UI，本地化部署无外部 CDN 依赖	                    pip install fastapi-swagger	            想要使用最新 Swagger UI 版本
fastapi-swagger-ui-theme	为 Swagger UI 添加暗黑模式 / 样式优化，同时本地化资源	                pip install fastapi-swagger-ui-theme	需自定义 Swagger UI 外观
'''

'''
最推荐：fastapi-offline（一行代码解决）
pip install fastapi-offline
pip install fastapi-swagger
pip install fastapi-swagger-ui-theme

启动后访问http://127.0.0.1:8000/docs，Swagger UI 会从本地加载资源，不再依赖外部 CDN。
'''
from fastapi_offline import FastAPIOffline
# 替换原FastAPI实例，其余代码完全不变
app = FastAPIOffline(title="医院互联网医院接口")

@app.get("/")
def read_root():
    return {"msg": "Swagger UI已本地化加载"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

'''
1.3.常见错误及解决
字段类型不匹配：确保输入数据类型与注解一致，或使用 coerce_numbers_to_str 开启自动转换
额外字段报错：在 model_config 中设置 extra='allow' 允许额外字段
环境变量读取失败：检查 .env 文件路径是否正确，字段名与环境变量名是否匹配
嵌套模型验证失败：逐层检查子模型的字段是否符合要求
'''