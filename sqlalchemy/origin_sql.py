from sqlite3 import Row
from typing import List, Tuple, Optional, Sequence

from sqlalchemy import Integer, String, text
from sqlalchemy.engine import Result  # 2.0+ 结果类型注解
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column

# 定义数据库引擎/会话
from sync_crud import get_db_session
from sync_session import sync_engine


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


# ====================== 工具函数：初始化表和测试数据 ======================
def init_tables():
    """初始化关系表（删除旧表+创建新表）"""
    db: Session = get_db_session()
    try:
        # 先删除旧表（按依赖顺序）
        Base.metadata.drop_all(bind=sync_engine)
        # 创建新表
        Base.metadata.create_all(bind=sync_engine)
        print("关系表初始化完成")
    finally:
        db.close()


# ====================== 核心：原生SQL操作（2.0+ 优化版） ======================
def execute_sql() -> None:
    """执行原生SQL操作"""
    db: Session = get_db_session()  # 获取会话（封装为可复用函数）
    try:
        # 1. 单条插入数据（获取插入后的自增ID）
        single_insert_sql = text("""
                    INSERT INTO users (username, email, age, balance) 
                    VALUES (:username, :email, :age, :balance)
                """)
        single_insert_data = {"username": "wushi", "email": "wushi@example.com", "age": 30, "balance": 100}
        # MySQL 下获取自增ID（不同数据库语法不同）
        if sync_engine.dialect.name == "mysql":
            db.execute(single_insert_sql, single_insert_data)
            last_id = db.execute(text("SELECT LAST_INSERT_ID()")).scalar()
            db.commit()
            print(f"单条插入完成，自增ID：{last_id}")

        # 2. 批量插入数据（2.0+ 优化：executemany 模式，性能更高）
        batch_insert_sql = text("""
            INSERT INTO users (username, email, age, balance) 
            VALUES (:username, :email, :age, :balance)
        """)
        batch_data: List[dict] = [
            {"username": "zhangsan", "email": "zhangsan@example.com", "age": 20, "balance": 100},
            {"username": "lisi", "email": "lisi@example.com", "age": 22, "balance": 100},
            {"username": "wangwu", "email": "wangwu@example.com", "age": 25, "balance": 100}
        ]
        # 2.0+ 推荐使用 executemany_mode="values" 优化批量插入
        result: Result = db.execute(
            batch_insert_sql,
            batch_data,
            execution_options={"executemany_mode": "values"}  # 批量插入优化
        )
        db.commit()
        # 批量创建数据完成，影响行数：3
        print(f"批量创建数据完成，影响行数：{result.rowcount}")  # type: ignore[attr-defined]

        # 3. 执行查询
        query_sql = text("SELECT username, age FROM users WHERE age > :age")
        query_result: Result = db.execute(query_sql, {"age": 20})
        all_results: Sequence[Row] = query_result.fetchall()
        print("原生 SQL 查询结果：", all_results)  # 输出: [('lisi', 22), ('wangwu', 25)]

        # 4. 执行单条查询（返回单个元组，2.0+ 空值处理优化）
        single_sql = text("SELECT username FROM users WHERE id = :id")
        single_result: Optional[Tuple[str]] = db.execute(single_sql, {"id": 1}).fetchone()
        if single_result:
            print("单个结果：", single_result[0])  # 输出: zhangsan
        else:
            print("未找到 ID 为 1 的用户")

        # 5. 执行更新操作
        update_sql = text("UPDATE users SET age = :age WHERE username = :username")
        update_result: Result = db.execute(update_sql, {"age": 23, "username": "zhangsan"})
        db.commit()
        # 使用rowcount属性
        update_row_count = update_result.rowcount  # type: ignore[attr-defined]
        print(f"原生 SQL 修改完成，影响行数：{update_row_count}")  # 输出: 1

    except Exception as e:
        db.rollback()  # 异常回滚，保证数据一致性
        raise RuntimeError(f"原生SQL操作失败：{str(e)}") from e  # 保留异常栈
    finally:
        db.close()  # 确保会话关闭（2.0+ 同步会话必须显式关闭）


# ====================== 执行入口 ======================
if __name__ == "__main__":
    # 1. 初始化表
    init_tables()
    # 2. 执行原生SQL操作
    execute_sql()

