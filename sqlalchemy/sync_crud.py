from typing import List, Optional, Sequence

from sqlalchemy import select, update, delete, desc
from sqlalchemy.orm import Session

# 假设 Base、User 模型、get_db 已从优化后的配置文件导入
from models import User
from sync_session import get_db


# ====================== 通用工具函数（提升复用性） ======================
def get_db_session() -> Session:
    """获取数据库会话（封装 get_db，简化调用）"""
    return next(get_db())

# ====================== 3.1.1 新增数据（Create）- 2.0+ 优化 ======================
def create_users():
    """新增数据（单个/批量）- 2.0+ 规范写法"""
    db: Session = get_db_session()
    try:
        # 方式1：创建单个对象（添加类型注解）
        user1: User = User(username="zhangsan", email="zhangsan@example.com", age=20)
        db.add(user1)

        # 方式2：批量创建对象（类型注解 + 列表初始化）
        batch_users: List[User] = [
            User(username="lisi", email="lisi@example.com", age=22),
            User(username="wangwu", email="wangwu@example.com", age=25)
        ]
        db.add_all(batch_users)

        # 提交事务（2.0+ 推荐先 flush 再 commit，确保获取自增ID）
        db.flush()  # 预提交，生成ID但不持久化
        db.commit()  # 最终提交

        # 刷新对象（获取数据库自动生成的字段）
        db.refresh(user1)
        print(f"新增用户ID：{user1.id}")  # 输出：新增用户ID：1
    except Exception as e:
        db.rollback()  # 异常回滚
        raise RuntimeError(f"新增用户失败：{str(e)}") from e
    finally:
        db.close()  # 确保会话关闭

# ====================== 3.1.2 查询数据（Read）- 2.0+ 核心优化 ======================
def query_users():
    """查询数据 - 2.0+ 推荐使用 select() 构造器（替代旧 query API）"""
    db: Session = get_db_session()
    try:
        # 1. 查询所有用户
        stmt = select(User)
        users: Sequence[User] = db.scalars(stmt).all()
        print("所有用户：", users)   # 输出: [<User(id=1, username='zhangsan', email='zhangsan@example.com', is_active=True)>, <User(id=2, username='lisi', email='lisi@example.com', is_active=True)>, <User(id=3, username='wangwu', email='wangwu@example.com', is_active=True)>]

        # 2. 查询单个用户（按主键）
        user: Optional[User] = db.get(User, 1)  # 2.0+ 推荐直接用 session.get()
        print("主键为1的用户：", user)   # 输出: <User(id=1, username='zhangsan', email='zhangsan@example.com', is_active=True)>

        # 3. 条件查询
        # 方式1：filter（2.0+ 推荐，支持复杂条件）
        stmt = select(User).where(User.username == "zhangsan")
        user: Optional[User] = db.scalars(stmt).first()
        print("方式1：用户名是zhangsan的用户：", user)   # 输出: <User(id=1, username='zhangsan', email='zhangsan@example.com', is_active=True)>

        # 方式2：简易条件（2.0+ 无 filter_by，用 where 简化）
        stmt = select(User).where(User.username == "zhangsan")
        user: Optional[User] = db.scalars(stmt).first()
        print("方式2：用户名是zhangsan的用户：", user)   # 输出: <User(id=1, username='zhangsan', email='zhangsan@example.com', is_active=True)>

        # 4. 多条件查询
        stmt = select(User).where(User.age > 20, User.is_active == True)
        users: Sequence[User] = db.scalars(stmt).all()
        print("年龄>20且激活的用户：", users)   # 输出: [<User(id=2, username='lisi', email='lisi@example.com', is_active=True)>, <User(id=3, username='wangwu', email='wangwu@example.com', is_active=True)>]

        # 5. 排序查询（2.0+ 用 desc()/asc() 函数）
        stmt = select(User).order_by(desc(User.age))
        users: Sequence[User] = db.scalars(stmt).all()
        print("按年龄降序的用户：", users)   # 输出: [<User(id=3, username='wangwu', email='wangwu@example.com', is_active=True)>, <User(id=2, username='lisi', email='lisi@example.com', is_active=True)>, <User(id=1, username='zhangsan', email='zhangsan@example.com', is_active=True)>]

        # 6. 限制查询结果数量（2.0+ 用 limit() 方法）
        stmt = select(User).limit(2)
        users: Sequence[User] = db.scalars(stmt).all()
        print("前2个用户：", users)   # 输出: [<User(id=1, username='zhangsan', email='zhangsan@example.com', is_active=True)>, <User(id=2, username='lisi', email='lisi@example.com', is_active=True)>]
    finally:
        db.close()

# ====================== 3.1.3 修改数据（Update）- 2.0+ 优化 ======================
def update_users():
    """修改数据（单个/批量）- 2.0+ 规范写法"""
    db: Session = get_db_session()
    try:
        # 1. 修改单个对象（查询-修改-提交）
        stmt = select(User).where(User.username == "zhangsan")
        user: Optional[User] = db.scalars(stmt).first()
        if user:
            # 修改属性
            user.age = 21
            user.email = "zhangsan_new@example.com"
            db.commit()  # 提交修改
            db.refresh(user)  # 刷新对象获取最新数据
            print("修改后的用户：", user)  # 输出: <User(id=1, username='zhangsan', email='zhangsan_new@example.com', is_active=True)>

        # 2. 批量修改（2.0+ 新 API：update() 构造器）
        stmt = (
            update(User)
            .where(User.age < 25)
            .values(is_active=False)  # 2.0+ 用 values() 指定修改字段
            .execution_options(synchronize_session="fetch")  # 同步会话数据
        )
        result = db.execute(stmt)
        db.commit()
        # 输出: 批量修改完成，影响行数：2
        print(f"批量修改完成，影响行数：{result.rowcount}")  # type: ignore[attr-defined]
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"修改用户失败：{str(e)}") from e
    finally:
        db.close()

# ====================== 3.1.4 删除数据（Delete）- 2.0+ 优化 ======================
def delete_users():
    """删除数据（单个/批量）- 2.0+ 规范写法"""
    db: Session = get_db_session()
    try:
        # 1. 删除单个对象
        stmt = select(User).where(User.username == "wangwu")
        user: Optional[User] = db.scalars(stmt).first()
        if user:
            db.delete(user)
            db.commit()
            print("删除用户完成")

        # 2. 批量删除（2.0+ 新 API：delete() 构造器）
        stmt = (
            delete(User)
            .where(User.is_active == True)
            .execution_options(synchronize_session="fetch")
        )
        result = db.execute(stmt)
        db.commit()
        # 输出: 批量删除完成，影响行数：2
        print(f"批量删除完成，影响行数：{result.rowcount}")  # type: ignore[attr-defined]
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"删除用户失败：{str(e)}") from e
    finally:
        db.close()


# ====================== 调用示例 ======================
if __name__ == "__main__":
    # 执行新增
    # create_users()
    # 执行查询
    # query_users()
    # 执行修改
    # update_users()
    # 执行删除
    delete_users()
