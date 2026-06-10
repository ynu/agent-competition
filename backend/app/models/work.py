"""
作品相关模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class WorkStatus(str, enum.Enum):
    """作品状态"""
    PENDING = "pending"     # 待审核
    APPROVED = "approved"   # 已通过
    REJECTED = "rejected"   # 已拒绝


class Work(Base):
    """作品表"""
    __tablename__ = "works"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, comment="队伍ID")
    theme_id = Column(Integer, ForeignKey("competition_themes.id", ondelete="SET NULL"), nullable=True, comment="大赛主题ID")
    name = Column(String(100), nullable=False, comment="作品名称")
    description = Column(Text, nullable=True, comment="作品描述")
    agent_url = Column(String(500), nullable=True, comment="智能体URL")
    agent_editor_url = Column(String(500), nullable=True, comment="智能体编排URL")
    pdf_file = Column(String(500), nullable=True, comment="PDF文件路径")
    video_file = Column(String(500), nullable=True, comment="视频文件路径")
    vote_count = Column(Integer, default=0, comment="投票数")
    view_count = Column(Integer, default=0, comment="浏览次数")
    score = Column(Float, nullable=True, comment="评审分数")
    status = Column(SQLEnum(WorkStatus), default=WorkStatus.PENDING, comment="状态")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    team = relationship("Team", back_populates="works")
    theme_obj = relationship("CompetitionTheme", back_populates="works")
    votes = relationship("Vote", back_populates="work", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="work", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Work {self.name}>"


class Review(Base):
    """评审表"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(Integer, ForeignKey("works.id", ondelete="CASCADE"), nullable=False, comment="作品ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="评审用户ID")
    score = Column(Float, nullable=True, comment="评分(0-100)")
    comment = Column(Text, nullable=True, comment="评价")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    work = relationship("Work", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"<Review work={self.work_id} user={self.user_id}>"


class Vote(Base):
    """投票表"""
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="投票用户ID")
    work_id = Column(Integer, ForeignKey("works.id", ondelete="CASCADE"), nullable=False, comment="作品ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="投票时间")

    # 关系
    user = relationship("User", back_populates="votes")
    work = relationship("Work", back_populates="votes")

    def __repr__(self):
        return f"<Vote user={self.user_id} work={self.work_id}>"


class CopyrightAgreement(Base):
    """版权协议签署表"""
    __tablename__ = "copyright_agreements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="签署用户ID")
    signature_data = Column(Text, nullable=False, comment="签名数据（Base64编码）")
    signature_name = Column(String(100), nullable=True, comment="签名人姓名")
    ip_address = Column(String(50), nullable=True, comment="签署IP地址")
    user_agent = Column(String(500), nullable=True, comment="浏览器User-Agent")
    agreement_content = Column(Text, nullable=False, comment="协议内容快照")
    created_at = Column(DateTime, default=datetime.utcnow, comment="签署时间")

    # 关系
    user = relationship("User", back_populates="copyright_agreements")

    def __repr__(self):
        return f"<CopyrightAgreement user={self.user_id}>"