# ====================== 5.1 加载策略优化（解决N+1查询） ======================
def optimize_loading_strategy(db: Session):
    """2.0+ 加载策略优化（joinedload/selectinload）"""
    print("=== 5.1 加载策略优化 ===")
    
    # 问题：N+1查询（2.0+ 仍存在，需显式优化）
    print("\n【N+1查询示例】")
    users: List[User] = db.scalars(select(User)).all()
    for user in users[:2]:  # 仅演示前2个用户
        # 访问articles时触发新查询（N+1问题）
        print(f"用户 {user.username} 的文章数：{len(user.articles)}")

    # 优化1：joinedload（左连接，一次性加载，适合一对一/一对多）
    print("\n【joinedload优化（左连接）】")
    stmt = select(User).options(joinedload(User.articles))
    users = db.scalars(stmt).all()
    for user in users[:2]:
        # 无额外查询，直接访问关联数据
        print(f"用户 {user.username} 的文章：{[art.title for art in user.articles[:1]]}")

    # 优化2：selectinload（IN查询，适合多对多/大数据量一对多）
    print("\n【selectinload优化（IN查询）】")
    stmt = select(User).options(selectinload(User.roles))
    users = db.scalars(stmt).all()
    for user in users[:2]:
        print(f"用户 {user.username} 的角色：{[role.name for role in user.roles]}")

    # 扩展：2.0+ 高级加载策略
    # 1. lazyload：强制延迟加载（覆盖模型默认）
    stmt = select(User).options(lazyload(User.articles))
    # 2. contains_eager：配合手动JOIN，复用已有连接
    stmt = select(User).join(User.articles).options(contains_eager(User.articles))

# ====================== 5.2 只查询指定字段 ======================
def optimize_selected_fields(db: Session):
    """字段筛选优化（减少数据传输）"""
    
    # 基础写法：只查询指定字段（返回元组）
    print("\n【基础字段筛选】")
    stmt = select(User.username, User.email)
    result: Result = db.execute(stmt)
    user_fields: List[Tuple[str, str]] = result.all()
    for username, email in user_fields[:3]:
        print(f"用户名：{username}，邮箱：{email}")

    # 进阶：映射为字典（更易用）
    print("\n【字段筛选+映射字典】")
    stmt = select(
        User.username.label("name"),
        User.age.label("user_age")
    ).where(User.age > 18)
    result = db.execute(stmt)
    # 转为字典列表（2.0+ Result对象支持mappings()）
    user_dicts = [dict(row) for row in result.mappings()]
    for user in user_dicts[:3]:
        print(f"姓名：{user['name']}，年龄：{user['user_age']}")

    # 性能优化：count查询仅查主键（避免count(*)）
    print("\n【count优化】")
    total = db.scalar(select(func.count(User.id)))  # 比count(*)更快
    print(f"总用户数：{total}")

# ====================== 5.3.使用索引 ======================
# User模型
class User(Base):
    __tablename__ = "users"
    
    # 基础字段 + 单字段索引
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="用户名（索引）"
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True, comment="邮箱（唯一索引）"
    )
    age: Mapped[int] = mapped_column(Integer, default=0, comment="年龄")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    balance: Mapped[int] = mapped_column(Integer, default=0, comment="余额")

    # 关联关系（默认lazy="select"，即延迟加载）
    articles: Mapped[List[Article]] = relationship("Article", back_populates="author")
    roles: Mapped[List[Role]] = relationship("Role", secondary=user_role, back_populates="users")

    # 2.0+ 复合索引（生产级优化：覆盖高频查询条件）
    __table_args__ = (
        # 复合索引：age + is_active（匹配 WHERE age > ? AND is_active = ?）
        Index("idx_age_active", "age", "is_active"),
        # 唯一索引（避免重复）
        Index("idx_username_unique", "username", unique=True),
        # 部分索引（仅对激活用户生效，SQLite不支持，MySQL/PG支持）
        # Index("idx_active_email", "email", postgresql_where=(is_active == True)),
    )
    
# ====================== 5.3 索引优化（2.0+ 规范） ======================
def index_optimization_demo():
    """索引优化说明（模型定义规范）"""
    print("\n=== 5.3 索引优化 ===")
    print("✅ 单字段索引：username/email/index=True（高频查询字段）")
    print("✅ 复合索引：idx_age_active（匹配多字段查询条件）")
    print("✅ 唯一索引：username/email（避免重复数据）")
    print("✅ 部分索引：仅对激活用户生效（MySQL/PG支持，SQLite不支持）")
    print("❌ 避免过度索引：更新频繁的字段（如balance）不建索引")
   
# ====================== 5.4 批量操作（2.0+ 性能优化） ======================
def batch_operations_optimization(db: Session):
    """批量操作优化（减少数据库交互）"""
    
    # 1. 批量插入
    print("\n【批量插入】")
    batch_users = [
        User(username=f"user{i}", email=f"user{i}@example.com", age=18+i)
        for i in range(1, 4)
    ]
    db.add_all(batch_users)
    db.commit()
    print(f"批量插入 {len(batch_users)} 个用户完成")

    # 2. 批量更新
    print("\n【批量更新】")
    stmt = update(User).where(User.age < 20).values(is_active=False)
    result = db.execute(stmt)
    db.commit()
    print(f"批量更新 {result.rowcount} 条记录（年龄<20的用户设为非激活）")

    # 3. 批量删除
    print("\n【批量删除】")
    stmt = delete(User).where(User.is_active == False)
    result = db.execute(stmt)
    db.commit()
    print(f"批量删除 {result.rowcount} 条记录（非激活用户）")

    # 批量插入优化（executemany_mode）
    # 适用于MySQL，转为 VALUES (...), (...) 格式
    # db.execute(
    #     insert(User),
    #     [{"username": "u1", "email": "u1@com"}, ...],
    #     execution_options={"executemany_mode": "values"}
    # )
