'''
https://blog.csdn.net/inuex/article/details/159353395
'''

'''
1.什么是 SQLAlchemy？
SQLAlchemy 是 Python  的 SQL 工具包和对象关系映射器，是 Python 中最流行的 ORM（对象关系映射）工具，它为应用程序开发人员提供了 SQL 的全部功能和灵活性。它提供了一整套众所周知的企业级持久化模式，旨在实现高效且高性能的数据库访问，并已将其改编为简洁且符合 Python 风格的领域语言。

官方主站： https://www.sqlalchemy.org/

官方文档： https://docs.sqlalchemy.org/en/stable/

官网下载页：https://www.sqlalchemy.org/download.html

GitHub 源码库：https://github.com/sqlalchemy/sqlalchemy（可提 Issue、看源码、贡献代码）

官方 Discourse 论坛：https://discuss.sqlalchemy.org/（提问、交流问题的官方社区）

2.核心优势
异步非阻塞：适配 FastAPI、Starlette 等异步 Web 框架，提升高并发场景性能；
API 统一：异步 API 与同步 API 逻辑一致，学习成本低；
跨数据库兼容：支持 SQLite、MySQL、PostgreSQL、Oracle 等主流数据库，切换数据库只需修改连接字符串。
灵活易用：既支持高层的 ORM 操作，也支持底层的原生 SQL 执行。
强大的查询能力：提供丰富的查询 API，支持复杂的筛选、聚合、关联查询。
事务支持：完善的事务管理机制，保证数据操作的原子性。
3.核心组件
Engine：数据库连接引擎，负责管理数据库连接池。
Session：数据库会话，用于执行 CRUD 操作。
Declarative Base：模型基类，所有数据模型都继承该类。
Mapper：将 Python 类映射到数据库表。
Query：查询对象，用于构建数据库查询。
'''

'''
4.相关单词
单词	                音标	                                    中文释义	                核心使用场景
SQLAlchemy	            /ˌeskjuːˈel ˈælkəmi/	                    SQL 炼金术（ORM 框架名）	框架整体引用、技术栈说明
Session	                /ˈseʃn/	                                    会话	                    数据库连接会话管理（2.0 核心对象）
Model	                /ˈmɒdl/（英）/ˈmɑːdl/（美）	                模型	                    定义数据库表映射的类
Engine	                /ˈendʒɪn/	                                引擎	                    数据库连接引擎创建
Query	                /ˈkwɪəri/（英）/ˈkwɪri/（美）	            查询	                    构建数据库查询语句
Column	                /ˈkɒləm/（英）/ˈkɑːləm/（美）	            列	                        定义数据库表字段
Table	                /ˈteɪbl/	                                表	                        数据库表对象 / 映射
Relationship	        /rɪˈleɪʃnʃɪp/	                            关系	                    定义表之间的关联（一对多 / 多对多）
ForeignKey	            /ˈfɒrən kiː/（英                            外键	                    建立表之间的引用关系
DeclarativeBase	        /dɪˈklærətɪv beɪs/	                        声明式基类	                2.0 模型继承的核心基类
Mapped	                /mæpt/	                                    映射	                    2.0 字段类型注解（Mapped []）
mapped_column	        /mæpt ˈkɒləm/（英）/mæpt ˈkɑːləm/（美）	     映射列	                    2.0 定义字段的核心函数
Select	                /sɪˈlekt/	                                选择	                    2.0 构建查询的核心语句（select ()）
Commit	                /kəˈmɪt/	                                提交	                    事务提交操作
Rollback	            /ˈrəʊlbæk/（英）/ˈroʊlbæk/（美）             回滚	                    事务异常时回滚操作
Filter	                /ˈfɪltə/（英）/ˈfɪltər/（美）	            过滤	                    查询时添加条件过滤
Join	                /dʒɔɪn/	                                    连接	                    多表关联查询（join/joinedload）
Pagination	            /ˌpædʒɪˈneɪʃn/	                            分页	                    数据分页查询处理
Transaction	            /trænˈzækʃn/	                            事务	                    数据库事务管理
Metadata	            /ˈmetədeɪtə/	                            元数据	                    数据库表结构的元数据对象
Cascade	                /kæˈskeɪd/	                                级联	                    定义关联数据的级联操作（如删除）
Scalar	                /ˈskeɪlə/	                                标量	                    查询单个结果（scalar ()/scalars ()）
Sessionmaker	        /ˈseʃn ˌmeɪkə/（英）/ˈseʃn ˌmeɪkər/（美）	会话工厂	                创建 Session 的工厂函数
AsyncSession	        /eɪˈsɪŋk ˈseʃn/	                            异步会话	                2.0 异步操作的会话对象
Index	                /ˈɪndeks/	                                索引	                    为表字段创建索引
Unique	                /juˈniːk/	                                唯一	                    定义唯一约束（UniqueConstraint）
'''

'''
二、环境准备
1.安装 SQLAlchemy
# 安装核心库
pip install sqlalchemy

# 查看已安装的 sqlalchemy 包的详细信息
pip show sqlalchemy
'''

'''
2.安装数据库驱动
不同数据库需要安装对应的驱动，以下是主流数据库的驱动安装命令：

数据库	            同步驱动安装命令	                            异步驱动安装命令
SQLite	            无需安装（Python 内置）	                        无需安装
MySQL/MariaDB	    pip install pymysql 或 mysql-connector-python	pip install asyncmy
PostgreSQL	        pip install psycopg2-binary	                    pip install asyncpg
Oracle	            pip install cx-Oracle	                        无官方异步驱动（可使用同步 + 线程）
'''

