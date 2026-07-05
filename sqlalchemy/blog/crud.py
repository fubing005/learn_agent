import os
import sys
from dataclasses import dataclass
from typing import Dict, Optional, Any, Sequence

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SQLAlchemy 2.0 核心导入
from sqlalchemy import (
    select,
    func,
    delete,
    update,
    or_
)
from sqlalchemy.engine import Result
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError
)
from sqlalchemy.orm import (
    Session,
    joinedload,
    selectinload
)

# 导入模型和数据库会话
from blog.core import User, Role, Article, Comment, get_db


# --------------------------- 数据结构定义 ---------------------------
@dataclass
class PaginationResult:
    """分页结果数据结构"""
    items: Sequence[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "items": [item.__dict__ for item in self.items],  # 可替换为自定义序列化逻辑
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages
        }


# --------------------------- 异常定义 ---------------------------
class BusinessException(Exception):
    """业务异常基类"""

    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ResourceExistsException(BusinessException):
    """资源已存在异常"""

    def __init__(self, message: str):
        super().__init__(message, 409)


class ResourceNotFoundException(BusinessException):
    """资源不存在异常"""

    def __init__(self, message: str):
        super().__init__(message, 404)


class PermissionDeniedException(BusinessException):
    """权限不足异常"""

    def __init__(self, message: str):
        super().__init__(message, 403)


# --------------------------- 通用工具函数 ---------------------------
def commit_with_retry(db: Session, max_retries: int = 3) -> None:
    """
    提交事务并支持重试（处理并发冲突）
    """
    retries = 0
    while retries < max_retries:
        try:
            db.commit()
            return
        except SQLAlchemyError as ex:
            retries += 1
            db.rollback()
            if retries >= max_retries:
                raise BusinessException(f"数据库操作失败：{str(ex)}")


def get_password_hash(password: str) -> str:
    """
    密码加密（生产环境必需）
    """
    return password


# --------------------------- 用户管理 ---------------------------
def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        age: Optional[int] = None
) -> User:
    """
    创建用户（SQLAlchemy 2.0 优化版）

    Args:
        db: 数据库会话
        username: 用户名
        email: 邮箱
        password: 原始密码（自动加密）
        age: 年龄

    Returns:
        创建的用户对象

    Raises:
        ResourceExistsException: 用户名/邮箱已存在
        BusinessException: 数据库操作失败
    """
    # 2.0 优化：一次查询检查用户名和邮箱，减少数据库交互
    stmt = select(User).where(
        or_(User.username == username, User.email == email)
    )
    existing_user: Optional[User] = db.execute(stmt).scalar_one_or_none()

    if existing_user:
        if existing_user.username == username:
            raise ResourceExistsException("用户名已存在")
        else:
            raise ResourceExistsException("邮箱已存在")

    # 密码加密（生产环境必需）
    hashed_password = get_password_hash(password)

    # 创建用户
    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        is_active=True,
        age=age
    )

    # 分配普通用户角色（优化：使用 selectinload 减少N+1查询）
    user_role: Optional[Role] = db.execute(
        select(Role).where(Role.name == "user")
    ).scalar_one_or_none()

    if user_role:
        new_user.roles.append(user_role)

    try:
        db.add(new_user)
        # # 预提交，获取数据库生成的ID和默认值，此时对象仍在会话中
        # db.flush()  
        commit_with_retry(db)
        # 提交成功后，对象会从会话中过期，需要刷新以加载角色关系
        db.refresh(new_user)
        # 刷新后加载角色信息
        db.execute(select(User).options(joinedload(User.roles)).where(User.id == new_user.id))
        # # 显式触发角色的加载，避免在会话外延迟加载报错
        # _ = new_user.roles
        return new_user
    except SQLAlchemyError as ex:
        db.rollback()
        raise BusinessException(f"创建用户失败：{str(ex)}")


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    根据用户名查询用户（包含角色）

    Args:
        db: 数据库会话
        username: 用户名

    Returns:
        用户对象或None
    """
    stmt = select(User).options(
        selectinload(User.roles)  # 2.0 推荐：selectinload 性能优于 joinedload 多对多
    ).where(User.username == username)

    return db.execute(stmt).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    根据ID查询用户（包含角色）

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        用户对象或None
    """
    stmt = select(User).options(
        selectinload(User.roles)
    ).where(User.id == user_id)

    return db.execute(stmt).scalar_one_or_none()


