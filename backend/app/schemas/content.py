"""
内容 Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.models.content import ContentType, ContentContentType


# 内容基础 schema
class ContentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
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
    # 快捷入口特有字段
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)
    external_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=500)

    @field_validator("slug", "category", "tags", "external_url", "icon", "summary", "author", "cover_image", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        """空字符串视为未填写"""
        if isinstance(v, str) and not v.strip():
            return None
        return v


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
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)
    external_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=500)

    @field_validator("slug", "category", "tags", "external_url", "icon", "summary", "author", "cover_image", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        """空字符串视为未填写"""
        if isinstance(v, str) and not v.strip():
            return None
        return v


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