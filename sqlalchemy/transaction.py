from sqlalchemy import select, Integer, String, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column

from sync_session import get_db

# ====================== 基础配置 ======================
class Base(DeclarativeBase):
    __abstract__ = True

# ====================== User 模型优化 ======================
class User(Base):
    __tablename__ = "users"

    # 2.0+ 新写法：Mapped + mapped_column（类型提示更精准）
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, comment="邮箱")
    age: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="年龄")
    balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="余额")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', age={self.age}, balance={self.balance})>"


# ====================== 通用工具函数（提升复用性） ======================
def get_db_session() -> Session:
    """获取数据库会话（封装 get_db，简化调用）"""
    try:
        return next(get_db())
    except StopIteration:
        raise RuntimeError("无法获取数据库会话")


# ====================== 核心：转账事务（2.0+ 优化版） ======================
def transfer_money(
        db: Session,
        from_username: str,
        to_username: str,
        amount: int
) -> Optional[tuple[bool, str]]:  # tuple[bool, str]:
    """
    安全的转账事务操作（2.0+ 规范）
    :param db: 数据库会话
    :param from_username: 转出用户名
    :param to_username: 转入用户名
    :param amount: 转账金额（正数）
    :return: (是否成功, 提示信息)
    """
    # 前置校验：金额合法性
    if amount <= 0:
        return False, "转账金额必须大于0"

    # 模拟异常
    if amount == 100:
        raise Exception("模拟异常")

    try:
        # 1. 2.0+ 推荐使用 select 构造器（替代旧 query()）
        stmt_a = select(User).where(User.username == from_username)
        stmt_b = select(User).where(User.username == to_username)

        # 2. 悲观锁：锁定行，避免并发修改（关键！防止超卖/余额不一致）
        # for update：2.0+ 兼容，锁定查询到的行直到事务结束
        user_a: Optional[User] = db.scalars(stmt_a.with_for_update()).first()
        user_b: Optional[User] = db.scalars(stmt_b.with_for_update()).first()

        # 3. 业务校验：用户存在性 + 余额充足性
        if not user_a:
            return False, f"转出用户 {from_username} 不存在"
        if not user_b:
            return False, f"转入用户 {to_username} 不存在"
        if user_a.balance < amount:
            return False, f"用户 {from_username} 余额不足（当前：{user_a.balance}，需转出：{amount}）"

        # 4. 原子性更新操作
        user_a.balance -= amount
        user_b.balance += amount

        # 5. 可选：批量更新（替代对象修改，性能更高）
        # 适用于高并发场景，直接执行UPDATE语句，减少ORM对象操作
        # stmt_update_a = update(User).where(User.username == from_username).values(balance=User.balance - amount)
        # stmt_update_b = update(User).where(User.username == to_username).values(balance=User.balance + amount)
        # db.execute(stmt_update_a)
        # db.execute(stmt_update_b)

        # 6. 提交事务（2.0+ 同步提交，无需await）
        db.commit()

        # 7. 刷新对象，获取最新数据（可选）
        db.refresh(user_a)
        db.refresh(user_b)

        return True, (
            f"转账成功！\n"
            f"{from_username} 余额：{user_a.balance}（原：{user_a.balance + amount}）\n"
            f"{to_username} 余额：{user_b.balance}（原：{user_b.balance - amount}）"
        )

    except SQLAlchemyError as e:
        # 2.0+ 专用异常捕获：仅捕获数据库相关异常，避免捕获所有异常
        db.rollback()
        return False, f"转账失败（数据库异常）：{str(e)}"
    except Exception as e:
        # 其他业务异常
        db.rollback()
        return False, f"转账失败（业务异常）：{str(e)}"
    finally:
        # 可选：关闭会话（若会话是函数内创建，否则由调用方管理）
        # db.close()
        pass

# ====================== 执行入口 ======================
if __name__ == "__main__":
    """执行原生SQL操作"""
    db: Session = get_db_session()  # 获取会话（封装为可复用函数）

    # 测试1：正常转账
    success, msg = transfer_money(db, "zhangsan", "lisi", 10)
    print("\n测试1 - 正常转账：", success, msg)
    # 输出:
    # 测试1 - 正常转账： True 转账成功！
    # zhangsan 余额：90（原：100）
    # lisi ：110（原：100）

    # 测试2：余额不足（触发回滚）
    success, msg = transfer_money(db, "zhangsan", "lisi", 1000)
    print("\n测试2 - 余额不足：", success, msg)
    # 输出: 测试2 - 余额不足： False 用户 zhangsan 余额不足（当前：90，需转出：1000）

    # 测试3：用户不存在（触发回滚）
    success, msg = transfer_money(db, "alice", "lisi", 10)
    print("\n测试3 - 用户不存在：", success, msg)
    # 输出: 测试3 - 用户不存在： False 转出用户 alice 不存在

    # 测试4：手动触发异常（模拟业务报错）
    # 可取消注释测试：在transfer_money中添加 raise Exception("模拟异常")
    # success, msg = transfer_money(db, "zhangsan", "lisi", 100)
    # print("\n测试4 - 手动异常：", success, msg)

'''
事务特性（ACID）：

原子性（Atomicity）：操作不可分割；
一致性（Consistency）：数据状态一致；
隔离性（Isolation）：多个事务互不干扰；
持久性（Durability）：提交后数据永久保存。
'''