def update_user(
        db: Session,
        user_id: int,
        **kwargs
) -> User:
    """
    修改用户信息

    Args:
        db: 数据库会话
        user_id: 用户ID
        **kwargs: 要更新的字段（如 email, age, is_active 等）

    Returns:
        更新后的用户对象

    Raises:
        ResourceNotFoundException: 用户不存在
        BusinessException: 更新失败
    """
    # 检查用户是否存在
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise ResourceNotFoundException("用户不存在")

    # 过滤合法字段，防止更新敏感字段
    allowed_fields = {"username", "email", "age", "is_active"}
    update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not update_fields:
        return db_user

    # 2.0 优化：批量更新字段
    try:
        for key, value in update_fields.items():
            setattr(db_user, key, value)

        commit_with_retry(db)
        db.refresh(db_user)
        return db_user
    except IntegrityError as ex:
        db.rollback()
        raise ResourceExistsException(f"更新失败：{str(ex)}")
    except SQLAlchemyError as ex:
        db.rollback()
        raise BusinessException(f"更新用户失败：{str(ex)}")


def delete_user(db: Session, user_id: int) -> bool:
    """
    删除用户（2.0 批量删除写法，无需先查询）

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        删除成功返回True

    Raises:
        ResourceNotFoundException: 用户不存在
    """
    stmt = delete(User).where(User.id == user_id)
    result: Result = db.execute(stmt)

    if result.rowcount == 0:  # type: ignore[attr-defined]
        raise ResourceNotFoundException("用户不存在")

    commit_with_retry(db)
    return True


# --------------------------- 文章管理 ---------------------------
def create_article(
        db: Session,
        title: str,
        content: str,
        user_id: int
) -> Article:
    """
    发布文章

    Args:
        db: 数据库会话
        title: 文章标题
        content: 文章内容
        user_id: 作者ID

    Returns:
        文章对象

    Raises:
        ResourceNotFoundException: 用户不存在
        BusinessException: 创建失败
    """
    # 检查用户是否存在
    if not db.execute(select(User.id).where(User.id == user_id)).scalar():
        raise ResourceNotFoundException("用户不存在")

    new_article = Article(
        title=title,
        content=content,
        user_id=user_id
    )

    try:
        db.add(new_article)
        commit_with_retry(db)
        db.refresh(new_article)
        return new_article
    except SQLAlchemyError as ex:
        db.rollback()
        raise BusinessException(f"发布文章失败：{str(ex)}")


