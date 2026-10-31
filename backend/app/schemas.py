"""Pydantic 请求/响应模型。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- 认证 ----------
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20, description="用户名")
    password: str = Field(min_length=6, max_length=32, description="密码")


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- 工单 ----------
class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1000)
    image_url: str | None = Field(default=None, max_length=255)


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    image_url: str | None
    status: str
    user_id: int
    author_name: str | None
    created_at: datetime
    updated_at: datetime


class PageResult(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TicketOut]


class ReplyCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class ReplyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    author_name: str | None
    author_role: str | None
    created_at: datetime


class StatusUpdate(BaseModel):
    status: str


class LogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    detail: str | None
    operator_name: str | None
    created_at: datetime


class TicketDetailOut(TicketOut):
    replies: list[ReplyOut] = Field(default=[])
    logs: list[LogOut] = Field(default=[])


class UploadResponse(BaseModel):
    url: str
    filename: str
