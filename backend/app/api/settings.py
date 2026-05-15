"""
配置管理 API 路由
"""
import json
import base64
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_active_user_optional, require_role
from app.models.user import User, UserRole
from app.models.setting import Setting, CompetitionTheme
from app.schemas.common import SettingCreate, SettingUpdate, SettingResponse, PageResponse

router = APIRouter(prefix="/settings", tags=["配置管理"])

# 默认配置项（按类别分组 + 排序）
DEFAULT_SETTINGS = {
    # ========== 基础限制 ==========
    "max_votes": {"value": "5", "description": "Max votes per user (0 = unlimited)", "sort_order": 10},
    "max_team_members": {"value": "5", "description": "Max team members", "sort_order": 11},
    "max_works_per_team": {"value": "5", "description": "Max works per team", "sort_order": 12},
    # ========== 报名时间 ==========
    "registration_start": {"value": "", "description": "Registration start time (ISO format, empty = no limit)", "sort_order": 20},
    "registration_end": {"value": "", "description": "Registration end time (ISO format, empty = no limit)", "sort_order": 21},
    # ========== 作品提交时间 ==========
    "submission_start": {"value": "", "description": "Submission start time (ISO format, empty = no limit)", "sort_order": 30},
    "submission_end": {"value": "", "description": "Submission end time (ISO format, empty = no limit)", "sort_order": 31},
    # ========== 投票时间 ==========
    "voting_start": {"value": "", "description": "Voting start time (ISO format, empty = no limit)", "sort_order": 40},
    "voting_end": {"value": "", "description": "Voting end time (ISO format, empty = no limit)", "sort_order": 41},
    # ========== 大赛信息 ==========
    "competition_theme": {"value": "", "description": "Competition theme name", "sort_order": 50},
    "competition_description": {"value": "", "description": "Competition theme description", "sort_order": 51},
    "themes": {"value": "智能问答,Agent工作流,多智能体协作,智能客服,数据分析,内容生成", "description": "Work themes (comma-separated)", "sort_order": 52},
    # ========== 统一身份认证 ==========
    "cas_enabled": {"value": "true", "description": "Enable CAS authentication", "sort_order": 60},
    "cas_base_url": {"value": "https://ids.ynu.edu.cn/authserver", "description": "CAS server URL", "sort_order": 61},
    "base_url": {"value": "http://localhost:5173", "description": "Application base URL (for CAS callback)", "sort_order": 62},
}


# Theme structure
class ThemeItem(BaseModel):
    id: int
    name: str
    description: str = ""
    is_active: bool = True


def ensure_default_settings(db: Session):
    """确保默认配置存在"""
    for key, config in DEFAULT_SETTINGS.items():
        existing = db.query(Setting).filter(Setting.key == key).first()
        if not existing:
            setting = Setting(
                key=key,
                value=config["value"],
                description=config["description"],
                sort_order=config.get("sort_order", 99)
            )
            db.add(setting)

    # 更新现有配置的 sort_order
    for key, config in DEFAULT_SETTINGS.items():
        setting = db.query(Setting).filter(Setting.key == key).first()
        if setting and setting.sort_order != config.get("sort_order", 99):
            setting.sort_order = config.get("sort_order", 99)

    # 删除旧配置 max_votes_per_day
    old_setting = db.query(Setting).filter(Setting.key == "max_votes_per_day").first()
    if old_setting:
        db.delete(old_setting)

    db.commit()

    # 确保CompetitionTheme表有默认数据
    theme_count = db.query(CompetitionTheme).count()
    if theme_count == 0:
        default_themes = [
            "智能问答", "Agent工作流", "多智能体协作", "智能客服", "数据分析", "内容生成"
        ]
        for i, name in enumerate(default_themes):
            theme = CompetitionTheme(name=name, description="", is_active=True, order=i)
            db.add(theme)
        db.commit()


@router.get("", response_model=PageResponse)
async def get_settings(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """获取配置列表"""
    # 确保默认配置存在
    ensure_default_settings(db)

    query = db.query(Setting)

    if keyword:
        query = query.filter(Setting.key.contains(keyword))

    total = query.count()
    settings = query.order_by(Setting.sort_order, Setting.key).offset((page - 1) * page_size).limit(page_size).all()

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[SettingResponse.model_validate(s) for s in settings]
    )


# 注意：特定路由必须放在通用路由 /{key} 之前

