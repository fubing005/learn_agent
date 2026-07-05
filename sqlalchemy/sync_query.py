from typing import Tuple

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    or_, and_, not_, func, select, distinct, Sequence
)
from sqlalchemy.orm import Session, DeclarativeBase

from sync_crud import get_db_session
from sync_session import sync_engine


# ====================== 基础模型定义（2.0+ 规范） ======================
class Base(DeclarativeBase):
    __abstract__ = True


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=True, index=True, comment="邮箱")
    age = Column(Integer, default=0, nullable=False, comment="年龄")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="是否激活")
    create_time = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="文章ID")
    title = Column(String(100), nullable=False, comment="文章标题")
    content = Column(String(500), comment="文章内容")
    user_id = Column(Integer, nullable=False, index=True, comment="关联用户ID")
    create_time = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title='{self.title}', user_id={self.user_id})>"


# ====================== 1.1 初始化表和测试数据 ======================
def init_data():
    """初始化测试数据（仅首次执行）"""
    db: Session = get_db_session()
    try:
        # 创建表
        print("正在创建数据库表...")
        Base.metadata.create_all(bind=sync_engine)
        print("表创建完成")

        # 清空旧数据（避免重复）
        print("正在清空旧数据...")
        db.query(User).delete()
        db.query(Article).delete()
        db.commit()
        print("旧数据已清空")

        # 新增用户
        print("正在新增用户...")
        users = [
            User(username="zhangsan", email="zhangsan@example.com", age=20),
            User(username="lisi", email="lisi@example.com", age=22),
            User(username="wangwu", email="wangwu@example.com", age=25),
            User(username="zhaoliu", email=None, age=30)  # type: ignore[arg-type]
        ]
        db.add_all(users)
        db.commit()
        print(f"用户新增完成，共 {len(users)} 个用户")

        # 新增文章
        print("正在新增文章...")
        articles = [
            Article(title="Python 入门", content="SQLAlchemy 学习", user_id=1),
            Article(title="SQLAlchemy 进阶", content="关联查询", user_id=1),
            Article(title="MySQL 优化", content="索引使用", user_id=2)
        ]
        db.add_all(articles)
        db.commit()
        print(f"文章新增完成，共 {len(articles)} 篇文章")

        print("\n=== 测试数据初始化完成 ===\n")
    except Exception as e:
        db.rollback()
        error_msg = f"初始化数据失败：{str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        raise RuntimeError(error_msg) from e
    finally:
        db.close()

# ====================== 1.2 筛选查询（2.0+ 优化版） ======================
def filter_query():
    """筛选查询（2.0+ select 构造器）"""
    db: Session = get_db_session()
    try:
        # 1. 或条件（or_）
        stmt = select(User).where(or_(User.age == 20, User.username == "lisi"))
        users: Sequence[User] = db.scalars(stmt).all()
        print("或条件（or_）: ", users)  # 输出: [<User(id=1, username='zhangsan', email='zhangsan@example.com')>, <User(id=2, username='lisi', email='lisi@example.com')>]

        # 2. 与条件（and_）
        stmt = select(User).where(and_(User.age > 20, User.is_active == True))
        users = db.scalars(stmt).all()
        print("与条件（and_）: ", users)  # 输出: [<User(id=2, username='lisi', email='lisi@example.com')>, <User(id=3, username='wangwu', email='wangwu@example.com')>, <User(id=4, username='zhaoliu', email='None')>]

        # 3. 非条件（not_）
        stmt = select(User).where(not_(User.age == 20))
        users = db.scalars(stmt).all()
        print("非条件（not_）: ", users)  # 输出: [<User(id=2, username='lisi', email='lisi@example.com')>, <User(id=3, username='wangwu', email='wangwu@example.com')>, <User(id=4, username='zhaoliu', email='None')>]

        # 4. 模糊查询（like）
        # 以zhang开头
        stmt = select(User).where(User.username.like("zhang%"))
        users = db.scalars(stmt).all()
        print("模糊查询（以zhang开头）: ", users)  # 输出: [<User(id=1, username='zhangsan', email='zhangsan@example.com')>]
        # 包含si
        stmt = select(User).where(User.username.like("%si%"))
        users = db.scalars(stmt).all()
        print("模糊查询（包含si）: ", users)  # 输出: [<User(id=2, username='lisi', email='lisi@example.com')>]

        # 5. 范围查询（in_）
        stmt = select(User).where(User.age.in_([20, 21, 22]))
        users = db.scalars(stmt).all()
        print("范围查询（in_）: ", users)  # 输出: [<User(id=1, username='zhangsan', email='zhangsan@example.com')>, <User(id=2, username='lisi', email='lisi@example.com')>]

        # 6. 空值查询
        # 邮箱为空
        stmt = select(User).where(User.email.is_(None))
        users = db.scalars(stmt).all()
        print("空值查询（is_）: ", users)  # 输出: [<User(id=4, username='zhaoliu', email='None')>]
        # 邮箱不为空
        stmt = select(User).where(User.email.isnot(None))
        users = db.scalars(stmt).all()
        print("空值查询（isnot）: ", users)  # 输出: [<User(id=1, username='zhangsan', email='zhangsan@example.com')>, <User(id=2, username='lisi', email='lisi@example.com')>, <User(id=3, username='wangwu', email='wangwu@example.com')>]
    finally:
        db.close()

