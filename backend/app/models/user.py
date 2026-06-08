"""
用户模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色"""
    USER = "user"           # 普通用户
    REVIEWER = "reviewer"   # 评审用户
    ADMIN = "admin"         # 超级用户


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False, comment="用户名/学工号")
    nickname = Column(String(100), nullable=True, comment="显示名称")
    email = Column(String(255), unique=True, index=True, nullable=True, comment="邮箱")
    hashed_password = Column(String(255), nullable=True, comment="密码哈希")
    role = Column(SQLEnum(UserRole), default=UserRole.USER, comment="用户角色")
    auth_source = Column(String(50), default="local", comment="认证来源")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    teams_as_leader = relationship("Team", back_populates="leader", foreign_keys="Team.leader_id")
    votes = relationship("Vote", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    logs = relationship("Log", back_populates="user")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    copyright_agreements = relationship("CopyrightAgreement", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"