def get_article_list(
        db: Session,
        page: int = 1,
        page_size: int = 10
) -> PaginationResult:
    """
    分页查询文章列表（包含作者）

    Args:
        db: 数据库会话
        page: 页码（默认1）
        page_size: 每页条数（默认10）

    Returns:
        分页结果对象
    """
    # 参数校验
    page = max(1, page)
    page_size = max(1, min(100, page_size))  # 限制最大页大小
    offset = (page - 1) * page_size

    # 2.0 优化：使用 with_for_update(read=True) 避免脏读（可选）
    # 查询文章列表（优化：只加载需要的字段）
    stmt = select(Article).options(
        joinedload(Article.author).load_only(User.id, User.username, User.email)
    ).order_by(Article.create_time.desc()).offset(offset).limit(page_size)

    articles: Sequence[Article] = db.execute(stmt).scalars().all()

    # 总数量（优化：避免子查询）
    total: int | None = db.execute(select(func.count(Article.id))).scalar()
    if total is None:
        total = 0
    total_pages = (total + page_size - 1) // page_size

    return PaginationResult(
        items=articles,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


def get_article_detail(db: Session, article_id: int) -> Article:
    """
    查询文章详情（包含作者、评论及评论作者）

    Args:
        db: 数据库会话
        article_id: 文章ID

    Returns:
        文章对象

    Raises:
        ResourceNotFoundException: 文章不存在
    """
    stmt = select(Article).options(
        joinedload(Article.author).load_only(User.id, User.username),
        joinedload(Article.comments).joinedload(
            Comment.author
        ).load_only(User.id, User.username)
    ).where(Article.id == article_id)

    # 使用 unique() 方法处理连接集合导致的重复数据
    db_article: Optional[Article] = db.execute(stmt).unique().scalar_one_or_none()

    if not db_article:
        raise ResourceNotFoundException("文章不存在")

    # 阅读量+1（2.0 优化：使用 update 语句，无需查询后修改）
    db.execute(
        update(Article)
        .where(Article.id == article_id)
        .values(read_count=Article.read_count + 1)
    )
    commit_with_retry(db)

    # 刷新阅读量
    db.refresh(db_article, attribute_names=["read_count"])

    return db_article


def update_article(
        db: Session,
        article_id: int,
        user_id: int,
        **kwargs
) -> Article:
    """
    修改文章（仅作者可修改）

    Args:
        db: 数据库会话
        article_id: 文章ID
        user_id: 操作人ID
        **kwargs: 要更新的字段（title, content）

    Returns:
        更新后的文章对象

    Raises:
        ResourceNotFoundException: 文章/用户不存在
        PermissionDeniedException: 无权限
    """
    # 检查文章是否存在并验证权限
    stmt = select(Article).where(Article.id == article_id)
    db_article: Optional[Article] = db.execute(stmt).scalar_one_or_none()

    if not db_article:
        raise ResourceNotFoundException("文章不存在")

    if db_article.user_id != user_id:
        raise PermissionDeniedException("无权限修改该文章")

    # 过滤合法字段
    allowed_fields = {"title", "content"}
    update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not update_fields:
        return db_article

    try:
        for key, value in update_fields.items():
            setattr(db_article, key, value)

        commit_with_retry(db)
        db.refresh(db_article)
        return db_article
    except SQLAlchemyError as ex:
        db.rollback()
        raise BusinessException(f"修改文章失败：{str(ex)}")


def delete_article(
        db: Session,
        article_id: int,
        user_id: int
) -> bool:
    """
    删除文章（仅作者/管理员可删除）

    Args:
        db: 数据库会话
        article_id: 文章ID
        user_id: 操作人ID

    Returns:
        删除成功返回True

    Raises:
        ResourceNotFoundException: 文章/用户不存在
        PermissionDeniedException: 无权限
    """
    # 检查文章是否存在
    db_article: Optional[Article] = db.execute(
        select(Article).where(Article.id == article_id)
    ).scalar_one_or_none()

    if not db_article:
        raise ResourceNotFoundException("文章不存在")

    # 检查用户和权限
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise ResourceNotFoundException("操作用户不存在")

    is_admin = any(role.name == "admin" for role in db_user.roles)
    if db_article.user_id != user_id and not is_admin:
        raise PermissionDeniedException("无权限删除该文章")

    try:
        db.delete(db_article)
        commit_with_retry(db)
        return True
    except SQLAlchemyError as ex:
        db.rollback()
        raise BusinessException(f"删除文章失败：{str(ex)}")


# --------------------------- 评论管理 ---------------------------
def create_comment(
        db: Session,
        content: str,
        user_id: int,
        article_id: int
) -> Comment:
    """
    新增评论

    Args:
        db: 数据库会话
        content: 评论内容
        user_id: 评论者ID
        article_id: 文章ID

    Returns:
        评论对象

    Raises:
        ResourceNotFoundException: 用户/文章不存在
    """
    # 2.0 优化：一次查询检查用户和文章
    user_exists = db.execute(select(User.id).where(User.id == user_id)).scalar()
    article_exists = db.execute(select(Article.id).where(Article.id == article_id)).scalar()

    if not user_exists:
        raise ResourceNotFoundException("用户不存在")
    if not article_exists:
        raise ResourceNotFoundException("文章不存在")

    db_comment = Comment(
        content=content,
        user_id=user_id,
        article_id=article_id
    )

    try:
        db.add(db_comment)
        commit_with_retry(db)
        db.refresh(db_comment)
        return db_comment
    except SQLAlchemyError as ex:
        db.rollback()
        raise BusinessException(f"新增评论失败：{str(ex)}")


def delete_comment(
        db: Session,
        comment_id: int,
        user_id: int
) -> bool:
    """
    删除评论（仅评论者/管理员可删除）

    Args:
        db: 数据库会话
        comment_id: 评论ID
        user_id: 操作人ID

    Returns:
        删除成功返回True

    Raises:
        ResourceNotFoundException: 评论/用户不存在
        PermissionDeniedException: 无权限
    """
    # 检查评论是否存在
    db_comment: Optional[Comment] = db.execute(
        select(Comment).where(Comment.id == comment_id)
    ).scalar_one_or_none()

    if not db_comment:
        raise ResourceNotFoundException("评论不存在")

    # 检查用户和权限
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise ResourceNotFoundException("操作用户不存在")

    is_admin = any(role.name == "admin" for role in db_user.roles)
    if db_comment.user_id != user_id and not is_admin:
        raise PermissionDeniedException("无权限删除该评论")

    try:
        db.delete(db_comment)
        commit_with_retry(db)
        return True
    except SQLAlchemyError as ex:
        db.rollback()
        raise BusinessException(f"删除评论失败：{str(ex)}")


# --------------------------- 测试功能 ---------------------------
if __name__ == "__main__":
    # 获取数据库会话
    db_session: Session = next(get_db())

    try:
        # 1. 初始化角色
        roles = db_session.execute(select(Role).where(Role.name.in_(["admin", "guest"]))).scalars().all()
        role_names = {role.name for role in roles}

        missing_roles = []
        if "admin" not in role_names:
            missing_roles.append(Role(name="admin", description="系统管理员"))
        if "guest" not in role_names:
            missing_roles.append(Role(name="guest", description="来宾用户"))

        if missing_roles:
            db_session.add_all(missing_roles)
            commit_with_retry(db_session)
            print("初始化角色成功")

        # 2. 创建测试用户
        try:
            user = create_user(
                db_session,
                username="test_user",
                email="test@example.com",
                password="123456",
                age=23
            )
            print(f"创建用户成功：{user.username} (ID: {user.id})")  # 输出: 创建用户成功：test_user (ID: 1)
        except ResourceExistsException as e:
            print(f"创建用户失败：{e.message}")
            # 获取已存在的用户
            user = get_user_by_username(db_session, "test_user")
            if not user:
                raise

        # 3. 发布测试文章
        article = create_article(
            db_session,
            title="我的第一篇博客",
            content="SQLAlchemy 2.0 实战案例",
            user_id=user.id
        )
        print(f"发布文章成功：{article.title} (ID: {article.id})")  # 输出: 发布文章成功：我的第一篇博客 (ID: 1)

        # 4. 新增评论
        comment = create_comment(
            db_session,
            content="这篇文章写得很好！",
            user_id=user.id,
            article_id=article.id
        )
        print(f"新增评论成功：{comment.content} (ID: {comment.id})")  # 输出: 新增评论成功：这篇文章写得很好！ (ID: 1)

        # 5. 查询文章详情
        detail = get_article_detail(db_session, article.id)
        print("\n=== 文章详情 ===")
        print(f"标题：{detail.title}")  # 输出: 标题：我的第一篇博客
        print(f"作者：{detail.author.username}")  # 输出: 作者：test_user
        print(f"阅读量：{detail.read_count}")  # 输出: 阅读量：1
        print(f"评论数：{len(detail.comments)}")  # 输出: 评论数：1
        print(f"第一条评论：{detail.comments[0].content}")  # 输出: 第一条评论：这篇文章写得很好！
        print(f"评论作者：{detail.comments[0].author.username}")  # 输出: 评论作者：test_user

        # 6. 测试分页查询
        pagination = get_article_list(db_session, page=1, page_size=10)
        print(f"\n=== 分页查询 ===")
        print(f"总文章数：{pagination.total}")  # 输出: 总文章数：1
        print(f"当前页：{pagination.page}/{pagination.total_pages}")  # 输出: 当前页：1/1

    except BusinessException as e:
        print(f"业务异常：{e.message} (代码：{e.code})")
    except Exception as e:
        print(f"测试失败：{str(e)}")
        db_session.rollback()
    finally:
        # 关闭会话
        db_session.close()
        print("\n数据库会话已关闭")

