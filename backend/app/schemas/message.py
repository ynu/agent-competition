"""
站内消息 Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# 消息创建 schema
class MessageCreate(BaseModel):
    receiver_ids: List[int] = Field(..., min_length=1, description="接收者用户ID列表")
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, description="消息内容，支持富文本")


# 消息响应 schema
class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    title: str
    content: str
    is_read: bool
    created_at: datetime
    sender_username: Optional[str] = None
    sender_nickname: Optional[str] = None
    receiver_username: Optional[str] = None
    receiver_nickname: Optional[str] = None

    class Config:
        from_attributes = True


# 未读计数响应
class UnreadCountResponse(BaseModel):
    unread_count: int