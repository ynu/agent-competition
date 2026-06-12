"""
队伍相关模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class TeamStatus(str, enum.Enum):
    """队伍状态"""
    PENDING = "pending"     # 待审核
    APPROVED = "approved"   # 已通过
    REJECTED = "rejected"   # 已拒绝


class Team(Base):
    """队伍表"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False, comment="队名")
    description = Column(Text, nullable=True, comment="队伍描述")
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="队长用户ID")
    status = Column(SQLEnum(TeamStatus), default=TeamStatus.PENDING, comment="状态")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    leader = relationship("User", foreign_keys=[leader_id], back_populates="teams_as_leader")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    works = relationship("Work", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team {self.name}>"


class TeamMember(Base):
    """队伍成员表"""
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, comment="队伍ID")
    user_id = Column(String(50), nullable=True, comment="用户ID（保留字段，可选）")
    student_id = Column(String(50), nullable=False, comment="学工号")
    name = Column(String(100), nullable=False, comment="姓名")
    is_leader = Column(Boolean, default=False, comment="是否队长")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    team = relationship("Team", back_populates="members")

    def __repr__(self):
        return f"<TeamMember {self.name}>"