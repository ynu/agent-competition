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
from app.services.webhook import trigger_webhook_and_notification
from app.models.webhook import WebhookEventType

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

    # 普通用户只能看到自己是队长的队伍
    if current_user.role == UserRole.USER:
        # 根据当前用户的 username（学工号）查找队长的队伍
        leader_member = db.query(TeamMember).filter(
            TeamMember.user_id == current_user.username,
            TeamMember.is_leader == True
        ).first()

        if leader_member:
            query = query.filter(Team.id == leader_member.team_id)
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

    # 检查用户是否已创建/加入其他队伍（每人只能创建一个队伍）
    existing_membership = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).first()
    if existing_membership:
        raise HTTPException(status_code=400, detail="您已加入其他队伍，不能再创建新队伍")

    # 检查用户是否已创建过队伍（作为队长）
    existing_leader = db.query(Team).filter(Team.leader_id == current_user.id).first()
    if existing_leader:
        raise HTTPException(status_code=400, detail="您已经是队长，不能再创建新队伍")

    # 检查队员是否已在其他队伍
    if team_data.members:
        for member_data in team_data.members:
            if member_data.is_leader:
                continue
            # 检查学工号是否已在其他队伍
            existing_in_team = db.query(TeamMember).filter(
                TeamMember.student_id == member_data.student_id
            ).first()
            if existing_in_team:
                team = db.query(Team).filter(Team.id == existing_in_team.team_id).first()
                team_name = team.name if team else "其他队伍"
                raise HTTPException(
                    status_code=400,
                    detail=f"学工号 {member_data.student_id} 已在队伍 \"{team_name}\" 中"
                )

    # 检查成员数量限制
    max_members = get_max_team_members(db)
    member_count = len(team_data.members) if team_data.members else 1
    if member_count > max_members:
        raise HTTPException(status_code=400, detail=f"队伍最多{max_members}名成员")

    # 创建队伍
    team = Team(
        name=team_data.name,
        description=team_data.description,
        leader_id=current_user.id,
        status=TeamStatus.APPROVED  # 默认审核通过
    )
    db.add(team)
    db.commit()
    db.refresh(team)

    # 添加队长（当前用户）- user_id 默认等于 student_id
    leader_member = TeamMember(
        team_id=team.id,
        user_id=current_user.username,  # 默认等于学工号
        student_id=current_user.username,
        name=current_user.nickname or current_user.username,
        is_leader=True
    )
    db.add(leader_member)

    # 如果有其他成员数据，添加其他成员（不包含队长）
    if team_data.members:
        for member_data in team_data.members:
            # 跳过队长（由系统自动添加）
            if member_data.is_leader:
                continue
            member = TeamMember(
                team_id=team.id,
                user_id=member_data.student_id,  # 默认等于学工号
                student_id=member_data.student_id,
                name=member_data.name,
                is_leader=False
            )
            db.add(member)

    db.commit()
    db.refresh(team)

    add_log(db, current_user.id, "create", "team", team.id, f"创建队伍: {team.name}")

    team_response = TeamResponse.model_validate(team)
    team_response.members = [TeamMemberResponse.model_validate(m) for m in team.members]

    # 触发 Webhook
    await trigger_webhook_and_notification(db, WebhookEventType.TEAM_CREATED, {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "leader_id": team.leader_id,
        "status": team.status.value if hasattr(team.status, 'value') else team.status
    }, "created")

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

    # 更新字段（排除 members）
    update_data = team_data.model_dump(exclude_unset=True)
    update_data.pop("members", None)

    # 非管理员不能修改状态
    if current_user.role != UserRole.ADMIN:
        update_data.pop("status", None)

    for key, value in update_data.items():
        setattr(team, key, value)

    # 处理队员更新（跳过队长，删除其他队员，添加新队员）
    if team_data.members is not None:
        # 删除除队长外的所有队员
        db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.is_leader == False
        ).delete()

        # 检查新队员是否在其他队伍
        for member_data in team_data.members:
            existing_in_team = db.query(TeamMember).filter(
                TeamMember.student_id == member_data.student_id,
                TeamMember.team_id != team_id
            ).first()
            if existing_in_team:
                other_team = db.query(Team).filter(Team.id == existing_in_team.team_id).first()
                team_name = other_team.name if other_team else "其他队伍"
                raise HTTPException(
                    status_code=400,
                    detail=f"学工号 {member_data.student_id} 已在队伍 \"{team_name}\" 中"
                )

        # 添加新队员（不包含队长）
        for member_data in team_data.members:
            if member_data.is_leader:
                continue
            member = TeamMember(
                team_id=team_id,
                user_id=member_data.student_id,  # 默认等于学工号
                student_id=member_data.student_id,
                name=member_data.name,
                is_leader=False
            )
            db.add(member)

    db.commit()
    db.refresh(team)

    add_log(db, current_user.id, "update", "team", team.id, f"更新队伍: {team.name}")

    team_response = TeamResponse.model_validate(team)
    team_response.members = [TeamMemberResponse.model_validate(m) for m in team.members]

    # 触发 Webhook
    await trigger_webhook_and_notification(db, WebhookEventType.TEAM_UPDATED, {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "leader_id": team.leader_id,
        "status": team.status.value if hasattr(team.status, 'value') else team.status,
        "updated_fields": list(update_data.keys())
    }, "updated")

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

    # 检查队伍下是否有审核通过的作品
    from app.models.work import Work, WorkStatus
    approved_works = db.query(Work).filter(
        Work.team_id == team_id,
        Work.status == WorkStatus.APPROVED
    ).count()
    if approved_works > 0:
        raise HTTPException(status_code=400, detail="该队伍有待审核通过的作品，无法删除")

    # 检查队伍下是否有其他作品（待审核/已拒绝的）
    other_works = db.query(Work).filter(
        Work.team_id == team_id,
        Work.status != WorkStatus.APPROVED
    ).count()
    if other_works > 0 and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="该队伍有待审核的作品，请先处理后再删除")

    team_name = team.name

    # 先删除队伍的所有队员
    db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()

    # 再删除队伍
    team_data = {
        "id": team.id,
        "name": team.name,
        "leader_id": team.leader_id
    }
    db.delete(team)
    db.commit()

    add_log(db, current_user.id, "delete", "team", team_id, f"删除队伍: {team_name}")

    # 触发 Webhook（删除后触发，数据已保存）
    await trigger_webhook_and_notification(db, WebhookEventType.TEAM_DELETED, team_data, "deleted")

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

    # 触发 Webhook
    await trigger_webhook_and_notification(db, WebhookEventType.TEAM_MEMBER_ADDED, {
        "team_id": team.id,
        "team_name": team.name,
        "member": {
            "id": member.id,
            "user_id": member.user_id,
            "student_id": member.student_id,
            "name": member.name
        }
    }, "member_added")

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