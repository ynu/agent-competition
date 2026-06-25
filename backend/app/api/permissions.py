"""
权限管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.permission import Permission, Role, get_default_permissions, get_default_roles, role_permissions
from app.schemas.common import PageResponse
from pydantic import BaseModel

router = APIRouter(prefix="/permissions", tags=["权限管理"])


# Schema
class PermissionResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    category: str
    action: str

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    is_system: bool
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str
    description: Optional[str]
    permission_ids: List[int] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class UserRoleUpdate(BaseModel):
    role: str


def init_permissions(db: Session):
    """初始化权限和角色数据"""
    # 初始化权限 - 检查并添加缺失的权限
    existing_codes = {p.code for p in db.query(Permission).all()}
    for perm_data in get_default_permissions():
        if perm_data["code"] not in existing_codes:
            perm = Permission(**perm_data)
            db.add(perm)
    db.commit()

    # 初始化角色
    existing_roles = db.query(Role).count()
    if existing_roles == 0:
        for role_data in get_default_roles():
            permission_codes = role_data.pop("permissions", [])
            role = Role(**role_data)
            db.add(role)
            db.flush()

            # 关联权限
            for perm_code in permission_codes:
                perm = db.query(Permission).filter(Permission.code == perm_code).first()
                if perm:
                    role.permissions.append(perm)

        # 为管理员角色添加所有权限
        admin_role = db.query(Role).filter(Role.code == "admin").first()
        if admin_role:
            all_perms = db.query(Permission).all()
            admin_role.permissions = all_perms

        db.commit()


@router.get("/init")
async def init_permissions_data(db: Session = Depends(get_db)):
    """初始化权限数据"""
    init_permissions(db)
    return {"message": "权限数据初始化成功"}


@router.get("/categories")
async def get_permission_categories():
    """获取权限分类列表"""
    categories = [
        {"code": "user", "name": "用户管理"},
        {"code": "team", "name": "队伍管理"},
        {"code": "work", "name": "作品管理"},
        {"code": "review", "name": "评审管理"},
        {"code": "content", "name": "内容管理"},
        {"code": "setting", "name": "配置管理"},
        {"code": "log", "name": "日志管理"},
        {"code": "message", "name": "消息管理"},
        {"code": "webhook", "name": "Webhook管理"},
        {"code": "event", "name": "事件通知"},
    ]
    return {"categories": categories}


@router.get("", response_model=PageResponse)
async def get_permissions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """获取权限列表"""
    query = db.query(Permission)

    if category:
        query = query.filter(Permission.category == category)
    if keyword:
        query = query.filter(Permission.name.contains(keyword))

    total = query.count()
    items = query.order_by(Permission.category, Permission.action).offset((page - 1) * page_size).limit(page_size).all()

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[PermissionResponse.model_validate(p) for p in items]
    )


@router.get("/roles", response_model=PageResponse)
async def get_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """获取角色列表"""
    query = db.query(Role)
    total = query.count()
    items = query.order_by(Role.id).offset((page - 1) * page_size).limit(page_size).all()

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[RoleResponse.model_validate(r) for r in items]
    )


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """获取角色详情"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    return RoleResponse.model_validate(role)


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """创建角色"""
    # 检查角色代码是否已存在
    existing = db.query(Role).filter(Role.code == role_data.name.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="角色已存在")

    role = Role(
        code=role_data.name.lower(),
        name=role_data.name,
        description=role_data.description,
        is_system=False
    )

    # 关联权限
    for perm_id in role_data.permission_ids:
        perm = db.query(Permission).filter(Permission.id == perm_id).first()
        if perm:
            role.permissions.append(perm)

    db.add(role)
    db.commit()
    db.refresh(role)

    return RoleResponse.model_validate(role)


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """更新角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role.is_system:
        raise HTTPException(status_code=400, detail="系统角色不可修改")

    if role_data.name is not None:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description
    if role_data.permission_ids is not None:
        role.permissions = []
        for perm_id in role_data.permission_ids:
            perm = db.query(Permission).filter(Permission.id == perm_id).first()
            if perm:
                role.permissions.append(perm)

    db.commit()
    db.refresh(role)

    return RoleResponse.model_validate(role)


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """删除角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role.is_system:
        raise HTTPException(status_code=400, detail="系统角色不可删除")

    db.delete(role)
    db.commit()

    return {"message": "删除成功"}


@router.get("/my-permissions")
async def get_my_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户权限"""
    from app.core.security import get_user_permissions
    permissions = get_user_permissions(db, current_user)

    # 获取用户角色信息
    role_code = current_user.role.value

    return {
        "role": role_code,
        "permissions": permissions
    }