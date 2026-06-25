"""
权限模型 - RBAC 权限管理
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class PermissionCategory(str, enum.Enum):
    """权限分类"""
    USER = "user"          # 用户管理
    TEAM = "team"          # 队伍管理
    WORK = "work"          # 作品管理
    REVIEW = "review"      # 评审管理
    CONTENT = "content"    # 内容管理
    SETTING = "setting"    # 配置管理
    LOG = "log"            # 日志管理
    MESSAGE = "message"    # 消息管理
    WEBHOOK = "webhook"    # Webhook管理
    EVENT = "event"        # 事件通知
    SYSTEM = "system"      # 系统管理


class PermissionAction(str, enum.Enum):
    """权限动作"""
    CREATE = "create"      # 创建
    READ = "read"          # 读取
    UPDATE = "update"      # 更新
    DELETE = "delete"      # 删除
    AUDIT = "audit"        # 审核
    EXPORT = "export"      # 导出


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, comment="权限代码")
    name = Column(String(100), nullable=False, comment="权限名称")
    description = Column(String(500), nullable=True, comment="权限描述")
    category = Column(String(50), nullable=False, comment="权限分类")
    action = Column(String(50), nullable=False, comment="权限动作")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    def __repr__(self):
        return f"<Permission {self.code}>"


class Role(Base):
    """角色表"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, comment="角色代码")
    name = Column(String(100), nullable=False, comment="角色名称")
    description = Column(String(500), nullable=True, comment="角色描述")
    is_system = Column(Boolean, default=False, comment="是否系统角色")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

    def __repr__(self):
        return f"<Role {self.code}>"


# 角色-权限关联表
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# 更新 Permission 模型的关系
Permission.roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


def get_default_permissions():
    """获取默认权限列表"""
    permissions = [
        # 用户管理
        {"code": "user:read", "name": "查看用户", "category": "user", "action": "read"},
        {"code": "user:create", "name": "创建用户", "category": "user", "action": "create"},
        {"code": "user:update", "name": "更新用户", "category": "user", "action": "update"},
        {"code": "user:delete", "name": "删除用户", "category": "user", "action": "delete"},

        # 队伍管理
        {"code": "team:read", "name": "查看队伍", "category": "team", "action": "read"},
        {"code": "team:create", "name": "创建队伍", "category": "team", "action": "create"},
        {"code": "team:update", "name": "更新队伍", "category": "team", "action": "update"},
        {"code": "team:delete", "name": "删除队伍", "category": "team", "action": "delete"},
        {"code": "team:audit", "name": "审核队伍", "category": "team", "action": "audit"},

        # 作品管理
        {"code": "work:read", "name": "查看作品", "category": "work", "action": "read"},
        {"code": "work:create", "name": "创建作品", "category": "work", "action": "create"},
        {"code": "work:update", "name": "更新作品", "category": "work", "action": "update"},
        {"code": "work:delete", "name": "删除作品", "category": "work", "action": "delete"},
        {"code": "work:audit", "name": "审核作品", "category": "work", "action": "audit"},

        # 评审管理
        {"code": "review:read", "name": "查看评审", "category": "review", "action": "read"},
        {"code": "review:create", "name": "创建评审", "category": "review", "action": "create"},
        {"code": "review:update", "name": "更新评审", "category": "review", "action": "update"},

        # 内容管理
        {"code": "content:read", "name": "查看内容", "category": "content", "action": "read"},
        {"code": "content:create", "name": "创建内容", "category": "content", "action": "create"},
        {"code": "content:update", "name": "更新内容", "category": "content", "action": "update"},
        {"code": "content:delete", "name": "删除内容", "category": "content", "action": "delete"},

        # 配置管理
        {"code": "setting:read", "name": "查看配置", "category": "setting", "action": "read"},
        {"code": "setting:update", "name": "更新配置", "category": "setting", "action": "update"},

        # 日志管理
        {"code": "log:read", "name": "查看日志", "category": "log", "action": "read"},
        {"code": "log:export", "name": "导出日志", "category": "log", "action": "export"},

        # 消息管理
        {"code": "message:read", "name": "查看消息", "category": "message", "action": "read"},
        {"code": "message:create", "name": "发送消息", "category": "message", "action": "create"},
        {"code": "message:delete", "name": "删除消息", "category": "message", "action": "delete"},

        # Webhook管理
        {"code": "webhook:read", "name": "查看Webhook", "category": "webhook", "action": "read"},
        {"code": "webhook:create", "name": "创建Webhook", "category": "webhook", "action": "create"},
        {"code": "webhook:update", "name": "更新Webhook", "category": "webhook", "action": "update"},
        {"code": "webhook:delete", "name": "删除Webhook", "category": "webhook", "action": "delete"},

        # 事件通知
        {"code": "event:read", "name": "查看事件通知", "category": "event", "action": "read"},
        {"code": "event:create", "name": "创建事件通知", "category": "event", "action": "create"},
        {"code": "event:update", "name": "更新事件通知", "category": "event", "action": "update"},
        {"code": "event:delete", "name": "删除事件通知", "category": "event", "action": "delete"},
    ]
    return permissions


def get_default_roles():
    """获取默认角色列表"""
    return [
        {
            "code": "user",
            "name": "普通用户",
            "description": "参赛用户，可以报名、提交作品、投票",
            "permissions": ["team:create", "team:read", "work:create", "work:read", "content:read", "review:read"]
        },
        {
            "code": "reviewer",
            "name": "评审用户",
            "description": "专家评审，可以审核队伍、作品，进行评审打分",
            "permissions": ["team:read", "team:audit", "work:read", "work:audit", "review:create", "review:read", "review:update", "content:read", "log:read"]
        },
        {
            "code": "admin",
            "name": "超级管理员",
            "description": "系统管理员，拥有所有权限",
            "permissions": []  # 拥有所有权限
        }
    ]