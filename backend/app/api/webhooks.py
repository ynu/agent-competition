"""
Webhook 管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.webhook import Webhook, WebhookDelivery, WebhookEventType
from app.services.webhook import WebhookService


router = APIRouter(prefix="/webhooks", tags=["Webhook 管理"])


# ============== 请求/响应模型 ==============

class WebhookCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Webhook 名称")
    url: str = Field(..., description="回调地址")
    secret: Optional[str] = Field(None, max_length=255, description="签名密钥")
    events: List[str] = Field(default_factory=list, description="订阅的事件类型")
    description: Optional[str] = Field(None, description="描述")
    headers: Optional[dict] = Field(default_factory=dict, description="自定义请求头")
    is_active: bool = Field(True, description="是否启用")


class WebhookUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    url: Optional[str] = None
    secret: Optional[str] = Field(None, max_length=255)
    events: Optional[List[str]] = None
    description: Optional[str] = None
    headers: Optional[dict] = None
    is_active: Optional[bool] = None


class WebhookResponse(BaseModel):
    id: int
    name: str
    url: str
    secret: Optional[str] = None
    events: List[str]
    description: Optional[str] = None
    headers: Optional[dict] = None
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    last_triggered_at: Optional[str] = None
    last_trigger_status: Optional[int] = None

    class Config:
        from_attributes = True


class WebhookListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[WebhookResponse]


class WebhookDeliveryResponse(BaseModel):
    id: int
    webhook_id: int
    event: str
    payload: str
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    attempt: int
    created_at: str

    class Config:
        from_attributes = True


class TestWebhookResponse(BaseModel):
    success: bool
    status: Optional[int] = None
    response: Optional[str] = None
    error: Optional[str] = None


class EventTypeInfo(BaseModel):
    name: str
    description: str
    group: str


# ============== 路由实现 ==============

@router.get("/event-types", response_model=dict)
async def get_event_types():
    """获取所有可用的 Webhook 事件类型"""
    event_descriptions = {
        WebhookEventType.TEAM_CREATED: "队伍创建",
        WebhookEventType.TEAM_UPDATED: "队伍更新",
        WebhookEventType.TEAM_DELETED: "队伍删除",
        WebhookEventType.TEAM_MEMBER_ADDED: "队伍成员添加",
        WebhookEventType.TEAM_MEMBER_REMOVED: "队伍成员移除",
        WebhookEventType.WORK_CREATED: "作品创建",
        WebhookEventType.WORK_UPDATED: "作品更新",
        WebhookEventType.WORK_DELETED: "作品删除",
        WebhookEventType.REVIEW_CREATED: "评审创建",
        WebhookEventType.REVIEW_UPDATED: "评审更新",
        WebhookEventType.VOTE_CREATED: "投票创建",
        WebhookEventType.CONTENT_CREATED: "内容创建",
        WebhookEventType.CONTENT_UPDATED: "内容更新",
        WebhookEventType.CONTENT_DELETED: "内容删除",
        WebhookEventType.USER_REGISTERED: "用户注册",
    }

    groups = WebhookEventType.get_event_groups()
    result = {}
    for group_name, events in groups.items():
        result[group_name] = [
            {
                "name": event,
                "description": event_descriptions.get(event, event),
                "group": group_name
            }
            for event in events
        ]

    return result


@router.get("", response_model=WebhookListResponse)
async def get_webhooks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """获取 Webhook 列表"""
    query = db.query(Webhook)

    if keyword:
        query = query.filter(
            Webhook.name.contains(keyword) |
            Webhook.url.contains(keyword)
        )

    if is_active is not None:
        query = query.filter(Webhook.is_active == is_active)

    total = query.count()
    webhooks = query.order_by(Webhook.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # 构建响应（隐藏完整 secret）
    items = []
    for w in webhooks:
        items.append(WebhookResponse(
            id=w.id,
            name=w.name,
            url=w.url,
            secret=w.secret[:8] + "***" if w.secret else None,  # 只显示前8位
            events=w.events or [],
            description=w.description,
            headers=w.headers,
            is_active=w.is_active,
            created_at=w.created_at.isoformat() if w.created_at else "",
            updated_at=w.updated_at.isoformat() if w.updated_at else None,
            last_triggered_at=w.last_triggered_at.isoformat() if w.last_triggered_at else None,
            last_trigger_status=w.last_trigger_status
        ))

    return WebhookListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """获取单个 Webhook 详情"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook 不存在")

    return WebhookResponse(
        id=webhook.id,
        name=webhook.name,
        url=webhook.url,
        secret=webhook.secret[:8] + "***" if webhook.secret else None,
        events=webhook.events or [],
        description=webhook.description,
        headers=webhook.headers,
        is_active=webhook.is_active,
        created_at=webhook.created_at.isoformat() if webhook.created_at else "",
        updated_at=webhook.updated_at.isoformat() if webhook.updated_at else None,
        last_triggered_at=webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None,
        last_trigger_status=webhook.last_trigger_status
    )


