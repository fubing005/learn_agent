# -*- coding: utf-8 -*-
"""
电商订单管理系统 - 核心配置与数据模型
========================================
功能：
    1. 定义SQLAlchemy 2.0的基础模型（DeclarativeBase）
    2. 配置数据库连接与会话工厂
    3. 定义业务数据模型（用户、商品、分类、订单、订单项）
    4. 实现通用分页数据结构
依赖：
    - SQLAlchemy 2.0.48
    - Python 3.13.11
创建时间：2026-03-22
作者：inuex
版本：v1.0
"""
import datetime
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Generator, Sequence

from sqlalchemy import (
    create_engine,
    ForeignKey,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
    Mapped,
    mapped_column,
    relationship,
)


# --------------------------- 基础配置 ---------------------------
class Base(DeclarativeBase):
    """所有模型的抽象基类"""
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    create_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now(datetime.UTC), comment="创建时间"
    )
    update_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC),
        comment="更新时间"
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否删除（软删除）"
    )


# 数据库连接（SQLite，可替换为MySQL/PostgreSQL）
DATABASE_URL = "sqlite:///./mall.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # 设为True可打印SQL语句，便于学习
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --------------------------- 数据模型 ---------------------------
class User(Base):
    """用户模型"""
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="用户名")
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, comment="手机号")
    email: Mapped[str] = mapped_column(String(100), nullable=True, comment="邮箱")
    address: Mapped[str] = mapped_column(String(200), nullable=True, comment="收货地址")
    balance: Mapped[float] = mapped_column(Float, default=0.0, comment="账户余额")

    # 关联订单（一对多）
    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, balance={self.balance})>"


class Category(Base):
    """商品分类模型"""
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(50), unique=True, comment="分类名称")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="分类描述")

    # 关联商品（一对多）
    products: Mapped[List["Product"]] = relationship(
        "Product", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"


class Product(Base):
    """商品模型"""
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(100), index=True, comment="商品名称")
    price: Mapped[float] = mapped_column(Float, comment="商品价格")
    stock: Mapped[int] = mapped_column(Integer, default=0, comment="库存数量")
    sales: Mapped[int] = mapped_column(Integer, default=0, comment="销量")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="商品描述")
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), comment="分类ID")

    # 关联分类
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    # 关联订单项
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, price={self.price}, stock={self.stock})>"


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"

    order_no: Mapped[str] = mapped_column(String(32), unique=True, index=True, comment="订单编号")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="用户ID")
    total_amount: Mapped[float] = mapped_column(Float, default=0.0, comment="订单总金额")
    status: Mapped[str] = mapped_column(String(20), default="pending",
                                        comment="订单状态：pending/paid/shipped/completed/cancelled")
    payment_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True, comment="支付时间")

    # 关联用户
    user: Mapped["User"] = relationship("User", back_populates="orders")
    # 关联订单项
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, order_no={self.order_no}, status={self.status}, total_amount={self.total_amount})>"


class OrderItem(Base):
    """订单项模型（订单-商品 多对多关联）"""
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), comment="订单ID")
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), comment="商品ID")
    quantity: Mapped[int] = mapped_column(Integer, default=1, comment="购买数量")
    unit_price: Mapped[float] = mapped_column(Float, comment="购买时的单价")

    # 关联订单
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    # 关联商品
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"


# --------------------------- 分页数据结构 ---------------------------
@dataclass
class Pagination:
    """通用分页返回结构"""
    items: Sequence[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "items": [i.__dict__ for i in self.items],
            "pagination": {
                "total": self.total,
                "page": self.page,
                "page_size": self.page_size,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev
            }
        }


# --------------------------- 核心业务逻辑 ---------------------------
def create_tables() -> None:
    """创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功！")


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db_session: Session = SessionLocal()
    try:
        yield db_session
    except SQLAlchemyError as ex:
        db_session.rollback()
        raise ex
    finally:
        db_session.close()

