import asyncio
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine  # 显式导入类型
)
from sqlalchemy.orm import DeclarativeBase  # 2.0+ 推荐的基类
from sqlalchemy.pool import AsyncAdaptedQueuePool  # 异步连接池

# ====================== 1. 配置项抽离（提升可维护性） ======================
# 数据库连接配置（统一管理，方便环境切换）
DATABASE_URL = "sqlite+aiosqlite:///async_test.db"
# 调试开关（建议通过环境变量控制，如 os.getenv("DEBUG", "False") == "True"）
DEBUG_MODE = True

# ====================== 2. 异步引擎优化（核心性能+兼容性） ======================
async_engine: AsyncEngine = create_async_engine(
    url=DATABASE_URL,
    # 基础配置
    echo=DEBUG_MODE,  # 生产环境关闭，调试时开启
    echo_pool=False,  # 关闭连接池日志（减少IO开销）
    # 异步连接池配置（2.0+ 推荐 AsyncAdaptedQueuePool）
    poolclass=AsyncAdaptedQueuePool,
    pool_size=5,  # 核心连接数（SQLite 无实际连接，适配其他数据库）
    max_overflow=10,  # 最大溢出连接数
    pool_recycle=3600,  # 1小时回收连接，避免失效（适配MySQL/PostgreSQL）
    pool_pre_ping=True,  # 获取连接前检测有效性，防止死连接
    # SQLite 专属异步优化参数
    connect_args={
        "check_same_thread": False,  # 解决SQLite线程安全问题
        "timeout": 30,  # 数据库锁定超时时间（默认5秒，提升稳定性）
    },
)

# ====================== 3. 异步会话工厂优化（2.0+ 规范） ======================
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,  # 显式指定异步会话类（2.0+ 规范）
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # 提交后不失效对象（异步场景减少重复查询）
)


# ====================== 4. 模型基类优化（2.0+ 官方推荐） ======================
# 替代旧的 declarative_base()，2.0+ 推荐直接继承 DeclarativeBase
class Base(DeclarativeBase):
    """所有异步模型的基类（2.0+ 规范写法）"""
    __abstract__ = True  # 标记为抽象类，不生成数据库表


# ====================== 5. 异步会话获取函数（核心优化，解决原逻辑问题） ======================
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话生成器（适配 FastAPI 依赖注入）
    优化点：
    1. 移除 async with 与手动 close() 的冲突
    2. 取消自动提交（避免业务逻辑未完成时误提交）
    3. 完善异常处理和类型注解
    4. 确保会话最终关闭，防止连接泄漏
    """
    session: Optional[AsyncSession] = None
    try:
        session = AsyncSessionLocal()  # 手动创建会话，替代 async with
        yield session  # 传递会话给业务逻辑
    except Exception as e:
        # 异常时回滚所有未提交的操作
        if session:
            await session.rollback()
        raise e  # 重新抛出异常，让上层框架（如FastAPI）处理
    finally:
        # 确保会话最终关闭，释放连接
        if session:
            await session.close()


# ====================== 6. 可选：创建数据库表的异步函数（通用工具） ======================
async def create_all_tables() -> None:
    """异步创建所有模型对应的数据库表（初始化用）"""
    async with async_engine.begin() as conn:
        # 异步执行表创建（2.0+ 推荐使用 engine.begin()）
        await conn.run_sync(Base.metadata.create_all)


# 测试示例（可选）
async def main():
    # 初始化数据库表
    # await create_all_tables()
    # 使用会话
    async for db in get_async_db():
        # 业务逻辑示例
        print(f"会话状态：{db.is_active}")  # 输出: 会话状态：True


if __name__ == "__main__":
    asyncio.run(main())

