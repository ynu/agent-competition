"""
站内消息 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageResponse, UnreadCountResponse
from app.schemas.common import PageResponse

router = APIRouter(prefix="/messages", tags=["站内消息"])


@router.get("", response_model=PageResponse)
async def get_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_read: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的消息列表"""
    query = db.query(Message).filter(Message.receiver_id == current_user.id)

    if is_read is not None:
        query = query.filter(Message.is_read == is_read)

    total = query.count()
    messages = query.order_by(Message.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 构建响应，包含发送者信息
    result = []
    for msg in messages:
        msg_dict = {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "title": msg.title,
            "content": msg.content,
            "is_read": msg.is_read,
            "created_at": msg.created_at,
            "sender_username": msg.sender.username if msg.sender else None,
            "sender_nickname": msg.sender.nickname if msg.sender else None,
            "receiver_username": msg.receiver.username if msg.receiver else None,
            "receiver_nickname": msg.receiver.nickname if msg.receiver else None,
        }
        result.append(MessageResponse(**msg_dict))

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=result
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取未读消息数量"""
    count = db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).count()
    return UnreadCountResponse(unread_count=count)


@router.get("/receivers", response_model=List[dict])
async def get_receiver_options(
    role: Optional[str] = Query(None, description="按角色筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取可选的接收者列表（管理员可选择所有用户，普通用户只能查看）"""
    if current_user.role == UserRole.ADMIN:
        query = db.query(User).filter(User.is_active == True)
        if role:
            query = query.filter(User.role == role)
        users = query.all()
        return [
            {"id": u.id, "username": u.username, "nickname": u.nickname or u.username, "role": u.role.value if hasattr(u.role, 'value') else u.role}
            for u in users
        ]
    return []


@router.post("", response_model=List[MessageResponse])
async def create_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """发送消息（管理员可发送）"""
    # 只有管理员可以发送消息
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="只有管理员可以发送站内消息")

    # 验证接收者存在
    for receiver_id in message_data.receiver_ids:
        receiver = db.query(User).filter(User.id == receiver_id).first()
        if not receiver:
            raise HTTPException(status_code=404, detail=f"用户 ID {receiver_id} 不存在")

    # 创建消息
    messages = []
    for receiver_id in message_data.receiver_ids:
        message = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            title=message_data.title,
            content=message_data.content
        )
        db.add(message)
        messages.append(message)

    db.commit()

    # 刷新并构建响应
    result = []
    for msg in messages:
        db.refresh(msg)
        msg_dict = {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "title": msg.title,
            "content": msg.content,
            "is_read": msg.is_read,
            "created_at": msg.created_at,
            "sender_username": msg.sender.username if msg.sender else None,
            "sender_nickname": msg.sender.nickname if msg.sender else None,
            "receiver_username": msg.receiver.username if msg.receiver else None,
            "receiver_nickname": msg.receiver.nickname if msg.receiver else None,
        }
        result.append(MessageResponse(**msg_dict))

    return result


@router.put("/{message_id}/read", response_model=MessageResponse)
async def mark_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """标记消息为已读"""
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.receiver_id == current_user.id
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")

    message.is_read = True
    db.commit()
    db.refresh(message)

    return MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        title=message.title,
        content=message.content,
        is_read=message.is_read,
        created_at=message.created_at,
        sender_username=message.sender.username if message.sender else None,
        sender_nickname=message.sender.nickname if message.sender else None,
        receiver_username=message.receiver.username if message.receiver else None,
        receiver_nickname=message.receiver.nickname if message.receiver else None,
    )


@router.put("/read-all")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """标记所有消息为已读"""
    db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "所有消息已标记为已读"}


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取消息详情"""
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.receiver_id == current_user.id
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")

    # 自动标记为已读
    if not message.is_read:
        message.is_read = True
        db.commit()

    return MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        title=message.title,
        content=message.content,
        is_read=message.is_read,
        created_at=message.created_at,
        sender_username=message.sender.username if message.sender else None,
        sender_nickname=message.sender.nickname if message.sender else None,
        receiver_username=message.receiver.username if message.receiver else None,
        receiver_nickname=message.receiver.nickname if message.receiver else None,
    )