# ====================== 1.3 聚合查询（2.0+ 优化版） ======================
def aggregate_query():
    """聚合查询（2.0+ func 优化）"""
    db: Session = get_db_session()
    try:
        # 1. 计数（推荐用 scalar() 获取单个值）
        stmt = select(func.count(User.id))
        total_users: int = db.scalar(stmt)
        print("总用户数：", total_users)  # 输出: 4

        # 2. 求和
        stmt = select(func.sum(User.age))
        total_age: int = db.scalar(stmt)
        print("年龄总和：", total_age)  # 输出: 97

        # 3. 平均值（转换为浮点数，避免精度丢失）
        stmt = select(func.avg(User.age))
        avg_age_value = db.scalar(stmt)
        avg_age: float = float(avg_age_value) if avg_age_value is not None else 0.0
        # 保留 2 位小数
        print("平均年龄：", round(avg_age, 2))  # 输出: 24.25

        # 4. 最大值/最小值
        stmt_max = select(func.max(User.age))
        max_age: int = db.scalar(stmt_max)
        stmt_min = select(func.min(User.age))
        min_age: int = db.scalar(stmt_min)
        print("最大年龄：", max_age, "最小年龄：", min_age)  # 输出: 最大年龄： 30 最小年龄： 20

        # 5. 分组聚合（按激活状态分组）
        stmt = select(User.is_active, func.count(User.id)).group_by(User.is_active)
        result: Sequence[Tuple[bool, int]] = db.execute(stmt).all()
        print("按激活状态分组：", result)  # 输出: [(True, 4)]
    finally:
        db.close()

# ====================== 1.4 关联查询（2.0+ 优化版） ======================
def join_query():
    """关联查询（2.0+ join/outerjoin 规范写法）"""
    db: Session = get_db_session()
    try:
        # 1. 内连接（INNER JOIN）：查询用户及其文章
        # 生成的SQL：SELECT users.id, users.username, users.email, users.age, users.is_active, users.create_time, articles.id AS id_1, articles.title, articles.content, articles.user_id, articles.create_time AS create_time_1
        # FROM users JOIN articles ON users.id = articles.user_id
        stmt = select(User, Article).join(Article, User.id == Article.user_id)
        result: Sequence[Tuple[User, Article]] = db.execute(stmt).all()
        print("\n内连接结果：")
        for user, article in result:  # type: ignore[misc]
            print(f"用户：{user.username}，文章：{article.title}")
            # 输出:
            # 用户：zhangsan，文章：Python 入门
            # 用户：zhangsan，文章：SQLAlchemy 进阶
            # 用户：lisi，文章：MySQL 优化

        # 2. 左连接（LEFT JOIN）：查询所有用户（包括无文章的）
        # 生成的SQL：SELECT users.id, users.username, users.email, users.age, users.is_active, users.create_time, articles.id AS id_1, articles.title, articles.content, articles.user_id, articles.create_time AS create_time_1
        # FROM users LEFT OUTER JOIN articles ON users.id = articles.user_id
        stmt = select(User, Article).outerjoin(Article, User.id == Article.user_id)
        result = db.execute(stmt).all()
        print("\n左连接结果：")
        for user, article in result:  # type: ignore[misc]
            print(f"用户：{user.username}，文章：{article.title if article else '无'}")
            # 输出:
            # 用户：zhangsan，文章：Python 入门
            # 用户：zhangsan，文章：SQLAlchemy 进阶
            # 用户：lisi，文章：MySQL 优化
            # 用户：wangwu，文章：无
            # 用户：zhaoliu，文章：无

    finally:
        db.close()

