# -*- coding: utf-8 -*-
"""
电商订单管理系统 - 数据操作层（CRUD）
=====================================
功能：
    1. 实现商品、订单、用户等核心业务的增删改查
    2. 封装分页查询、条件过滤、排序等通用查询逻辑
    3. 处理电商核心业务逻辑（订单创建、库存扣减、状态更新）
    4. 实现事务管理与异常处理
依赖：
    - core.py（数据模型与数据库配置）
    - SQLAlchemy 2.0.48
创建时间：2026-03-22
作者：inuex
版本：v1.0
注意：
    1. 所有数据库操作需通过Session会话执行，禁止直接操作数据库连接
    2. 订单创建包含事务逻辑，异常时自动回滚
    3. 分页查询默认最大页大小为50，防止大数据量查询
"""
import datetime
from typing import List, Tuple, Sequence

from sqlalchemy import (
    select,
    func,
    and_,
    desc,
    asc,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    Session,
    joinedload,
    selectinload,
)

from mall.core import Category, Product, User, Pagination, Order, OrderItem


# ====================== 商品管理 ======================
def create_product(
        db: Session,
        name: str,
        price: float,
        category_id: int,
        stock: int = 0,
        description: str = None
) -> Product:
    """创建商品"""
    # 检查分类是否存在
    category = db.execute(select(Category).where(Category.id == category_id)).scalar_one_or_none()
    if not category:
        raise ValueError(f"分类ID {category_id} 不存在")

    db_product = Product(
        name=name,
        price=price,
        stock=stock,
        description=description,
        category_id=category_id
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_product_list(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        category_id: int = None,
        min_price: float = None,
        max_price: float = None,
        keyword: str = None,
        sort_by: str = "create_time",
        sort_order: str = "desc"
) -> Pagination:
    """
    分页查询商品列表（支持多条件过滤、排序）
    :param db: 数据库会话
    :param page: 页码
    :param page_size: 每页条数
    :param category_id: 分类ID（可选）
    :param min_price: 最低价格（可选）
    :param max_price: 最高价格（可选）
    :param keyword: 商品名称关键词（可选）
    :param sort_by: 排序字段（create_time/price/stock/sales）
    :param sort_order: 排序方向（asc/desc）
    :return: 分页结果
    """
    # 参数校验
    page = max(1, page)
    page_size = max(1, min(50, page_size))  # 限制最大页大小
    offset = (page - 1) * page_size

    # 构建查询条件
    conditions = [Product.is_deleted == False]

    if category_id:
        conditions.append(Product.category_id == category_id)
    if min_price is not None:
        conditions.append(Product.price >= min_price)
    if max_price is not None:
        conditions.append(Product.price <= max_price)
    if keyword:
        conditions.append(Product.name.like(f"%{keyword}%"))

    # 构建排序规则
    sort_column = getattr(Product, sort_by, Product.create_time)
    sort_func = desc if sort_order.lower() == "desc" else asc

    # 构建查询
    stmt = select(Product).options(
        joinedload(Product.category).load_only(Category.id, Category.name)  # 关联加载分类（只加载必要字段）
    ).where(and_(*conditions)).order_by(sort_func(sort_column)).offset(offset).limit(page_size)

    # 执行查询
    products: Sequence[Product] = db.execute(stmt).scalars().all()

    # 查询总数（复用条件，不包含分页和排序）
    count_stmt = select(func.count(Product.id)).where(and_(*conditions))
    total = db.execute(count_stmt).scalar()

    # 计算分页信息
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_prev = page > 1

    return Pagination(
        items=products,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )


# ====================== 订单管理 ======================
def generate_order_no() -> str:
    """生成唯一订单编号"""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(datetime.datetime.now().microsecond)[:4]


def create_order(
        db: Session,
        user_id: int,
        product_items: List[Tuple[int, int]]  # [(product_id, quantity), ...]
) -> Order:
    """
    创建订单（包含事务管理、库存检查、金额计算）
    :param db: 数据库会话
    :param user_id: 用户ID
    :param product_items: 商品列表 [(商品ID, 数量), ...]
    :return: 创建的订单
    """
    if not product_items:
        raise ValueError("订单中至少包含一个商品")

    # 1. 检查用户是否存在
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise ValueError(f"用户ID {user_id} 不存在")

    # 2. 检查商品库存并计算总金额
    total_amount = 0.0
    order_items = []

    for product_id, quantity in product_items:
        if quantity <= 0:
            raise ValueError(f"商品ID {product_id} 购买数量必须大于0")

        # 加锁查询商品（防止超卖）
        product = db.execute(
            select(Product).where(and_(Product.id == product_id, Product.is_deleted == False)).with_for_update()
        ).scalar_one_or_none()

        if not product:
            raise ValueError(f"商品ID {product_id} 不存在或已删除")

        if product.stock < quantity:
            raise ValueError(f"商品 {product.name} 库存不足（当前库存：{product.stock}，请求数量：{quantity}）")

        # 计算金额
        item_amount = product.price * quantity
        total_amount += item_amount

        # 创建订单项
        order_items.append(OrderItem(
            product_id=product_id,
            quantity=quantity,
            unit_price=product.price
        ))

        # 扣减库存，增加销量
        product.stock -= quantity
        product.sales += quantity

    # 3. 创建订单
    order = Order(
        order_no=generate_order_no(),
        user_id=user_id,
        total_amount=total_amount,
        status="pending",
        items=order_items
    )

    try:
        db.add(order)
        db.commit()
        db.refresh(order)

        # 关联加载订单项和商品信息
        db.execute(
            select(Order).options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.user)
            ).where(Order.id == order.id)
        )

        return order
    except SQLAlchemyError as ex:
        db.rollback()
        raise ex


