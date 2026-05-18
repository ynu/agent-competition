"""
Webhook 模型
"""
import hmac
import hashlib
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class WebhookEventType:
    """Webhook 事件类型"""
    # 队伍事件
    TEAM_CREATED = "team.created"
    TEAM_UPDATED = "team.updated"
    TEAM_DELETED = "team.deleted"
    TEAM_MEMBER_ADDED = "team.member_added"
    TEAM_MEMBER_REMOVED = "team.member_removed"

    # 作品事件
    WORK_CREATED = "work.created"
    WORK_UPDATED = "work.updated"
    WORK_DELETED = "work.deleted"

    # 评审事件
    REVIEW_CREATED = "review.created"
    REVIEW_UPDATED = "review.updated"

    # 投票事件
    VOTE_CREATED = "vote.created"

    # 内容事件
    CONTENT_CREATED = "content.created"
    CONTENT_UPDATED = "content.updated"
    CONTENT_DELETED = "content.deleted"

    # 用户事件
    USER_REGISTERED = "user.registered"

    @classmethod
    def all_events(cls) -> list:
        """获取所有事件类型"""
        return [
            cls.TEAM_CREATED, cls.TEAM_UPDATED, cls.TEAM_DELETED,
            cls.TEAM_MEMBER_ADDED, cls.TEAM_MEMBER_REMOVED,
            cls.WORK_CREATED, cls.WORK_UPDATED, cls.WORK_DELETED,
            cls.REVIEW_CREATED, cls.REVIEW_UPDATED,
            cls.VOTE_CREATED,
            cls.CONTENT_CREATED, cls.CONTENT_UPDATED, cls.CONTENT_DELETED,
            cls.USER_REGISTERED
        ]

    @classmethod
    def get_event_groups(cls) -> dict:
        """获取按资源分组的事件"""
        return {
            "队伍": [cls.TEAM_CREATED, cls.TEAM_UPDATED, cls.TEAM_DELETED,
                     cls.TEAM_MEMBER_ADDED, cls.TEAM_MEMBER_REMOVED],
            "作品": [cls.WORK_CREATED, cls.WORK_UPDATED, cls.WORK_DELETED],
            "评审": [cls.REVIEW_CREATED, cls.REVIEW_UPDATED],
            "投票": [cls.VOTE_CREATED],
            "内容": [cls.CONTENT_CREATED, cls.CONTENT_UPDATED, cls.CONTENT_DELETED],
            "用户": [cls.USER_REGISTERED]
        }


class Webhook(Base):
    """Webhook 配置表"""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="Webhook 名称")
    url = Column(String(500), nullable=False, comment="回调地址")
    secret = Column(String(255), nullable=True, comment="签名密钥")
    events = Column(JSON, nullable=False, default=list, comment="订阅的事件类型")
    is_active = Column(Boolean, default=True, comment="是否启用")
    description = Column(String(255), nullable=True, comment="描述")
    headers = Column(JSON, nullable=True, default=dict, comment="自定义请求头")
    created_by = Column(Integer, nullable=True, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    last_triggered_at = Column(DateTime, nullable=True, comment="最后触发时间")
    last_trigger_status = Column(Integer, nullable=True, comment="最后触发状态码")

    @staticmethod
    def generate_signature(payload: str, secret: str) -> str:
        """生成 HMAC-SHA256 签名"""
        if not secret:
            return ""
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    def verify_signature(self, payload: str, signature: str) -> bool:
        """验证签名"""
        if not self.secret or not signature:
            return False
        expected = self.generate_signature(payload, self.secret)
        return hmac.compare_digest(expected, signature)

    def __repr__(self):
        return f"<Webhook {self.name}>"


class WebhookDelivery(Base):
    """Webhook 投递记录表"""
    __tablename__ = "webhook_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, nullable=False, index=True, comment="Webhook ID")
    event = Column(String(50), nullable=False, comment="事件类型")
    payload = Column(Text, nullable=False, comment="请求载荷")
    response_status = Column(Integer, nullable=True, comment="响应状态码")
    response_body = Column(Text, nullable=True, comment="响应内容")
    error_message = Column(Text, nullable=True, comment="错误信息")
    attempt = Column(Integer, default=1, comment="尝试次数")
    created_at = Column(DateTime, default=datetime.utcnow, comment="投递时间")

    def __repr__(self):
        return f"<WebhookDelivery {self.id} {self.event}>"