"""
配置与日志 Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# 配置基础 schema
class SettingBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: Optional[str] = None
    description: Optional[str] = Field(None, max_length=255)


# 配置创建 schema
class SettingCreate(SettingBase):
    pass


# 配置更新 schema
class SettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = Field(None, max_length=255)


# 配置响应 schema
class SettingResponse(SettingBase):
    id: int
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 日志基础 schema
class LogBase(BaseModel):
    action: str = Field(..., min_length=1, max_length=50)
    resource: Optional[str] = Field(None, max_length=100)
    resource_id: Optional[int] = None
    details: Optional[str] = None


# 日志响应 schema
class LogResponse(LogBase):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# 分页响应 schema
class PageResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list