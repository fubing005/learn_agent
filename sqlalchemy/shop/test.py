# -*- coding: utf-8 -*-
"""
电商订单管理系统 - 功能测试脚本
=================================
功能：
    1. 验证数据库表创建
    2. 测试核心CRUD功能（商品创建、订单生成、状态更新）
    3. 验证分页查询、条件过滤、事务回滚等高级特性
    4. 模拟电商业务流程（用户下单→库存扣减→订单状态更新）
测试场景：
    - 商品分类初始化
    - 商品创建与分页查询
    - 订单创建（含库存检查）
    - 订单状态更新与库存恢复（取消订单）
    - 多条件过滤的商品查询
依赖：
    - core.py + crud.py（核心业务层）
    - SQLAlchemy 2.0.48
创建时间：2026-03-22
作者：inuex
版本：v1.0
运行方式：
    python -m mall.test
"""
import datetime

from sqlalchemy import (
    select,
)
from sqlalchemy.exc import SQLAlchemyError

from mall.core import create_tables, Category, Product, User, get_db
from mall.crud import create_product, create_order, get_product_list, update_order_status, get_order_list


# --------------------------- 测试代码 ---------------------------
def main():
    # 获取数据库会话
    db = next(get_db())

    try:
        # 1. 初始化分类
        electronics = db.execute(select(Category).where(Category.name == "电子产品")).scalar_one_or_none()
        if not electronics:
            electronics = Category(name="电子产品", description="手机、电脑、平板等")
            db.add(electronics)
            db.commit()

        # 2. 创建测试商品
        iphone = db.execute(select(Product).where(Product.name == "iPhone 15")).scalar_one_or_none()
        if not iphone:
            iphone = create_product(
                db,
                name="iPhone 15",
                price=5999.0,
                category_id=electronics.id,
                stock=100,
                description="苹果15手机，128G版本"
            )

        macbook = db.execute(select(Product).where(Product.name == "MacBook Pro")).scalar_one_or_none()
        if not macbook:
            macbook = create_product(
                db,
                name="MacBook Pro",
                price=12999.0,
                category_id=electronics.id,
                stock=50,
                description="苹果笔记本电脑，M3芯片"
            )

        # 3. 创建测试用户
        test_user = db.execute(select(User).where(User.username == "test_buyer")).scalar_one_or_none()
        if not test_user:
            test_user = User(
                username="test_buyer",
                phone="13800138000",
                email="test@example.com",
                address="北京市海淀区",
                balance=20000.0
            )
            db.add(test_user)
            db.commit()

        # 4. 创建订单（购买2个iPhone 15 + 1个MacBook Pro）
        try:
            order = create_order(
                db,
                user_id=test_user.id,
                product_items=[(iphone.id, 2), (macbook.id, 1)]
            )
            print(f"创建订单成功：{order}") # 输出: <Order(id=1, order_no=202603221724427528, status=pending, total_amount=24997.0)>
            print(f"订单总金额：{order.total_amount}") # 输出: 24997.0
            print(f"订单项数量：{len(order.items)}") # 输出: 2

            # 打印订单项详情
            for item in order.items:
                print(f"  - 商品：{item.product.name}，数量：{item.quantity}，单价：{item.unit_price}")
                # 输出:
                # - 商品：iPhone 15，数量：2，单价：5999.0
                # - 商品：MacBook Pro，数量：1，单价：12999.0

        except ValueError as e:
            print(f"创建订单失败：{e}") # 输出:

        # 5. 分页查询商品（测试多条件过滤）
        print("\n=== 分页查询商品（价格区间 5000-15000，按价格升序）===")
        product_pagination = get_product_list(
            db,
            page=1,
            page_size=5,
            min_price=5000.0,
            max_price=15000.0,
            sort_by="price",
            sort_order="asc"
        )
        print(f"总商品数：{product_pagination.total}") # 输出: 2
        print(f"当前页：{product_pagination.page}/{product_pagination.total_pages}") # 输出: 1/1
        print(f"是否有下一页：{product_pagination.has_next}") # 输出: False
        for product in product_pagination.items:
            print(f"  - {product.name}，价格：{product.price}，分类：{product.category.name}")
            # 输出:
            # - iPhone 15，价格：5999.0，分类：电子产品
            # - MacBook Pro，价格：12999.0，分类：电子产品

        # 6. 分页查询订单
        print("\n=== 分页查询订单 ===")
        order_pagination = get_order_list(
            db,
            page=1,
            page_size=10,
            user_id=test_user.id
        )
        print(f"总订单数：{order_pagination.total}") # 输出: 1
        for order in order_pagination.items:
            print(f"  - 订单编号：{order.order_no}，状态：{order.status}，金额：{order.total_amount}")
            # 输出:
            # - 订单编号：202603221724427528，状态：pending，金额：24997.0

        # 7. 更新订单状态为已支付
        if order_pagination.items:
            updated_order = update_order_status(
                db,
                order_id=order_pagination.items[0].id,
                status="paid",
                payment_time=datetime.datetime.now(datetime.UTC)
            )
            print(f"\n更新订单状态成功：{updated_order.order_no} -> {updated_order.status}") # 输出: 202603221724427528 -> paid

    except SQLAlchemyError as e:
        db.rollback()
        print(f"数据库错误：{e}")
    except ValueError as e:
        print(f"业务错误：{e}")
    finally:
        db.close()
        print("\n数据库会话已关闭")


if __name__ == "__main__":
    # 创建表
    create_tables()

    # 运行测试
    main()