def get_order_list(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        user_id: int = None,
        status: str = None,
        start_time: datetime.datetime = None,
        end_time: datetime.datetime = None
) -> Pagination:
    """
    分页查询订单列表（支持多条件过滤）
    """
    page = max(1, page)
    page_size = max(1, min(50, page_size))
    offset = (page - 1) * page_size

    # 构建条件
    conditions = [Order.is_deleted == False]

    if user_id:
        conditions.append(Order.user_id == user_id)
    if status:
        conditions.append(Order.status == status)
    if start_time:
        conditions.append(Order.create_time >= start_time)
    if end_time:
        conditions.append(Order.create_time <= end_time)

    # 构建查询（关联加载用户和订单项）
    stmt = select(Order).options(
        joinedload(Order.user).load_only(User.id, User.username, User.phone),
        selectinload(Order.items).joinedload(OrderItem.product).load_only(Product.id, Product.name, Product.price)
    ).where(and_(*conditions)).order_by(desc(Order.create_time)).offset(offset).limit(page_size)

    orders = db.execute(stmt).scalars().all()

    # 查询总数
    count_stmt = select(func.count(Order.id)).where(and_(*conditions))
    total = db.execute(count_stmt).scalar()

    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_prev = page > 1

    return Pagination(
        items=orders,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )


def update_order_status(
        db: Session,
        order_id: int,
        status: str,
        payment_time: datetime.datetime = None
) -> Order:
    """
    更新订单状态
    :param db: 数据库会话
    :param order_id: 订单ID
    :param status: 新状态
    :param payment_time: 支付时间（仅status=paid时需要）
    :return: 更新后的订单
    """
    valid_status = ["pending", "paid", "shipped", "completed", "cancelled"]
    if status not in valid_status:
        raise ValueError(f"无效的订单状态，可选值：{valid_status}")

    db_order = db.execute(select(Order).where(Order.id == order_id)).scalar_one_or_none()
    if not db_order:
        raise ValueError(f"订单ID {order_id} 不存在")

    # 如果是取消订单，恢复库存
    if status == "cancelled" and db_order.status != "cancelled":
        for i in db_order.items:
            db_product = db.execute(select(Product).where(Product.id == i.product_id)).scalar()
            if db_product:
                db_product.stock += i.quantity
                db_product.sales -= i.quantity

    # 更新订单状态
    db_order.status = status
    if status == "paid" and payment_time:
        db_order.payment_time = payment_time

    db.commit()
    db.refresh(db_order)
    return db_order

