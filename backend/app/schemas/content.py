"""
内容 Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.content import ContentType, ContentContentType


# 内容基础 schema
class ContentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100)
    type: ContentType = ContentType.PAGE
    content: Optional[str] = None
    content_format: ContentContentType = ContentContentType.MARKDOWN
    parent_id: Optional[int] = None
    order: int = 0
    is_published: bool = False
    # 文章特有字段
    summary: Optional[str] = Field(None, max_length=500)
    author: Optional[str] = Field(None, max_length=100)
    cover_image: Optional[str] = Field(None, max_length=500)


# 内容创建 schema
class ContentCreate(ContentBase):
    pass


# 内容更新 schema
class ContentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[ContentType] = None
    content: Optional[str] = None
    content_format: Optional[ContentContentType] = None
    parent_id: Optional[int] = None
    order: Optional[int] = None
    is_published: Optional[bool] = None
    summary: Optional[str] = Field(None, max_length=500)
    author: Optional[str] = Field(None, max_length=100)
    cover_image: Optional[str] = Field(None, max_length=500)


# 内容响应 schema
class ContentResponse(ContentBase):
    id: int
    view_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 内容树响应 schema
class ContentTreeResponse(ContentResponse):
    children: List["ContentTreeResponse"] = []

    class Config:
        from_attributes = True