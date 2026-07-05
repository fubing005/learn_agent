from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from sqlalchemy.sql import func  # 2.0+ 推荐的函数工具

# 注意：Base 需从之前优化后的 DeclarativeBase 子类导入
# 导入 Base 根据同步/异步场景选择
# from async_session import Base
from sync_session import Base


# ====================== 用户表模型（2.0+ 规范写法） ======================
class User(Base):
    """
    用户表模型
    表名：users
    核心字段：ID、用户名、邮箱、年龄、激活状态、创建/更新时间
    """
    __tablename__ = "users"

    # 1. 核心字段优化（2.0+ 规范 + 约束增强）
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="用户ID（自增主键）",
        autoincrement=True  # 显式声明自增（兼容多数据库）
    )
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="用户名（唯一，非空）",
        index=True  # 高频查询字段加索引，提升查询性能
    )
    email = Column(
        String(100),
        unique=True,
        nullable=True,
        comment="邮箱（唯一，可选）",
        index=True  # 邮箱查询场景多，添加索引
    )
    age = Column(
        Integer,
        default=0,
        nullable=False,  # 显式声明非空（默认值已保证，增强约束）
        comment="年龄（默认0）"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活（默认True）",
        index=True  # 状态字段高频过滤，添加索引
    )
    # 时间字段优化：使用 func.now() 替代 datetime.now（数据库层面生成时间，兼容异步）
    create_time = Column(
        DateTime,
        default=func.now(),  # 2.0+ 推荐，数据库服务器时间（更精准）
        nullable=False,
        comment="创建时间（自动生成）"
    )
    # 新增更新时间字段（业务常用，2.0+ 支持 onupdate）
    update_time = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),  # 数据更新时自动刷新
        nullable=False,
        comment="更新时间（自动更新）"
    )

    # 2. 复合索引（针对多字段查询场景，提升性能）
    __table_args__ = (
        # 示例：按「激活状态+创建时间」查询的复合索引
        Index("idx_user_active_create", "is_active", "create_time"),
    )

    # 3. 自定义方法优化（类型注解 + 实用方法）
    def __repr__(self) -> str:
        """自定义打印格式（类型注解增强）"""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', is_active={self.is_active})>"

    def to_dict(self) -> dict:
        """新增：模型转字典（业务常用，避免手动序列化）"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "age": self.age,
            "is_active": self.is_active,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
        }

