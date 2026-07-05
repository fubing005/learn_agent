from typing import List, Optional

from sqlalchemy import (
    Column, Integer, String, ForeignKey, Boolean, Table, func, DateTime
)
from sqlalchemy.orm import (
    Session, DeclarativeBase, relationship, Mapped, mapped_column
)

# 假设从优化后的配置导入会话和引擎
from sync_crud import get_db_session
from sync_session import sync_engine


# ====================== 基础基类（2.0+ 规范） ======================
class Base(DeclarativeBase):
    """所有模型的基类（2.0+ 推荐 DeclarativeBase）"""
    __abstract__ = True

    # 通用字段：创建/更新时间（所有表复用）
    create_time = mapped_column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    update_time = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")


# ====================== 2.2 一对多（用户 - 文章） ======================
# 推荐：先定义被关联模型（Article），避免循环引用；或使用字符串引用
class Article(Base):
    __tablename__ = "articles"

    # 2.0+ 推荐使用 mapped_column 替代旧 Column 写法（类型注解更友好）
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True, comment="文章ID")
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="文章标题")
    content: Mapped[Optional[str]] = mapped_column(String(500), comment="文章内容")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), comment="关联用户ID")

    # 多对一关联：多个文章属于一个用户
    author: Mapped["User"] = relationship(
        "User",
        back_populates="articles",
        lazy="selectin"  # 2.0+ 推荐的加载策略，避免N+1查询
    )

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title='{self.title}', user_id={self.user_id})>"


# ====================== 2.4 多对多（用户 - 角色） ======================
# 中间表（2.0+ 规范写法）
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, comment="用户ID"),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, comment="角色ID"),
    # 新增中间表通用字段（可选）
    Column("create_time", DateTime, default=func.now(), nullable=False, comment="关联创建时间")
)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True, comment="角色ID")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色名称")

    # 多对多关联：一个角色对应多个用户
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_role,  # 指定中间表
        back_populates="roles",
        cascade="all",
        lazy="selectin"
    )


class User(Base):
    __tablename__ = "users"

    # 2.0+ 新写法：Mapped + mapped_column（类型提示更精准）
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, comment="邮箱")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")

    # 一对多关联：一个用户有多个文章
    articles: Mapped[List["Article"]] = relationship(
        "Article",
        back_populates="author",
        cascade="all, delete-orphan",  # 级联删除：删用户时删文章，删文章自动解除关联
        passive_deletes=True,  # 配合外键 ondelete="CASCADE"，提升删除性能
        lazy="selectin"  # 预加载关联数据，避免N+1查询
    )

    # 一对一关联：uselist=False 表示非列表（一对一）
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )

    # 多对多关联：一个用户对应多个角色
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=user_role,
        back_populates="users",
        cascade="all",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


# ====================== 2.3 一对一（用户 - 用户详情） ======================
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="详情ID")
    address: Mapped[Optional[str]] = mapped_column(String(200), comment="地址")
    phone: Mapped[Optional[str]] = mapped_column(String(20), comment="手机号")
    # 唯一外键：保证一对一关系
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        comment="关联用户ID"
    )

    # 一对一关联：一个详情属于一个用户
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
        lazy="selectin"
    )


# ====================== 2.1 工具函数：初始化表和测试数据 ======================
def init_relationship_tables():
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

# ====================== 2.2 一对多使用示例 ======================
def one_to_many():
    """测试一对多关系（修复PyCharm报错+规范写法）"""
    db: Session = get_db_session()
    try:
        # 1. 新增用户+文章（修复PyCharm参数报错：使用类型注解+分步创建）
        # 方式1：推荐写法（分步创建，无IDE报错）
        new_user = User(username="tianqi", email="tianqi@example.com")
        # 创建文章并关联作者（推荐）
        article1 = Article(title="SQLAlchemy关系映射", content="一对多示例", author=new_user)
        article2 = Article(title="PythonORM", content="ORM入门", author=new_user)
        db.add_all([new_user, article1, article2])
        db.flush()  # 预提交，生成ID
        db.commit()
        print("新增用户+文章完成")

        # 2. 查询用户的所有文章（2.0+ select 构造器）
        from sqlalchemy import select
        stmt = select(User).where(User.username == "tianqi")
        user = db.scalars(stmt).first()
        if user:
            print(f"\n{user.username}的文章：", [art.title for art in user.articles])   # 输出: tianqi的文章： ['SQLAlchemy关系映射', 'PythonORM']

        # 3. 查询文章的作者
        stmt = select(Article).where(Article.title == "SQLAlchemy关系映射")
        article = db.scalars(stmt).first()
        if article:
            print(f"{article.title}的作者：", article.author.username)  # 输出: SQLAlchemy关系映射的作者： tianqi

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"一对多测试失败：{str(e)}") from e
    finally:
        db.close()

'''
参数说明：
back_populates：反向关联（对应另一张表的关系字段）；
cascade="all, delete-orphan"：级联操作（删除用户时自动删除其文章）；
ForeignKey("users.id")：外键约束（关联用户表的 id 字段）。
'''

# ====================== 2.3 一对一使用示例） ======================
def one_to_one():
    """测试一对一关系"""
    db: Session = get_db_session()
    try:
        # 1. 查询用户
        from sqlalchemy import select
        stmt = select(User).where(User.username == "tianqi")
        user = db.scalars(stmt).first()
        if user:
            # 2. 新增/更新用户详情
            if user.profile:
                db.delete(user.profile)
                db.flush()

            user.profile = UserProfile(address="北京市海淀区", phone="13800138000")
            db.commit()
            # 输出: tianqi的地址： 北京市海淀区
            print(f"\n{user.username}的地址：", user.profile.address)  # type: ignore
            # 输出: tianqi的手机号： 13800138000
            print(f"{user.username}的手机号：", user.profile.phone)  # type: ignore

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"一对一测试失败：{str(e)}") from e
    finally:
        db.close()

# ====================== 2.4 多对多使用示例（优化版） ======================
def many_to_many():
    """测试多对多关系"""
    db: Session = get_db_session()
    try:
        # 1. 新增角色
        admin_role = Role(name="admin")
        guest_role = Role(name="guest")
        db.add_all([admin_role, guest_role])
        db.commit()

        # 2. 给用户分配角色
        from sqlalchemy import select
        stmt = select(User).where(User.username == "tianqi")
        user = db.scalars(stmt).first()
        if user:
            user.roles.append(admin_role)
            user.roles.append(guest_role)
            db.commit()

            # 3. 查询用户的角色
            print(f"\n{user.username}的角色：", [role.name for role in user.roles]) # 输出: tianqi的角色： ['admin', 'guest']

            # 4. 查询角色下的用户
            stmt = select(Role).where(Role.name == "admin")
            role = db.scalars(stmt).first()
            if role:
                print(f"{role.name}角色下的用户：", [u.username for u in role.users])  # 输出: admin角色下的用户： ['tianqi']

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"多对多测试失败：{str(e)}") from e
    finally:
        db.close()


# ====================== 执行所有测试 ======================
if __name__ == "__main__":
    # 1. 初始化表
    init_relationship_tables()
    # 2. 测试一对多
    one_to_many()
    # 3. 测试一对一
    one_to_one()
    # 4. 测试多对多
    many_to_many()

