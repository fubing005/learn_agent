# 导入核心模块（2.0+ 推荐的导入方式）
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.pool import QueuePool  # 连接池配置

# ====================== 1. 数据库引擎优化（核心性能优化） ======================
# 针对 SQLite 和 SQLAlchemy 2.0+ 的引擎配置优化
# 关键优化点：
# - 关闭 echo（生产环境必须关闭，调试时可开启）
# - 配置连接池（SQLite 虽无真正连接池，但配置可兼容其他数据库）
# - 设置 SQLite 专属优化参数（提升读写性能）
sync_engine = create_engine(
    "sqlite:///sync_test.db",
    # 基础配置
    echo=True,  # 生产环境关闭 SQL 打印，提升性能
    echo_pool=False,  # 关闭连接池日志
    # 连接池配置（适配 MySQL/PostgreSQL 等数据库时更重要）
    poolclass=QueuePool,
    pool_size=5,  # 核心连接数
    max_overflow=10,  # 最大溢出连接数
    pool_recycle=3600,  # 1小时回收连接，避免失效
    pool_pre_ping=True,  # 获取连接前检测是否有效，防止死连接
    # SQLite 专属优化参数（2.0+ 推荐）
    connect_args={
        "check_same_thread": False,  # 允许多线程访问（SQLite 必要配置）
        "timeout": 30,  # 数据库锁定超时时间（默认5秒，提升到30秒避免锁死）
    },
)


# ====================== 2. 模型基类优化（2.0+ 规范） ======================
# SQLAlchemy 2.0+ 推荐直接继承 DeclarativeBase（替代旧的 declarative_base()）
class Base(DeclarativeBase):
    """所有数据模型的基类（2.0+ 规范写法）"""
    __abstract__ = True  # 标记为抽象类，不会生成数据库表


# ====================== 3. 会话工厂优化（安全性+规范性） ======================
# 2.0+ 推荐显式指定类型，同时保留核心配置
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    expire_on_commit=False,  # 优化：提交后不自动过期对象，提升查询性能
    class_=Session,  # 显式指定会话类（2.0+ 规范）
)


# ====================== 4. 会话获取函数优化（类型安全+容错性） ======================
def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话生成器（2.0+ 类型安全版本）
    特性：
    - 类型注解明确，支持 IDE 提示
    - 异常捕获并友好提示
    - 确保会话最终关闭
    """
    db_session: Optional[Session] = None  # 初始化变量
    try:
        db_session = SessionLocal()
        yield db_session
    except Exception as e:
        # 可选：记录日志（推荐生产环境添加）
        # import logging; logging.error(f"数据库会话异常: {str(e)}")
        db_session.rollback()  # 异常时回滚未提交的操作
        raise  # 重新抛出异常，让上层处理
    finally:
        if db_session is not None:
            db_session.close()  # 确保会话无论是否异常都关闭


if __name__ == "__main__":
    # 测试示例
    db = next(get_db())
    print(db)  # <sqlalchemy.orm.session.Session object at 0x00000297EFE323C0>

