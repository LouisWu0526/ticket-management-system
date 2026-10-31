"""ORM 模型与工单状态机定义。"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# 角色
ROLE_USER = "user"
ROLE_ADMIN = "admin"

# 工单状态
STATUS_PENDING = "pending"      # 待处理
STATUS_PROCESSING = "processing"  # 处理中
STATUS_COMPLETED = "completed"   # 已完成

TICKET_STATUSES = (STATUS_PENDING, STATUS_PROCESSING, STATUS_COMPLETED)

# 允许的状态流转：只能单向向前
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    STATUS_PENDING: {STATUS_PROCESSING, STATUS_COMPLETED},
    STATUS_PROCESSING: {STATUS_COMPLETED},
    STATUS_COMPLETED: set(),
}


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default=ROLE_USER, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="user")


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=STATUS_PENDING, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="tickets")
    replies: Mapped[list["TicketReply"]] = relationship(
        back_populates="ticket", order_by="TicketReply.created_at"
    )

    @property
    def author_name(self) -> str | None:
        return self.user.username if self.user else None


class TicketReply(Base):
    __tablename__ = "ticket_replies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ticket: Mapped["Ticket"] = relationship(back_populates="replies")
    user: Mapped["User"] = relationship()

    @property
    def author_name(self) -> str | None:
        return self.user.username if self.user else None

    @property
    def author_role(self) -> str | None:
        return self.user.role if self.user else None


class OperationLog(Base):
    """工单操作日志（创建 / 状态变更 / 回复）。"""
    __tablename__ = "operation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    detail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship()

    @property
    def operator_name(self) -> str | None:
        return self.user.username if self.user else None
