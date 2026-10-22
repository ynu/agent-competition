"""
数据库连接管理模块
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
from app.core.config import settings, get_db_type


class Base(DeclarativeBase):
    """SQLAlchemy 基础类"""
    pass


def get_engine():
    """创建数据库引擎"""
    db_type = get_db_type()
    url = settings.DATABASE_URL

    if db_type == "sqlite":
        # SQLite 特殊配置
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False  # Always disable to prevent logging Chinese characters
        )
        # 启用外键约束
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    else:
        engine = create_engine(url, pool_pre_ping=True, echo=False)  # Always disable

    return engine


def get_session_factory():
    """获取会话工厂"""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 全局会话工厂
SessionLocal = get_session_factory()


def get_db():
    """获取数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_columns(engine):
    """为已有表补充新增列（create_all 不会给已存在的表加列）"""
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    if 'contents' not in inspector.get_table_names():
        return
    existing = {c['name'] for c in inspector.get_columns('contents')}
    new_columns = {
        'category': 'VARCHAR(100)',
        'tags': 'VARCHAR(500)',
        'external_url': 'VARCHAR(500)',
        'icon': 'VARCHAR(500)',
    }
    with engine.connect() as conn:
        for col, col_type in new_columns.items():
            if col not in existing:
                conn.execute(text(f'ALTER TABLE contents ADD COLUMN {col} {col_type}'))
        conn.commit()


def init_db():
    """初始化数据库表"""
    # Import all models to register them with Base.metadata
    from app.models import user, team, work, content, setting  # noqa
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    # 为已有数据库补充新增列（SQLite 等不支持 create_all 自动加列）
    _ensure_columns(engine)

    # 创建默认管理员账号
    from sqlalchemy.orm import Session
    from app.models.user import User
    from app.core.security import get_password_hash

    db = Session(bind=get_engine())
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                nickname="管理员",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                auth_source="local",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("默认管理员账号已创建: admin / admin123")
    finally:
        db.close()