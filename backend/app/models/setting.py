"""
配置与日志模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Setting(Base):
    """系统配置表"""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False, comment="配置键")
    value = Column(Text, nullable=True, comment="配置值")
    description = Column(String(255), nullable=True, comment="说明")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def __repr__(self):
        return f"<Setting {self.key}>"


class CompetitionTheme(Base):
    """大赛主题表"""
    __tablename__ = "competition_themes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="主题名称")
    description = Column(Text, nullable=True, comment="主题描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    order = Column(Integer, default=0, comment="排序权重")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    works = relationship("Work", back_populates="theme_obj")

    def __repr__(self):
        return f"<CompetitionTheme {self.name}>"


class Log(Base):
    """系统日志表"""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="操作用户ID")
    action = Column(String(50), nullable=False, comment="操作类型")
    resource = Column(String(100), nullable=True, comment="资源类型")
    resource_id = Column(Integer, nullable=True, comment="资源ID")
    details = Column(Text, nullable=True, comment="详情")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    created_at = Column(DateTime, default=datetime.utcnow, comment="操作时间")

    # 关系
    user = relationship("User", back_populates="logs")

    def __repr__(self):
        return f"<Log {self.action} {self.resource}>"