'''
3.连接字符串格式
连接字符串是 Engine 的核心参数，格式为：数据库类型+驱动://用户名:密码@主机:端口/数据库名?参数

数据库	    同步连接字符串示例	                                            异步连接字符串示例
SQLite	    sqlite:///test.db（相对路径）sqlite:////绝对路径/test.db	    sqlite+aiosqlite:///test.db
MySQL	    mysql+pymysql://root:123456@localhost:3306/test	               mysql+asyncmy://root:123456@localhost:3306/test
PostgreSQL	postgresql+psycopg2://postgres:123456@localhost:5432/test	   postgresql+asyncpg://postgres:123456@localhost:5432/test
Oracle	    oracle+cx_oracle://scott:tiger@127.0.0.1:1521/orcl
'''


# 3.3.同步 vs 异步核心差异
'''
3.3.1.核心语法差异（最直观）
维度	    同步操作	                    异步操作	                                    关键说明
函数定义	def func():	                    async def func():	                           所有异步操作函数必须标记 async
操作执行	直接调用（如 db.commit()）	    需加 await（如 await db.commit()）	             所有数据库 IO 操作必须用 await 挂起
入口执行	直接调用 func()	                asyncio.run(func())	                            异步代码必须在事件循环中执行
会话获取	next(get_db())	                await get_async_db_session()	                异步生成器需 await + 循环获取
'''

'''
3.3.2.核心 API 差异（2.0+ 重点）
同步 API（旧 / 2.0 兼容）	异步 API（2.0+ 推荐）	            适用场景
Session	                    AsyncSession	                会话对象类型
db.get(User, 1)	            await db.get(User, 1)	        按主键查询
db.scalars(stmt).all()	    (await db.scalars(stmt)).all()	通用查询
db.execute(stmt)	        await db.execute(stmt)	        执行 update/delete 语句
db.commit()	                await db.commit()	            提交事务
db.rollback()	            await db.rollback()	            回滚事务
db.delete(user)	            await db.delete(user)	        删除单个对象
db.close()	                await db.close()	            关闭会话
'''

'''
3.3.3.底层依赖 / 配置差异
配置项	            同步版本	        异步版本
引擎创建	        create_engine()	    create_async_engine()
会话工厂	        sessionmaker()	    async_sessionmaker()
SQLite 驱动	        内置 sqlite3	    需安装 aiosqlite（pip install aiosqlite）
MySQL/PG 驱动	    pymysql/psycopg2	asyncmy/psycopg[async]
连接池	            QueuePool	        AsyncAdaptedQueuePool
'''

'''
3.3.4.执行逻辑差异
特性	            同步执行	                    异步执行
阻塞方式	        线程阻塞（等待数据库响应）	    协程挂起（不阻塞线程，可处理其他任务）
并发能力	        受线程数限制（GIL 影响）	    高并发（单线程可处理上千协程）
异常处理	        try-except                      直接捕获	try-except 捕获 + await 内执行
事务控制	        同步 flush/commit/rollback	    异步 flush/commit/rollback（均需 await）
'''


'''
2.3.核心知识点解析（深入理解 SQLAlchemy）

2.3.1.复杂关系映射
一对多：Category -> Product、User -> Order，通过 ForeignKey + relationship 实现
多对多（隐式）：Order <-> Product 通过中间表 OrderItem 实现（更灵活的多对多，可存储额外字段如购买数量、单价）
级联操作：cascade="all, delete-orphan" 实现删除主表数据时自动删除关联子表数据

2.3.2.高级查询技巧
条件构建：使用 and_()、or_() 组合多条件，支持动态条件拼接
关联加载优化：
joinedload()：左连接加载关联数据（适合一对一 / 一对多）
selectinload()：IN 查询加载关联数据（适合多对多 / 一对多）
load_only()：只加载需要的字段，减少数据传输
行锁：with_for_update() 实现悲观锁，防止超卖（电商核心场景）

2.3.3.分页功能进阶
通用分页结构：封装 Pagination 类，包含总数、页码、是否有下一页 / 上一页等信息
条件分页：分页查询支持多条件过滤（价格区间、分类、关键词）+ 自定义排序
参数校验：限制页大小范围，防止恶意请求（如 page_size=10000）

2.3.4.事务管理
完整事务：创建订单时包含「库存检查 → 扣减库存 → 创建订单 → 提交事务」完整流程
异常回滚：任何步骤出错都通过 db.rollback() 回滚事务，保证数据一致性
并发控制：使用行锁防止超卖，解决电商核心并发问题

2.3.5.数据操作最佳实践
批量操作：add_all() 批量添加数据，减少数据库交互
更新优化：直接更新字段而非查询后修改（如库存扣减）
软删除：is_deleted 字段实现逻辑删除，保留数据记录

2.4.总结
关系建模：电商场景的多对多关系（订单 - 商品）通过中间表实现，比博客系统的简单关系更复杂，能充分理解 SQLAlchemy 的关系映射；
查询优化：关联加载、字段过滤、行锁等技巧，解决实际业务中的性能和并发问题；
分页进阶：支持多条件过滤、自定义排序的分页功能，覆盖实际项目中分页的常见需求；
事务管理：完整的事务流程 + 异常回滚，体现 SQLAlchemy 在数据一致性方面的能力；
业务结合：将 SQLAlchemy 操作与电商核心业务（订单创建、库存管理、订单状态更新）结合，理解 ORM 在实际项目中的应用方式。
'''