# 注意：Base 需从之前优化后的 DeclarativeBase 子类导入
# 导入 Base 根据同步/异步场景选择
from async_session import Base, async_engine
from sync_session import Base, sync_engine

# 导入数据模型（必须在创建表之前导入，这样 SQLAlchemy 才能知道要创建哪些表）
from models import User


# ====================== 表创建逻辑优化（兼容同步/异步） ======================
# 1. 同步场景创建表（2.0+ 规范写法）
def create_tables_sync(engine) -> None:
    """同步创建所有表（仅初始化时执行）"""
    # checkfirst=True：默认值，先检查表是否存在，避免重复创建
    # Base.metadata.create_all() 方法会自动扫描所有继承自 Base 的类，并将它们对应的表创建出来
    Base.metadata.create_all(bind=engine, checkfirst=True)


# 2. 异步场景创建表（2.0+ 推荐写法）
async def create_tables_async(engine) -> None:
    """异步创建所有表（适配异步引擎）"""
    async with engine.begin() as conn:
        # run_sync 适配异步引擎执行同步的 metadata.create_all
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


# ====================== 调用示例 ======================
# 同步场景
# create_tables_sync(sync_engine)

# # 异步场景（需在异步上下文执行）
import asyncio
asyncio.run(create_tables_async(async_engine))

