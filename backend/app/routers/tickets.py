"""工单接口：提交、列表（分页/筛选/权限）、详情、回复、状态流转、操作日志。"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..models import (
    ALLOWED_TRANSITIONS,
    TICKET_STATUSES,
    OperationLog,
    Ticket,
    TicketReply,
    User,
)
from ..schemas import (
    LogOut,
    PageResult,
    ReplyCreate,
    ReplyOut,
    StatusUpdate,
    TicketCreate,
    TicketDetailOut,
    TicketOut,
)

router = APIRouter(prefix="/tickets", tags=["工单"])


def _get_visible_ticket(ticket_id: int, db: Session, user: User) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工单不存在")
    # 普通用户只能看自己的工单，管理员可以看全部
    if user.role != "admin" and ticket.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看该工单")
    return ticket


def _write_log(db: Session, ticket_id: int, user: User, action: str, detail: str | None = None) -> None:
    db.add(OperationLog(ticket_id=ticket_id, user_id=user.id, action=action, detail=detail))


@router.get("", response_model=PageResult)
def list_tickets(
    status_filter: str | None = Query(default=None, alias="status"),
    keyword: str | None = Query(default=None, max_length=50),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """工单列表：管理员看全部，普通用户只看自己的；支持状态筛选、标题模糊搜索与分页。"""
    if status_filter is not None and status_filter not in TICKET_STATUSES:
        raise HTTPException(status_code=400, detail="非法的状态值")

    stmt = select(Ticket)
    count_stmt = select(func.count()).select_from(Ticket)

    if current_user.role != "admin":
        stmt = stmt.where(Ticket.user_id == current_user.id)
        count_stmt = count_stmt.where(Ticket.user_id == current_user.id)
    if status_filter:
        stmt = stmt.where(Ticket.status == status_filter)
        count_stmt = count_stmt.where(Ticket.status == status_filter)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(Ticket.title.like(like))
        count_stmt = count_stmt.where(Ticket.title.like(like))

    total = db.scalar(count_stmt)
    items = (
        db.scalars(
            stmt.order_by(Ticket.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .all()
    )
    return PageResult(
        total=total or 0,
        page=page,
        page_size=page_size,
        items=[TicketOut.model_validate(t) for t in items],
    )


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = Ticket(
        title=payload.title.strip(),
        description=payload.description.strip(),
        image_url=payload.image_url,
        user_id=current_user.id,
    )
    db.add(ticket)
    db.flush()
    _write_log(db, ticket.id, current_user, "create", "提交工单")
    db.commit()
    db.refresh(ticket)
    return TicketOut.model_validate(ticket)


@router.get("/{ticket_id}", response_model=TicketDetailOut)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = (
        db.scalar(
            select(Ticket)
            .where(Ticket.id == ticket_id)
            .options(selectinload(Ticket.replies), selectinload(Ticket.user))
        )
    )
    if ticket is None:
        raise HTTPException(status_code=404, detail="工单不存在")
    if current_user.role != "admin" and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看该工单")

    logs = db.scalars(
        select(OperationLog).where(OperationLog.ticket_id == ticket_id).order_by(OperationLog.id)
    ).all()

    detail = TicketDetailOut.model_validate(ticket)
    detail.logs = [LogOut.model_validate(log) for log in logs]
    return detail


@router.post("/{ticket_id}/replies", response_model=ReplyOut, status_code=status.HTTP_201_CREATED)
def reply_ticket(
    ticket_id: int,
    payload: ReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """回复工单：管理员可回复任意工单，普通用户可回复自己的工单（补充信息）。"""
    ticket = _get_visible_ticket(ticket_id, db, current_user)

    reply = TicketReply(
        ticket_id=ticket.id,
        user_id=current_user.id,
        content=payload.content.strip(),
    )
    db.add(reply)
    _write_log(db, ticket.id, current_user, "reply", "回复工单")
    db.commit()
    db.refresh(reply)
    return ReplyOut.model_validate(reply)


@router.patch("/{ticket_id}/status", response_model=TicketOut)
def update_status(
    ticket_id: int,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """管理员变更工单状态，服务端强制校验状态机（只能 待处理→处理中→已完成 向前流转）。"""
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="工单不存在")

    new_status = payload.status
    if new_status not in TICKET_STATUSES:
        raise HTTPException(status_code=400, detail="非法的状态值")
    if new_status == ticket.status:
        raise HTTPException(status_code=400, detail=f"工单已处于该状态：{new_status}")
    if new_status not in ALLOWED_TRANSITIONS[ticket.status]:
        raise HTTPException(
            status_code=400,
            detail=f"不允许的状态流转：{ticket.status} → {new_status}（状态只能向前流转）",
        )

    old_status = ticket.status
    ticket.status = new_status
    _write_log(db, ticket.id, admin, "status_change", f"{old_status} → {new_status}")
    db.commit()
    db.refresh(ticket)
    return TicketOut.model_validate(ticket)


@router.get("/{ticket_id}/logs", response_model=list[LogOut])
def list_logs(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_visible_ticket(ticket_id, db, current_user)
    logs = db.scalars(
        select(OperationLog).where(OperationLog.ticket_id == ticket_id).order_by(OperationLog.id)
    ).all()
    return [LogOut.model_validate(log) for log in logs]
