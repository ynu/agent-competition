"""
事件通知渠道模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from app.core.database import Base


class EventChannel(Base):
    """事件通知渠道配置表"""
    __tablename__ = "event_channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="渠道名称")
    channel_type = Column(String(50), nullable=False, comment="渠道类型：wecom-bot")
    config = Column(JSON, nullable=False, default=dict, comment="渠道配置（如 webhook_url）")
    events = Column(JSON, nullable=False, default=list, comment="订阅的事件类型列表")
    is_active = Column(Boolean, default=True, comment="是否启用")
    description = Column(String(255), nullable=True, comment="描述")
    created_by = Column(Integer, nullable=True, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    last_triggered_at = Column(DateTime, nullable=True, comment="最后触发时间")
    last_trigger_status = Column(Boolean, nullable=True, comment="最后触发状态")
    last_error = Column(Text, nullable=True, comment="最后错误信息")

    def __repr__(self):
        return f"<EventChannel {self.name} ({self.channel_type})>"