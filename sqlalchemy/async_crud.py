import asyncio
from typing import List, Optional

from sqlalchemy import select, update, delete, desc, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

# 假设从优化后的异步配置文件导入以下依赖
from models import User


# ====================== 通用工具函数（异步） ======================
async def get_async_db_session() -> AsyncSession:
    """获取异步数据库会话（封装 get_async_db，简化调用）"""
    # 由于 get_async_db 现在是上下文管理器，我们需要一个不同的实现
    # 直接创建会话而不是使用上下文管理器
    from async_session import AsyncSessionLocal

    session = AsyncSessionLocal()
    return session


# ====================== 3.1.1 新增数据（Create）- 异步版 ======================
async def create_users_async():
    """异步新增数据（单个/批量）"""
    db: AsyncSession = await get_async_db_session()
    try:
        # 方式1：创建单个对象
        user1: User = User(username="zhangsan", email="zhangsan@example.com", age=20)
        db.add(user1)

        # 方式2：批量创建对象
        batch_users: List[User] = [
            User(username="lisi", email="lisi@example.com", age=22),
            User(username="wangwu", email="wangwu@example.com", age=25)
        ]
        db.add_all(batch_users)

        # 异步提交（2.0+ 异步必须用 await）
        await db.flush()  # 预提交，生成自增ID
        await db.commit()  # 最终提交

        # 异步刷新对象
        await db.refresh(user1)
        print(f"新增用户ID：{user1.id}")  # 输出：新增用户ID：1
    except Exception as e:
        await db.rollback()  # 异步回滚
        raise RuntimeError(f"异步新增用户失败：{str(e)}") from e
    finally:
        await db.close()  # 异步关闭会话

# ====================== 3.1.2 查询数据（Read）- 异步版 ======================
async def query_users_async():
    """异步查询数据（2.0+ 异步 select 构造器）"""
    db: AsyncSession = await get_async_db_session()
    try:
        # 1. 查询所有用户（异步核心：await + scalars + all）
        stmt = select(User)
        result = await db.scalars(stmt)  # 异步执行查询
        users: Sequence[User] = result.all()
        print("所有用户：",
              users)  # 输出: [<User(id=1, username='zhangsan', email='zhangsan@example.com', is_active=True)>, <User(id=2, username='lisi', email='lisi@example.com', is_active=True)>, <User(id=3, username='wangwu', email='wangwu@example.com', is_active=True)>]

        # 2. 查询单个用户（按主键，异步 get）
        user: Optional[User] = await db.get(User, 1)  # 异步 get 方法
        print("主键为1的用户：",
              user)  # 输出: <User(id=1, username='zhangsan', email='zhangsan@example.com', is_active=True)>

        # 3. 条件查询
        # 方式1：where 条件 + 异步执行
        stmt = select(User).where(User.username == "zhangsan")
        user: Optional[User] = (await db.scalars(stmt)).first()
        print("方式1：用户名是zhangsan的用户：",
              user)  # 输出: <User(id=1, username='zhangsan', email='zhangsan@example.com', is_active=True)>

        # 4. 多条件查询
        stmt = select(User).where(User.age > 20, User.is_active == True)
        users: Sequence[User] = (await db.scalars(stmt)).all()
        print("年龄>20且激活的用户：",
              users)  # 输出: [<User(id=2, username='lisi', email='lisi@example.com', is_active=True)>, <User(id=3, username='wangwu', email='wangwu@example.com', is_active=True)>]

        # 5. 排序查询（2.0+ desc 函数）
        stmt = select(User).order_by(desc(User.age))
        users: Sequence[User] = (await db.scalars(stmt)).all()
        print("按年龄降序的用户：",
              users)  # 输出: [<User(id=3, username='wangwu', email='wangwu@example.com', is_active=True)>, <User(id=2, username='lisi', email='lisi@example.com', is_active=True)>, <User(id=1, username='zhangsan', email='zhangsan@example.com', is_active=True)>]

        # 6. 限制查询结果数量
        stmt = select(User).limit(2)
        users: Sequence[User] = (await db.scalars(stmt)).all()
        print("前2个用户：",
              users)  # 输出: [<User(id=1, username='zhangsan', email='zhangsan@example.com', is_active=True)>, <User(id=2, username='lisi', email='lisi@example.com', is_active=True)>]
    finally:
        await db.close()

# ====================== 3.1.3 修改数据（Update）- 异步版 ======================
async def update_users_async():
    """异步修改数据（单个/批量）"""
    db: AsyncSession = await get_async_db_session()
    try:
        # 1. 修改单个对象（查询-修改-提交）
        stmt = select(User).where(User.username == "zhangsan")
        user: Optional[User] = (await db.scalars(stmt)).first()
        if user:
            user.age = 21
            user.email = "zhangsan_new@example.com"
            await db.commit()  # 异步提交
            await db.refresh(user)  # 异步刷新
            print("修改后的用户：",
                  user)  # 输出: <User(id=1, username='zhangsan', email='zhangsan_new@example.com', is_active=True)>

        # 2. 批量修改（2.0+ 异步 update 构造器）
        stmt = (
            update(User)
            .where(User.age < 25)
            .values(is_active=False)
            .execution_options(synchronize_session="fetch")
        )
        result = await db.execute(stmt)  # 异步执行批量更新
        await db.commit()
        # 输出: 批量修改完成，影响行数：2
        print(f"批量修改完成，影响行数：{result.rowcount}")  # type: ignore[attr-defined]
    except Exception as e:
        await db.rollback()
        raise RuntimeError(f"异步修改用户失败：{str(e)}") from e
    finally:
        await db.close()

# ====================== 3.1.4 删除数据（Delete）- 异步版 ======================
async def delete_users_async():
    """异步删除数据（单个/批量）"""
    db: AsyncSession = await get_async_db_session()
    try:
        # 1. 删除单个对象
        stmt = select(User).where(User.username == "wangwu")
        user: Optional[User] = (await db.scalars(stmt)).first()
        if user:
            await db.delete(user)  # 异步删除
            await db.commit()
            print("删除用户完成")

        # 2. 批量删除（2.0+ 异步 delete 构造器）
        stmt = delete(User).where(User.is_active == False)
        result = await db.execute(stmt)  # 异步执行批量删除
        await db.commit()
        # 输出: 批量删除完成，影响行数：2
        print(f"批量删除完成，影响行数：{result.rowcount}")  # type: ignore[attr-defined]
    except Exception as e:
        await db.rollback()
        raise RuntimeError(f"异步删除用户失败：{str(e)}") from e
    finally:
        await db.close()


# ====================== 异步入口函数（执行所有操作） ======================
async def main():
    """异步主函数：按顺序执行所有 CRUD 操作"""
    # 1. 新增数据
    # await create_users_async()
    # 2. 查询数据
    # await query_users_async()
    # 3. 修改数据
    # await update_users_async()
    # 4. 删除数据
    await delete_users_async()


# ====================== 执行异步代码 ======================
if __name__ == "__main__":
    # 异步代码必须在 asyncio 事件循环中执行
    asyncio.run(main())

