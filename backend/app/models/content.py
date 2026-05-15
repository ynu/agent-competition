"""
内容/栏目模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ContentType(str, enum.Enum):
    """内容类型"""
    PAGE = "page"       # 页面
    CATEGORY = "category"  # 栏目
    ARTICLE = "article"    # 文章/新闻


class ContentContentType(str, enum.Enum):
    """内容格式"""
    MARKDOWN = "markdown"
    HTML = "html"


class Content(Base):
    """内容/栏目表"""
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="标题")
    slug = Column(String(100), unique=True, index=True, nullable=True, comment="slug标识")
    type = Column(SQLEnum(ContentType), default=ContentType.PAGE, comment="类型")
    content = Column(Text, nullable=True, comment="内容")
    content_format = Column(SQLEnum(ContentContentType), default=ContentContentType.MARKDOWN, comment="内容格式")
    parent_id = Column(Integer, ForeignKey("contents.id"), nullable=True, comment="父级ID")
    order = Column(Integer, default=0, comment="排序")
    is_published = Column(Boolean, default=False, comment="是否发布")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    parent = relationship("Content", remote_side=[id], back_populates="children")
    children = relationship("Content", back_populates="parent")

    # 文章特有字段
    summary = Column(String(500), nullable=True, comment="摘要")
    author = Column(String(100), nullable=True, comment="作者")
    cover_image = Column(String(500), nullable=True, comment="封面图片URL")
    view_count = Column(Integer, default=0, comment="浏览次数")

    def __repr__(self):
        return f"<Content {self.title}>"