@router.post("", response_model=WebhookResponse)
async def create_webhook(
    webhook_data: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """创建 Webhook"""
    # 验证事件类型
    valid_events = WebhookEventType.all_events()
    for event in webhook_data.events:
        if event not in valid_events:
            raise HTTPException(status_code=400, detail=f"无效的事件类型: {event}")

    # 验证 URL 格式
    if not webhook_data.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL 必须以 http:// 或 https:// 开头")

    webhook = Webhook(
        name=webhook_data.name,
        url=webhook_data.url,
        secret=webhook_data.secret,
        events=webhook_data.events,
        description=webhook_data.description,
        headers=webhook_data.headers or {},
        is_active=webhook_data.is_active,
        created_by=current_user.id
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)

    return WebhookResponse(
        id=webhook.id,
        name=webhook.name,
        url=webhook.url,
        secret=webhook.secret[:8] + "***" if webhook.secret else None,
        events=webhook.events or [],
        description=webhook.description,
        headers=webhook.headers,
        is_active=webhook.is_active,
        created_at=webhook.created_at.isoformat() if webhook.created_at else "",
        updated_at=None,
        last_triggered_at=None,
        last_trigger_status=None
    )


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: int,
    webhook_data: WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """更新 Webhook"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook 不存在")

    # 验证事件类型
    if webhook_data.events is not None:
        valid_events = WebhookEventType.all_events()
        for event in webhook_data.events:
            if event not in valid_events:
                raise HTTPException(status_code=400, detail=f"无效的事件类型: {event}")

    # 验证 URL 格式
    if webhook_data.url is not None and not webhook_data.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL 必须以 http:// 或 https:// 开头")

    # 更新字段
    update_data = webhook_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(webhook, key, value)

    db.commit()
    db.refresh(webhook)

    return WebhookResponse(
        id=webhook.id,
        name=webhook.name,
        url=webhook.url,
        secret=webhook.secret[:8] + "***" if webhook.secret else None,
        events=webhook.events or [],
        description=webhook.description,
        headers=webhook.headers,
        is_active=webhook.is_active,
        created_at=webhook.created_at.isoformat() if webhook.created_at else "",
        updated_at=webhook.updated_at.isoformat() if webhook.updated_at else None,
        last_triggered_at=webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None,
        last_trigger_status=webhook.last_trigger_status
    )


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """删除 Webhook"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook 不存在")

    # 删除关联的投递记录
    db.query(WebhookDelivery).filter(WebhookDelivery.webhook_id == webhook_id).delete()

    db.delete(webhook)
    db.commit()

    return {"message": "删除成功"}


@router.post("/{webhook_id}/test", response_model=TestWebhookResponse)
async def test_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """测试 Webhook"""
    service = WebhookService(db)
    result = service.test_webhook(webhook_id)
    return TestWebhookResponse(**result)


@router.get("/{webhook_id}/deliveries")
async def get_webhook_deliveries(
    webhook_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """获取 Webhook 投递记录"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook 不存在")

    query = db.query(WebhookDelivery).filter(
        WebhookDelivery.webhook_id == webhook_id
    ).order_by(WebhookDelivery.created_at.desc())

    total = query.count()
    deliveries = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            WebhookDeliveryResponse(
                id=d.id,
                webhook_id=d.webhook_id,
                event=d.event,
                payload=d.payload,
                response_status=d.response_status,
                response_body=d.response_body,
                error_message=d.error_message,
                attempt=d.attempt,
                created_at=d.created_at.isoformat() if d.created_at else ""
            )
            for d in deliveries
        ]
    }


@router.get("/{webhook_id}/secret")
async def get_webhook_secret(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """获取 Webhook 完整密钥（仅管理员）"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook 不存在")

    return {"secret": webhook.secret}