@router.get("/competition-themes", response_model=PageResponse)
async def get_competition_themes(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user_optional)
):
    """获取大赛主题列表"""
    ensure_default_settings(db)

    # 直接从数据库获取主题，使用真实的数据库ID
    query = db.query(CompetitionTheme).filter(CompetitionTheme.is_active == True)

    # 按order排序
    query = query.order_by(CompetitionTheme.order)

    total = query.count()
    themes = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for t in themes:
        items.append({
            "id": t.id,  # 使用数据库自增ID，不是数组索引
            "name": t.name,
            "description": t.description,
            "is_active": t.is_active,
            "order": t.order
        })

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


# 注意：特定路由必须放在通用路由 /{key} 之前
# 以下是主题排序相关路由

@router.put("/reorder-themes")
async def reorder_themes_api(
    body: dict = Body(..., description="主题ID列表，按新顺序排列"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """重新排序大赛主题"""
    theme_ids = body.get("theme_ids", [])

    # 使用数据库ID更新排序
    for i, theme_id in enumerate(theme_ids):
        theme = db.query(CompetitionTheme).filter(CompetitionTheme.id == theme_id).first()
        if theme:
            theme.order = i
    db.commit()

    return {"message": "排序已更新"}


@router.get("/themes/list")
async def get_themes(
    db: Session = Depends(get_db)
):
    """获取作品主题列表（公开接口，返回启用的主题）"""
    ensure_default_settings(db)

    # 直接从数据库获取
    themes = db.query(CompetitionTheme).filter(CompetitionTheme.is_active == True).order_by(CompetitionTheme.order).all()
    theme_names = [t.name for t in themes]

    if not theme_names:
        theme_names = ["智能问答", "Agent工作流", "多智能体协作", "智能客服", "数据分析", "内容生成"]

    return {"themes": theme_names}


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """获取单个配置"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        # 返回默认值
        if key in DEFAULT_SETTINGS:
            return SettingResponse(
                id=0,
                key=key,
                value=DEFAULT_SETTINGS[key]["value"],
                description=DEFAULT_SETTINGS[key]["description"]
            )
        raise HTTPException(status_code=404, detail="配置不存在")

    return SettingResponse.model_validate(setting)


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    setting_data: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """更新配置"""
    setting = db.query(Setting).filter(Setting.key == key).first()

    if not setting:
        # 检查是否是有效配置键
        if key in DEFAULT_SETTINGS:
            setting = Setting(
                key=key,
                value=setting_data.value or DEFAULT_SETTINGS[key]["value"],
                description=setting_data.description or DEFAULT_SETTINGS[key]["description"]
            )
            db.add(setting)
        else:
            raise HTTPException(status_code=404, detail="配置不存在")
    else:
        if setting_data.value is not None:
            setting.value = setting_data.value
        if setting_data.description is not None:
            setting.description = setting_data.description

    db.commit()
    db.refresh(setting)

    return SettingResponse.model_validate(setting)


@router.post("/init")
async def init_default_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """初始化默认配置"""
    ensure_default_settings(db)
    return {"message": "默认配置初始化成功"}


# ============== 大赛主题管理 ==============

class ThemeCreate(BaseModel):
    name: str
    description: str = ""
    is_active: bool = True
    order: int = 0


class ThemeUpdate(BaseModel):
    name: str = None
    description: str = None
    is_active: bool = None
    order: int = None


class ThemeResponse(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool
    order: int = 0

    class Config:
        from_attributes = True

    def model_dump(self, **kwargs):
        # Ensure strings are properly encoded
        data = super().model_dump(**kwargs)
        for key, value in data.items():
            if isinstance(value, str):
                # Re-encode to handle any encoding issues
                data[key] = value.encode('utf-8').decode('utf-8')
        return data


# ============== 主题保存辅助函数 ==============

def save_themes(db: Session, themes: list):
    """保存主题列表到设置，并同步到CompetitionTheme表"""
    setting = db.query(Setting).filter(Setting.key == "themes").first()
    if not setting:
        setting = Setting(key="themes", value="[]", description="智能体主题列表(JSON格式)")
        db.add(setting)

    # Convert to JSON bytes first
    json_bytes = json.dumps(themes, ensure_ascii=False).encode('utf-8')
    # Store as base64 with prefix to avoid any encoding issues
    setting.value = 'base64:' + base64.b64encode(json_bytes).decode('ascii')

    # 同步到CompetitionTheme表
    # 先删除所有现有主题
    db.query(CompetitionTheme).delete()
    # 重新创建
    for i, theme_data in enumerate(themes):
        new_theme = CompetitionTheme(
            name=theme_data.get("name", ""),
            description=theme_data.get("description", ""),
            is_active=theme_data.get("is_active", True),
            order=i
        )
        db.add(new_theme)

    db.commit()


def decode_themes(value: str) -> list:
    """解码主题列表"""
    if not value:
        return []

    # Check if it's base64 encoded
    if value.startswith('base64:'):
        try:
            json_bytes = base64.b64decode(value[7:])
            return json.loads(json_bytes.decode('utf-8'))
        except:
            return []

    # Legacy format: JSON array
    if value.startswith('['):
        try:
            return json.loads(value)
        except:
            return []

    # Legacy format: comma-separated
    if ',' in value:
        theme_names = [t.strip() for t in value.split(",") if t.strip()]
        return [{"name": name, "description": "", "is_active": True, "order": i}
                for i, name in enumerate(theme_names)]

    return []


@router.post("/competition-themes", response_model=ThemeResponse)
async def create_competition_theme(
    theme_data: ThemeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """创建大赛主题"""
    ensure_default_settings(db)

    # 检查主题名是否已存在
    existing = db.query(CompetitionTheme).filter(CompetitionTheme.name == theme_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="主题名称已存在")

    # 获取最大order值
    max_order = db.query(func.max(CompetitionTheme.order)).scalar() or -1

    # 创建新主题
    new_theme = CompetitionTheme(
        name=theme_data.name,
        description=theme_data.description or "",
        is_active=theme_data.is_active,
        order=max_order + 1
    )
    db.add(new_theme)
    db.commit()
    db.refresh(new_theme)

    return ThemeResponse(
        id=new_theme.id,
        name=new_theme.name,
        description=new_theme.description,
        is_active=new_theme.is_active,
        order=new_theme.order
    )


@router.put("/competition-themes/{theme_id}", response_model=ThemeResponse)
async def update_competition_theme(
    theme_id: int,
    theme_data: ThemeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """更新大赛主题"""
    ensure_default_settings(db)

    theme = db.query(CompetitionTheme).filter(CompetitionTheme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    # 检查主题名是否与其他主题重复
    if theme_data.name and theme_data.name != theme.name:
        existing = db.query(CompetitionTheme).filter(
            CompetitionTheme.name == theme_data.name,
            CompetitionTheme.id != theme_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="主题名称已存在")
        theme.name = theme_data.name

    if theme_data.description is not None:
        theme.description = theme_data.description
    if theme_data.is_active is not None:
        theme.is_active = theme_data.is_active
    if theme_data.order is not None:
        theme.order = theme_data.order

    db.commit()
    db.refresh(theme)

    return ThemeResponse(
        id=theme.id,
        name=theme.name,
        description=theme.description,
        is_active=theme.is_active,
        order=theme.order
    )


@router.delete("/competition-themes/{theme_id}")
async def delete_competition_theme(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """删除大赛主题"""
    ensure_default_settings(db)

    theme = db.query(CompetitionTheme).filter(CompetitionTheme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    # 删除主题
    db.delete(theme)
    db.commit()

    # 重新设置order
    themes = db.query(CompetitionTheme).order_by(CompetitionTheme.order).all()
    for i, t in enumerate(themes):
        t.order = i
    db.commit()

    return {"message": "删除成功"}


# ============== 数据管理 ==============

@router.post("/clear-data")
async def clear_all_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """清空所有数据（仅保留admin账号、角色/权限、配置）"""
    from app.models.team import Team, TeamMember
    from app.models.work import Work, Review, Vote

    # 1. 删除投票记录
    db.query(Vote).delete()
    db.commit()

    # 2. 删除评审记录
    db.query(Review).delete()
    db.commit()

    # 3. 删除作品（包括文件和关联数据）
    works = db.query(Work).all()
    import os
    from app.core.config import settings
    for work in works:
        # 删除文件
        if work.pdf_file and os.path.exists(work.pdf_file):
            try:
                os.remove(work.pdf_file)
            except:
                pass
        if work.video_file and os.path.exists(work.video_file):
            try:
                os.remove(work.video_file)
            except:
                pass
    db.query(Work).delete()
    db.commit()

    # 4. 删除队伍成员
    db.query(TeamMember).delete()
    db.commit()

    # 5. 删除队伍
    db.query(Team).delete()
    db.commit()

    # 6. 删除非admin用户
    admin_user = db.query(User).filter(User.username == "admin").first()
    admin_user_id = admin_user.id if admin_user else None
    db.query(User).filter(User.username != "admin").delete()
    db.commit()

    # 7. 删除日志
    db.query(Log).delete()
    db.commit()

    # 8. 恢复admin用户
    if admin_user_id:
        admin = db.query(User).filter(User.id == admin_user_id).first()
        if admin:
            admin.is_active = True
            admin.role = UserRole.ADMIN
            db.commit()

    return {"message": "数据清空完成，已保留admin账号、角色/权限、配置"}


# ============== 后续路由 ==============