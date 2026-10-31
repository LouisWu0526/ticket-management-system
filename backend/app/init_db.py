"""建表与默认管理员初始化。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, SessionLocal
from .models import ROLE_ADMIN, User
from .security import hash_password


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        exists = db.scalar(select(User).limit(1))
        if exists is None:
            admin = User(
                username=settings.FIRST_ADMIN_USERNAME,
                password_hash=hash_password(settings.FIRST_ADMIN_PASSWORD),
                role=ROLE_ADMIN,
            )
            db.add(admin)
            db.commit()
            print(f"[init] 已创建默认管理员: {settings.FIRST_ADMIN_USERNAME} / {settings.FIRST_ADMIN_PASSWORD}")
    finally:
        db.close()