# ====================== 1.5 子查询（2.0+ 优化版） ======================
def sub_query():
    """子查询（2.0+ scalar_subquery/subquery 规范）"""
    db: Session = get_db_session()
    try:
        # 示例1：查询有文章的用户
        # 子查询：所有发布过文章的用户ID（去重）
        subquery = select(distinct(Article.user_id)).scalar_subquery()
        # 主查询
        stmt = select(User).where(User.id.in_(subquery))
        users = db.scalars(stmt).all()
        print("\n发布过文章的用户：", users)  # 输出: [<User(id=1, username='zhangsan', email='zhangsan@example.com')>, <User(id=2, username='lisi', email='lisi@example.com')>]

        # 示例2：查询年龄大于平均年龄的用户
        # 子查询：平均年龄
        subquery = select(func.avg(User.age)).scalar_subquery()
        # 主查询
        stmt = select(User).where(User.age > subquery)
        users = db.scalars(stmt).all()
        print("年龄大于平均年龄的用户：", users)  # 输出: [<User(id=3, username='wangwu', email='wangwu@example.com')>, <User(id=4, username='zhaoliu', email='None')>]

        # 示例3：查询发布过2篇以上文章的用户
        # 子查询：统计用户文章数（>2）
        subquery = (
            select(Article.user_id, func.count(Article.id).label("article_count"))
            .group_by(Article.user_id)
            .having(func.count(Article.id) > 2)
            .subquery()
        )
        # 主查询：关联子查询
        stmt = select(User).join(subquery, User.id == subquery.c.user_id)
        users = db.scalars(stmt).all()
        print("发布过2篇以上文章的用户：", users)  # 输出: []
    finally:
        db.close()

# ====================== 1.6 分页查询（2.0+ 优化版） ======================
def pagination_query():
    """分页查询（2.0+ 规范写法，带总页数计算）"""
    db: Session = get_db_session()
    try:
        # 分页参数
        page = 1  # 当前页
        page_size = 2  # 每页条数
        offset = (page - 1) * page_size

        # 1. 分页查询数据
        stmt = select(User).offset(offset).limit(page_size).order_by(User.id)
        users: Sequence[User] = db.scalars(stmt).all()
        print(f"\n第{page}页用户：", users)  # 输出: 第1页用户： [<User(id=1, username='zhangsan', email='zhangsan@example.com')>, <User(id=2, username='lisi', email='lisi@example.com')>]

        # 2. 计算总条数和总页数（优化：一次查询获取总条数）
        total_count_stmt = select(func.count(User.id))
        total_users: int = db.scalar(total_count_stmt)
        total_pages = (total_users + page_size - 1) // page_size  # 向上取整
        print(f"总用户数：{total_users}，总页数：{total_pages}")  # 输出: 总用户数：4，总页数：2

        # 扩展：分页通用函数
        def paginate_query(query_stmt, page_num: int, page_size_num: int):  # type: ignore[no-untyped-def]
            """通用分页函数"""
            offset_num = (page_num - 1) * page_size_num
            # 查询数据
            query_data = db.scalars(query_stmt.offset(offset_num).limit(page_size_num)).all()
            # 查询总条数
            query_total = db.scalar(select(func.count()).select_from(query_stmt.subquery()))
            query_total_pages = (query_total + page_size_num - 1) // page_size_num if query_total else 0
            return query_data, query_total or 0, query_total_pages

        # 测试通用分页函数
        data, total, pages = paginate_query(select(User), page_num=2, page_size_num=2)
        print(f"第 2 页用户：{data}，总条数：{total}，总页数：{pages}")  # 输出: 第 2 页用户：[<User(id=3, username='wangwu', email='wangwu@example.com')>, <User(id=4, username='zhaoliu', email='None')>]，总条数：4，总页数：2
    finally:
        db.close()


# ====================== 执行所有测试 ======================
if __name__ == "__main__":
    # 初始化测试数据（仅首次执行）
    init_data()
    # 执行筛选查询
    filter_query()
    # 执行聚合查询
    aggregate_query()
    # 执行关联查询
    join_query()
    # 执行子查询
    sub_query()
    # 执行分页查询
    pagination_query()

