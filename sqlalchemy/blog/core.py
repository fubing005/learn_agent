import datetime
from typing import List, Optional, Generator

# SQLAlchemy 2.0 核心导入
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    text,
    create_engine,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
    Session,
)


# --------------------------- 基础配置 ---------------------------
class Base(DeclarativeBase):
    """所有模型的基类"""
    # 为所有模型添加通用的创建时间字段
    __abstract__ = True  # 抽象基类，不会创建表

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    create_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.UTC), comment="创建时间"
    )

    # # 如果希望直接用 SQL 插入也能自动填充时间，需要改用 server_default（数据库层面默认值）：
    # create_time: Mapped[datetime.datetime] = mapped_column(
    #     DateTime, 
    #     server_default=text("CURRENT_TIMESTAMP"),  # 数据库层面默认值
    #     comment="创建时间"
    # )

# 数据库连接配置
DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(
    DATABASE_URL,
    # check_same_thread=False 是 SQLite 专属配置:
    # 允许同一个数据库连接被多个线程共享使用，适配 SQLAlchemy 连接池的多线程场景；
    # 解除「连接必须和创建它的线程绑定」的限制，避免 ProgrammingError 报错；
    connect_args={
        "check_same_thread": False, # 关闭 SQLite 的线程检查机制
        "uri": True  # 启用URI模式
    },
    # 或使用文件锁保证写安全
    execution_options={"isolation_level": "SERIALIZABLE"},
    echo=True,  # 设为 True 可打印 SQL 语句，便于调试
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # 提交后不立即过期对象
)


# --------------------------- 数据模型 ---------------------------
class Role(Base):
    """角色模型"""
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="角色名称")
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="角色描述")

    # 多对多关联用户
    users: Mapped[List["User"]] = relationship(
        "User", secondary="user_roles", back_populates="roles"
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"

class UserRole(Base):
    """用户-角色 多对多中间表"""
    __tablename__ = "user_roles"
    __table_args__ = {"comment": "用户角色关联表"}  # 表注释

    # 复合主键
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), comment="用户ID" # primary_key=True,
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"), comment="角色ID" # primary_key=True,
    )


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="用户名")
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="邮箱")
    password: Mapped[str] = mapped_column(String(100), comment="密码（建议加密存储）")
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="是否激活"
    )
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="年龄")

    # 关联角色（多对多）
    roles: Mapped[List[Role]] = relationship(
        "Role", secondary="user_roles", back_populates="users"
    )
    # 关联文章（一对多）
    articles: Mapped[List["Article"]] = relationship(
        "Article", back_populates="author", cascade="all, delete-orphan"
    )
    # 关联评论（一对多）
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class Article(Base):
    """文章模型"""
    __tablename__ = "articles"
    __table_args__ = {"comment": "文章表"}

    title: Mapped[str] = mapped_column(String(100), index=True, comment="文章标题")
    content: Mapped[str] = mapped_column(String, comment="文章内容")
    read_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="阅读量"
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), comment="作者ID"
    )

    # 关联作者
    author: Mapped["User"] = relationship(
        "User", back_populates="articles"
    )
    # 关联评论（一对多，删除文章时级联删除评论）
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="article", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title={self.title[:20]}...)>"


class Comment(Base):
    """评论模型"""
    __tablename__ = "comments"
    __table_args__ = {"comment": "评论表"}

    content: Mapped[str] = mapped_column(String(500), comment="评论内容")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), comment="评论用户ID"
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"), comment="关联文章ID"
    )

    # 关联用户
    author: Mapped["User"] = relationship(
        "User", back_populates="comments"
    )
    # 关联文章
    article: Mapped["Article"] = relationship(
        "Article", back_populates="comments"
    )

    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, content={self.content[:20]}...)>"


# --------------------------- 数据库操作工具函数 ---------------------------
def create_tables() -> None:
    """创建所有表"""
    try:
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功！")
    except SQLAlchemyError as ex:
        print(f"创建表失败：{ex}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（依赖注入风格）
    2.0 版本推荐使用 Session 类型提示
    """
    db_session: Session = SessionLocal()
    try:
        yield db_session
    except SQLAlchemyError as ex:
        db_session.rollback()  # 异常时回滚
        print(f"数据库操作异常：{ex}")
        raise
    finally:
        db_session.close()


# --------------------------- 测试代码 ---------------------------
if __name__ == "__main__":
    # 创建所有表
    create_tables()

    # 测试代码
    # try:
    #     # with语句自动管理会话，结束后自动关闭
    #     with SessionLocal() as db:
    #         print("数据库会话创建成功！")
    
    #         admin_role = db.query(Role).filter(Role.name == "admin").first()
    #         if not admin_role:
    #             admin_role = Role(name="admin", description="管理员")
    #             db.add(admin_role)
    #             db.commit()
    #             db.refresh(admin_role)
    #             print(f"添加测试角色成功：{admin_role}")
    #         else:
    #             print(f"admin角色已存在：{admin_role}")
    # except Exception as e:
    #     print(f"测试过程出错：{e}")

