"""
事件通知渠道管理 API 路由
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User, UserRole
from app.models.event_channel import EventChannel
from app.schemas.event_channel import (
    EventChannelCreate, EventChannelUpdate, EventChannelResponse,
    EventChannelListResponse, TestChannelResponse, ChannelTypeInfo
)
from src.events import get_channel, get_available_channels


router = APIRouter(prefix="/event-channels", tags=["事件通知渠道"])


@router.get("/types", response_model=List[ChannelTypeInfo])
async def get_channel_types():
    """获取所有可用的渠道类型"""
    channels = get_available_channels()
    return [ChannelTypeInfo(**c) for c in channels]


@router.get("", response_model=EventChannelListResponse)
async def get_event_channels(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    channel_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """获取事件通知渠道列表"""
    query = db.query(EventChannel)

    if keyword:
        query = query.filter(EventChannel.name.contains(keyword))

    if channel_type:
        query = query.filter(EventChannel.channel_type == channel_type)

    if is_active is not None:
        query = query.filter(EventChannel.is_active == is_active)

    total = query.count()
    channels = query.order_by(EventChannel.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = [
        EventChannelResponse(
            id=c.id,
            name=c.name,
            channel_type=c.channel_type,
            config=c.config or {},
            events=c.events or [],
            description=c.description,
            is_active=c.is_active,
            created_at=c.created_at.isoformat() if c.created_at else "",
            updated_at=c.updated_at.isoformat() if c.updated_at else None,
            last_triggered_at=c.last_triggered_at.isoformat() if c.last_triggered_at else None,
            last_trigger_status=c.last_trigger_status,
            last_error=c.last_error
        )
        for c in channels
    ]

    return EventChannelListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{channel_id}", response_model=EventChannelResponse)
async def get_event_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """获取单个渠道详情"""
    channel = db.query(EventChannel).filter(EventChannel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")

    return EventChannelResponse(
        id=channel.id,
        name=channel.name,
        channel_type=channel.channel_type,
        config=channel.config or {},
        events=channel.events or [],
        description=channel.description,
        is_active=channel.is_active,
        created_at=channel.created_at.isoformat() if channel.created_at else "",
        updated_at=channel.updated_at.isoformat() if channel.updated_at else None,
        last_triggered_at=channel.last_triggered_at.isoformat() if channel.last_triggered_at else None,
        last_trigger_status=channel.last_trigger_status,
        last_error=channel.last_error
    )


@router.post("", response_model=EventChannelResponse)
async def create_event_channel(
    channel_data: EventChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """创建事件通知渠道"""
    # 验证渠道类型是否存在
    channel_class = get_channel(channel_data.channel_type)
    if not channel_class:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的渠道类型: {channel_data.channel_type}"
        )

    # 验证配置
    channel_instance = channel_class(**channel_data.config)
    is_valid, error_msg = channel_instance.validate_config(channel_data.config)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    channel = EventChannel(
        name=channel_data.name,
        channel_type=channel_data.channel_type,
        config=channel_data.config,
        events=channel_data.events,
        description=channel_data.description,
        is_active=channel_data.is_active,
        created_by=current_user.id
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)

    return EventChannelResponse(
        id=channel.id,
        name=channel.name,
        channel_type=channel.channel_type,
        config=channel.config or {},
        events=channel.events or [],
        description=channel.description,
        is_active=channel.is_active,
        created_at=channel.created_at.isoformat() if channel.created_at else "",
        updated_at=None,
        last_triggered_at=None,
        last_trigger_status=None,
        last_error=None
    )


@router.put("/{channel_id}", response_model=EventChannelResponse)
async def update_event_channel(
    channel_id: int,
    channel_data: EventChannelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """更新事件通知渠道"""
    channel = db.query(EventChannel).filter(EventChannel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")

    # 如果更改了渠道类型，验证新类型
    if channel_data.channel_type and channel_data.channel_type != channel.channel_type:
        channel_class = get_channel(channel_data.channel_type)
        if not channel_class:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的渠道类型: {channel_data.channel_type}"
            )

    # 如果更新了配置，验证配置
    if channel_data.config:
        channel_type = channel_data.channel_type or channel.channel_type
        channel_class = get_channel(channel_type)
        if channel_class:
            channel_instance = channel_class(**channel_data.config)
            is_valid, error_msg = channel_instance.validate_config(channel_data.config)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)

    # 更新字段
    update_data = channel_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(channel, key, value)

    db.commit()
    db.refresh(channel)

    return EventChannelResponse(
        id=channel.id,
        name=channel.name,
        channel_type=channel.channel_type,
        config=channel.config or {},
        events=channel.events or [],
        description=channel.description,
        is_active=channel.is_active,
        created_at=channel.created_at.isoformat() if channel.created_at else "",
        updated_at=channel.updated_at.isoformat() if channel.updated_at else None,
        last_triggered_at=channel.last_triggered_at.isoformat() if channel.last_triggered_at else None,
        last_trigger_status=channel.last_trigger_status,
        last_error=channel.last_error
    )


@router.delete("/{channel_id}")
async def delete_event_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """删除事件通知渠道"""
    channel = db.query(EventChannel).filter(EventChannel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")

    db.delete(channel)
    db.commit()

    return {"message": "删除成功"}


@router.post("/{channel_id}/test", response_model=TestChannelResponse)
async def test_event_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """测试事件通知渠道"""
    channel = db.query(EventChannel).filter(EventChannel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")

    # 获取渠道类并创建实例
    channel_class = get_channel(channel.channel_type)
    if not channel_class:
        return TestChannelResponse(
            success=False,
            error=f"不支持的渠道类型: {channel.channel_type}"
        )

    channel_instance = channel_class(**channel.config)

    # 构造测试消息
    test_event = "test"
    test_data = {
        "message": "这是一条测试消息",
        "timestamp": datetime.now().isoformat(),
        "test": True
    }
    message_content = channel_instance.format_message(test_event, test_data)

    # 发送测试消息
    success, result = await channel_instance.send(message_content)

    # 更新最后触发状态
    channel.last_triggered_at = datetime.utcnow()
    channel.last_trigger_status = success
    channel.last_error = result if not success else None
    db.commit()

    return TestChannelResponse(
        success=success,
        message="测试消息发送成功" if success else None,
        error=result if not success else None
    )


@router.post("/{channel_id}/toggle")
async def toggle_event_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """切换渠道启用状态"""
    channel = db.query(EventChannel).filter(EventChannel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")

    channel.is_active = not channel.is_active
    db.commit()

    return {
        "message": f"渠道已{'启用' if channel.is_active else '禁用'}",
        "is_active": channel.is_active
    }