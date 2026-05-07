"""
队伍管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.team import Team, TeamMember, TeamStatus
from app.models.setting import Log
from app.schemas.team import (
    TeamCreate, TeamUpdate, TeamResponse, TeamAuditRequest,
    JoinTeamRequest, TeamMemberResponse
)
from app.schemas.common import PageResponse

router = APIRouter(prefix="/teams", tags=["队伍管理"])


def get_setting(db: Session, key: str) -> str:
    """获取配置"""
    setting = db.query(Log).filter(Log.action == key).first()
    return None


def add_log(db: Session, user_id: int, action: str, resource: str = None,
            resource_id: int = None, details: str = None):
    """添加日志"""
    log = Log(user_id=user_id, action=action, resource=resource,
              resource_id=resource_id, details=details)
    db.add(log)
    db.commit()


def get_max_team_members(db: Session) -> int:
    """获取队伍最大成员数"""
    from app.models.setting import Setting
    setting = db.query(Setting).filter(Setting.key == "max_team_members").first()
    return int(setting.value) if setting and setting.value else 5


def check_registration_open(db: Session) -> tuple:
    """检查报名是否开放，返回(是否开放, 错误信息)"""
    from datetime import datetime
    from app.models.setting import Setting

    setting_start = db.query(Setting).filter(Setting.key == "registration_start").first()
    setting_end = db.query(Setting).filter(Setting.key == "registration_end").first()

    reg_start = setting_start.value if setting_start and setting_start.value else None
    reg_end = setting_end.value if setting_end and setting_end.value else None
    now = datetime.utcnow()

    if reg_start:
        try:
            start_time = datetime.fromisoformat(reg_start.replace('Z', '+00:00'))
            if now < start_time.replace(tzinfo=None):
                return (False, f"报名尚未开始，开始时间：{reg_start}")
        except:
            pass

    if reg_end:
        try:
            end_time = datetime.fromisoformat(reg_end.replace('Z', '+00:00'))
            if now > end_time.replace(tzinfo=None):
                return (False, f"报名已结束，结束时间：{reg_end}")
        except:
            pass

    return (True, "")


@router.get("", response_model=PageResponse)
async def get_teams(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[TeamStatus] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取队伍列表"""
    query = db.query(Team)

    # 普通用户只能看到自己和所在队伍
    if current_user.role == UserRole.USER:
        user_team_ids = db.query(TeamMember.team_id).filter(
            TeamMember.user_id == current_user.id
        ).all()
        team_ids = [t[0] for t in user_team_ids]
        if team_ids:
            query = query.filter(Team.id.in_(team_ids))
        else:
            return PageResponse(total=0, page=page, page_size=page_size, items=[])

    if status:
        query = query.filter(Team.status == status)

    if keyword:
        query = query.filter(Team.name.contains(keyword))

    total = query.count()
    teams = query.order_by(Team.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 获取成员信息
    result = []
    for team in teams:
        team_data = TeamResponse.model_validate(team)
        team_data.members = [TeamMemberResponse.model_validate(m) for m in team.members]
        result.append(team_data)

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=result
    )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取队伍详情"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")

    team_data = TeamResponse.model_validate(team)
    team_data.members = [TeamMemberResponse.model_validate(m) for m in team.members]
    return team_data


@router.post("", response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建队伍（普通用户）"""
    # 检查报名是否开放
    reg_open, reg_msg = check_registration_open(db)
    if not reg_open:
        raise HTTPException(status_code=400, detail=f"创建队伍：{reg_msg}")

    # 检查队伍名是否已存在
    if db.query(Team).filter(Team.name == team_data.name).first():
        raise HTTPException(status_code=400, detail="队伍名已存在")

    # 检查成员数量限制
    max_members = get_max_team_members(db)
    if len(team_data.members) > max_members:
        raise HTTPException(status_code=400, detail=f"队伍最多{max_members}名成员")

    # 检查用户是否已加入其他队伍
    existing = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已加入其他队伍")

    # 创建队伍
    team = Team(
        name=team_data.name,
        description=team_data.description,
        leader_id=current_user.id
    )
    db.add(team)
    db.commit()
    db.refresh(team)

    # 添加成员
    for i, member_data in enumerate(team_data.members):
        member = TeamMember(
            team_id=team.id,
            user_id=current_user.id if i == 0 else None,
            student_id=member_data.student_id,
            name=member_data.name,
            is_leader=member_data.is_leader or (i == 0)
        )
        db.add(member)

    db.commit()
    db.refresh(team)

    add_log(db, current_user.id, "create", "team", team.id, f"创建队伍: {team.name}")

    team_response = TeamResponse.model_validate(team)
    team_response.members = [TeamMemberResponse.model_validate(m) for m in team.members]
    return team_response


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新队伍信息"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")

    # 只有队长或管理员可以更新
    if team.leader_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
        raise HTTPException(status_code=403, detail="只有队长或管理员可以修改队伍信息")

    # 更新字段
    update_data = team_data.model_dump(exclude_unset=True)

    # 非管理员不能修改状态
    if current_user.role != UserRole.ADMIN:
        update_data.pop("status", None)

    for key, value in update_data.items():
        setattr(team, key, value)

    db.commit()
    db.refresh(team)

    add_log(db, current_user.id, "update", "team", team.id, f"更新队伍: {team.name}")

    team_response = TeamResponse.model_validate(team)
    team_response.members = [TeamMemberResponse.model_validate(m) for m in team.members]
    return team_response


@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除队伍"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")

    # 只有队长或管理员可以删除
    if team.leader_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="只有队长或管理员可以删除队伍")

    team_name = team.name
    db.delete(team)
    db.commit()

    add_log(db, current_user.id, "delete", "team", team_id, f"删除队伍: {team_name}")

    return {"message": "删除成功"}


@router.post("/{team_id}/join", response_model=TeamResponse)
async def join_team(
    team_id: int,
    join_data: JoinTeamRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """加入队伍"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")

    # 检查成员数量限制
    max_members = get_max_team_members(db)
    if len(team.members) >= max_members:
        raise HTTPException(status_code=400, detail="队伍人数已满")

    # 检查用户是否已加入其他队伍
    existing = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已加入其他队伍")

    # 检查成员学工号是否重复
    for member in team.members:
        if member.student_id == join_data.student_id:
            raise HTTPException(status_code=400, detail="该学工号已在队伍中")

    # 添加成员
    member = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        student_id=join_data.student_id,
        name=join_data.name,
        is_leader=False
    )
    db.add(member)
    db.commit()
    db.refresh(team)

    add_log(db, current_user.id, "join", "team", team.id, f"加入队伍: {team.name}")

    team_response = TeamResponse.model_validate(team)
    team_response.members = [TeamMemberResponse.model_validate(m) for m in team.members]
    return team_response


@router.put("/{team_id}/audit", response_model=TeamResponse)
async def audit_team(
    team_id: int,
    audit_data: TeamAuditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """审核队伍（评审/管理员）"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")

    team.status = audit_data.status
    db.commit()
    db.refresh(team)

    add_log(db, current_user.id, "audit", "team", team.id,
            f"审核队伍: {team.name}, 状态: {audit_data.status}")

    team_response = TeamResponse.model_validate(team)
    team_response.members = [TeamMemberResponse.model_validate(m) for m in team.members]
    return team_response


@router.get("/my/team", response_model=TeamResponse)
async def get_my_team(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取我的队伍"""
    member = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="您还未加入任何队伍")

    team = db.query(Team).filter(Team.id == member.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")

    team_response = TeamResponse.model_validate(team)
    team_response.members = [TeamMemberResponse.model_validate(m) for m in team.members]
    return team_response