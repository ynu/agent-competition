"""
事件通知渠道 Schema
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class EventChannelCreate(BaseModel):
    """创建渠道请求"""
    name: str = Field(..., min_length=1, max_length=100, description="渠道名称")
    channel_type: str = Field(..., description="渠道类型")
    config: dict = Field(default_factory=dict, description="渠道配置")
    events: List[str] = Field(default_factory=list, description="订阅的事件")
    description: Optional[str] = Field(None, description="描述")
    is_active: bool = Field(True, description="是否启用")


class EventChannelUpdate(BaseModel):
    """更新渠道请求"""
    name: Optional[str] = Field(None, max_length=100)
    channel_type: Optional[str] = None
    config: Optional[dict] = None
    events: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class EventChannelResponse(BaseModel):
    """渠道响应"""
    id: int
    name: str
    channel_type: str
    config: dict
    events: List[str]
    description: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    last_triggered_at: Optional[str] = None
    last_trigger_status: Optional[bool] = None
    last_error: Optional[str] = None

    class Config:
        from_attributes = True


class EventChannelListResponse(BaseModel):
    """渠道列表响应"""
    total: int
    page: int
    page_size: int
    items: List[EventChannelResponse]


class TestChannelResponse(BaseModel):
    """测试渠道响应"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class ChannelTypeInfo(BaseModel):
    """渠道类型信息"""
    type: str
    name: str
    description: str