"""
作品管理 API 路由
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_active_user_optional, require_role
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.team import Team, TeamMember, TeamStatus
from app.models.work import Work, Review, Vote, WorkStatus
from app.models.setting import Log, CompetitionTheme
from app.schemas.work import (
    WorkCreate, WorkUpdate, WorkResponse, WorkDetailResponse,
    ReviewCreate, ReviewUpdate, ReviewResponse, VoteRequest
)
from app.schemas.common import PageResponse
from app.services.webhook import trigger_webhook_and_notification
from app.models.webhook import WebhookEventType
import os
import aiofiles

router = APIRouter(prefix="/works", tags=["作品管理"])


def add_log(db: Session, user_id: int, action: str, resource: str = None,
            resource_id: int = None, details: str = None):
    """添加日志"""
    log = Log(user_id=user_id, action=action, resource=resource,
              resource_id=resource_id, details=details)
    db.add(log)
    db.commit()


def get_setting(db: Session, key: str, default=None):
    """获取配置"""
    from app.models.setting import Setting
    setting = db.query(Setting).filter(Setting.key == key).first()
    return setting.value if setting and setting.value else default


def get_user_total_votes(db: Session, user_id: int) -> int:
    """获取用户总投票数"""
    return db.query(Vote).filter(Vote.user_id == user_id).count()


def get_max_votes(db: Session) -> int:
    """获取最大投票数"""
    return int(get_setting(db, "max_votes", 5))


def get_max_works_per_team(db: Session) -> int:
    """获取每队最大作品数"""
    return int(get_setting(db, "max_works_per_team", 5))


def check_registration_open(db: Session) -> tuple:
    """检查报名是否开放，返回(是否开放, 错误信息)"""
    reg_start = get_setting(db, "registration_start")
    reg_end = get_setting(db, "registration_end")
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


def check_submission_open(db: Session) -> tuple:
    """检查作品提交是否开放，返回(是否开放, 错误信息)"""
    sub_start = get_setting(db, "submission_start")
    sub_end = get_setting(db, "submission_end")
    now = datetime.utcnow()

    if sub_start:
        try:
            start_time = datetime.fromisoformat(sub_start.replace('Z', '+00:00'))
            if now < start_time.replace(tzinfo=None):
                return (False, f"作品提交尚未开始，开始时间：{sub_start}")
        except:
            pass

    if sub_end:
        try:
            end_time = datetime.fromisoformat(sub_end.replace('Z', '+00:00'))
            if now > end_time.replace(tzinfo=None):
                return (False, f"作品提交已截止，结束时间：{sub_end}")
        except:
            pass

    return (True, "")


def check_voting_open(db: Session) -> tuple:
    """检查投票是否开放，返回(是否开放, 错误信息)"""
    vote_start = get_setting(db, "voting_start")
    vote_end = get_setting(db, "voting_end")
    now = datetime.utcnow()

    if vote_start:
        try:
            start_time = datetime.fromisoformat(vote_start.replace('Z', '+00:00'))
            if now < start_time.replace(tzinfo=None):
                return (False, f"投票尚未开始，开始时间：{vote_start}")
        except:
            pass

    if vote_end:
        try:
            end_time = datetime.fromisoformat(vote_end.replace('Z', '+00:00'))
            if now > end_time.replace(tzinfo=None):
                return (False, f"投票已结束，结束时间：{vote_end}")
        except:
            pass

    return (True, "")


async def save_upload_file(file: UploadFile, sub_dir: str, max_size: int) -> str:
    """保存上传文件"""
    # 检查文件大小
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > max_size:
        raise HTTPException(status_code=400, detail=f"文件大小超过限制 ({max_size // (1024*1024)}MB)")

    # 创建目录
    upload_dir = os.path.join(settings.UPLOAD_DIR, sub_dir)
    os.makedirs(upload_dir, exist_ok=True)

    # 生成文件名
    ext = os.path.splitext(file.filename)[1]
    filename = f"{datetime.utcnow().timestamp()}{ext}"
    filepath = os.path.join(upload_dir, filename)

    # 保存文件
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        await f.write(content)

    return filepath


@router.get("/voting-status")
async def get_voting_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的投票状态"""
    # 获取最大投票数（0表示不限制）
    max_votes = get_max_votes(db)

    # 获取总投票数
    total_votes = get_user_total_votes(db, current_user.id)

    # 获取已投票的作品列表
    voted_works = db.query(Vote).filter(Vote.user_id == current_user.id).all()
    voted_work_ids = [v.work_id for v in voted_works]

    # 获取作品详情
    voted_works_info = []
    if voted_work_ids:
        works = db.query(Work).filter(Work.id.in_(voted_work_ids)).all()
        for w in works:
            voted_works_info.append({
                "id": w.id,
                "name": w.name,
                "team_name": w.team.name if w.team else None
            })

    # 获取总作品数（仅已审核通过的作品）
    total_works = db.query(Work).filter(Work.status == "approved").count()

    # 计算剩余票数
    if max_votes == 0:
        remaining = "不限制"
    else:
        remaining = max(0, max_votes - total_votes)

    return {
        "max_votes": max_votes,
        "used_votes": total_votes,
        "remaining_votes": remaining,
        "voted_works": voted_works_info,
        "total_works": total_works,
        "voting_open": check_voting_open(db)[0]
    }


@router.get("", response_model=PageResponse)
async def get_works(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[WorkStatus] = None,
    team_name: Optional[str] = None,
    keyword: Optional[str] = None,
    theme_id: Optional[int] = Query(None, description="主题ID"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user_optional)
):
    """获取作品列表"""
    query = db.query(Work).join(Team).outerjoin(CompetitionTheme, Work.theme_id == CompetitionTheme.id)

    # 普通用户只能查看已通过的作品
    if not current_user or current_user.role == UserRole.USER:
        query = query.filter(Work.status == WorkStatus.APPROVED)
    # 管理员/审核员可以查看所有作品，不需要额外过滤

    if status:
        query = query.filter(Work.status == status)

    if team_name:
        query = query.filter(Team.name.contains(team_name))

    if keyword:
        query = query.filter(Work.name.contains(keyword))

    if theme_id:
        query = query.filter(Work.theme_id == theme_id)

    # 普通用户可以看到所有已审核通过的作品（不需要按队伍过滤）

    total = query.count()
    works = query.order_by(Work.vote_count.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for w in works:
        item = WorkResponse.model_validate(w).model_dump()
        item["team_name"] = w.team.name
        # 获取主题名称
        if w.theme_id and w.theme_obj:
            item["theme_name"] = w.theme_obj.name
        items.append(item)

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{work_id}", response_model=WorkDetailResponse)
async def get_work(
    work_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user_optional)
):
    """获取作品详情"""
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

    # 普通用户只能查看已通过的作品
    if current_user and current_user.role == UserRole.USER and work.status != WorkStatus.APPROVED:
        raise HTTPException(status_code=403, detail="作品未通过审核")

    team = work.team
    from app.schemas.team import TeamMemberResponse
    members = [TeamMemberResponse.model_validate(m) for m in team.members]

    response = WorkDetailResponse(
        **WorkResponse.model_validate(work).model_dump(),
        team_name=team.name,
        team_members=members
    )
    return response


@router.post("", response_model=WorkResponse)
async def create_work(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    theme_id: int = Form(..., description="主题方向ID"),
    team_id: Optional[int] = Form(None),
    agent_url: str = Form(..., description="发布后的智能体URL，如 https://agent.ynu.edu.cn/product/llm/chat/<publish_id>"),
    agent_editor_url: str = Form(..., description="智能体编排URL，如 https://agent.ynu.edu.cn/product/llm/personal/<space_id>/application/<app_id>/arrange"),
    pdf_file: Optional[UploadFile] = File(..., description="PDF文档"),
    video_file: Optional[UploadFile] = File(..., description="演示视频"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """提交作品"""
    # 检查作品提交是否开放
    sub_open, sub_msg = check_submission_open(db)
    if not sub_open:
        raise HTTPException(status_code=400, detail=f"作品提交：{sub_msg}")

    # 检查用户是否有队伍
    member = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.username,
        TeamMember.is_leader == True
    ).first()

    if not member:
        raise HTTPException(status_code=400, detail="只有队长可以提交作品")

    # 使用传入的team_id或当前用户的队伍
    team = None
    if team_id:
        team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        team = db.query(Team).filter(Team.id == member.team_id).first()
    if team.status != TeamStatus.APPROVED:
        raise HTTPException(status_code=400, detail="队伍未通过审核")

    # 检查作品数量限制
    max_works = get_max_works_per_team(db)
    work_count = db.query(Work).filter(Work.team_id == team.id).count()
    if work_count >= max_works:
        raise HTTPException(status_code=400, detail=f"每队最多{max_works}个作品")

    # 检查主题是否重复（同一队伍不能提交相同主题的作品）
    if theme_id:
        existing_with_theme = db.query(Work).filter(
            Work.team_id == team.id,
            Work.theme_id == theme_id
        ).first()
        if existing_with_theme:
            raise HTTPException(status_code=400, detail="该队伍已提交过相同主题的作品")

    # 保存文件
    pdf_path = None
    video_path = None

    if pdf_file:
        pdf_path = await save_upload_file(pdf_file, "pdf", settings.MAX_PDF_SIZE)

    if video_file:
        video_path = await save_upload_file(video_file, "video", settings.MAX_VIDEO_SIZE)

    # 创建作品
    # 管理员/评审提交时自动通过审核，普通用户需要审核
    is_admin_or_reviewer = current_user.role in [UserRole.ADMIN, UserRole.REVIEWER]
    work_status = WorkStatus.APPROVED if is_admin_or_reviewer else WorkStatus.PENDING

    # 管理员可以不上传文件
    if not is_admin_or_reviewer:
        if not pdf_file:
            raise HTTPException(status_code=400, detail="请上传PDF文档")
        if not video_file:
            raise HTTPException(status_code=400, detail="请上传演示视频")

    work = Work(
        team_id=team.id,
        theme_id=theme_id,
        name=name,
        description=description,
        agent_url=agent_url,
        agent_editor_url=agent_editor_url,
        pdf_file=pdf_path,
        video_file=video_path,
        status=work_status
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    add_log(db, current_user.id, "create", "work", work.id, f"提交作品: {work.name}")

    response = WorkResponse.model_validate(work)

    # 触发 Webhook
    await trigger_webhook_and_notification(db, WebhookEventType.WORK_CREATED, {
        "id": work.id,
        "name": work.name,
        "description": work.description,
        "team_id": work.team_id,
        "theme_id": work.theme_id,
        "status": work.status.value if hasattr(work.status, 'value') else work.status
    }, "created")

    return response


@router.put("/{work_id}", response_model=WorkResponse)
async def update_work(
    work_id: int,
    work_data: WorkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新作品信息"""
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

    # 检查权限
    team = work.team
    is_leader = any(m.user_id == current_user.id and m.is_leader for m in team.members)
    is_admin_or_reviewer = current_user.role in [UserRole.ADMIN, UserRole.REVIEWER]

    if not is_leader and not is_admin_or_reviewer:
        raise HTTPException(status_code=403, detail="权限不足")

    update_data = work_data.model_dump(exclude_unset=True)

    # 处理无效的theme_id（0或空）
    if 'theme_id' in update_data and update_data['theme_id'] is not None:
        if update_data['theme_id'] == 0:
            update_data['theme_id'] = None

    # 只有管理员可以修改状态
    if current_user.role != UserRole.ADMIN:
        update_data.pop("status", None)

    for key, value in update_data.items():
        setattr(work, key, value)

    db.commit()
    db.refresh(work)

    add_log(db, current_user.id, "update", "work", work.id, f"更新作品: {work.name}")

    response = WorkResponse.model_validate(work)

    # 触发 Webhook
    await trigger_webhook_and_notification(db, WebhookEventType.WORK_UPDATED, {
        "id": work.id,
        "name": work.name,
        "description": work.description,
        "team_id": work.team_id,
        "theme_id": work.theme_id,
        "status": work.status.value if hasattr(work.status, 'value') else work.status,
        "updated_fields": list(update_data.keys())
    }, "updated")

    return response


@router.delete("/{work_id}")
async def delete_work(
    work_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除作品"""
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

    # 检查权限
    team = work.team
    is_leader = any(m.user_id == current_user.id and m.is_leader for m in team.members)

    if not is_leader and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")

    work_name = work.name
    work_data = {
        "id": work.id,
        "name": work.name,
        "team_id": work.team_id
    }

    # 删除文件
    if work.pdf_file and os.path.exists(work.pdf_file):
        os.remove(work.pdf_file)
    if work.video_file and os.path.exists(work.video_file):
        os.remove(work.video_file)

    db.delete(work)
    db.commit()

    add_log(db, current_user.id, "delete", "work", work_id, f"删除作品: {work_name}")

    # 触发 Webhook
    await trigger_webhook_and_notification(db, WebhookEventType.WORK_DELETED, work_data, "deleted")

    return {"message": "删除成功"}


@router.post("/{work_id}/vote")
async def vote_work(
    work_id: int,
    vote_data: VoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """投票"""
    # 检查投票是否开放
    voting_open, voting_msg = check_voting_open(db)
    if not voting_open:
        raise HTTPException(status_code=400, detail=f"投票未开放：{voting_msg}")

    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

    if work.status != WorkStatus.APPROVED:
        raise HTTPException(status_code=400, detail="作品未通过审核")

    # 检查投票数限制
    max_votes = get_max_votes(db)
    total_votes = get_user_total_votes(db, current_user.id)

    if max_votes > 0 and total_votes >= max_votes:
        raise HTTPException(status_code=400, detail=f"投票次数已用完（最多{max_votes}票）")

    # 检查是否已投过
    existing_vote = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.work_id == work_id
    ).first()

    if existing_vote:
        raise HTTPException(status_code=400, detail="您已为该作品投票")

    # 投票
    vote = Vote(user_id=current_user.id, work_id=work_id)
    db.add(vote)

    work.vote_count += 1
    db.commit()

    add_log(db, current_user.id, "vote", "work", work_id, f"投票: {work.name}")

    # 触发 Webhook
    await trigger_webhook_and_notification(db, WebhookEventType.VOTE_CREATED, {
        "id": vote.id,
        "work_id": work_id,
        "work_name": work.name,
        "user_id": current_user.id
    }, "vote_created")

    return {"message": "投票成功", "vote_count": work.vote_count}


@router.get("/voting-status")
async def get_voting_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的投票状态"""
    # 获取最大投票数（0表示不限制）
    max_votes = get_max_votes(db)

    # 获取总投票数
    total_votes = get_user_total_votes(db, current_user.id)

    # 获取已投票的作品列表
    voted_works = db.query(Vote).filter(Vote.user_id == current_user.id).all()
    voted_work_ids = [v.work_id for v in voted_works]

    # 获取作品详情
    voted_works_info = []
    if voted_work_ids:
        works = db.query(Work).filter(Work.id.in_(voted_work_ids)).all()
        for w in works:
            voted_works_info.append({
                "id": w.id,
                "name": w.name,
                "team_name": w.team.name if w.team else None
            })

    # 获取总作品数（仅已审核通过的作品）
    total_works = db.query(Work).filter(Work.status == "approved").count()

    # 计算剩余票数
    if max_votes == 0:
        remaining = "不限制"
    else:
        remaining = max(0, max_votes - total_votes)

    return {
        "max_votes": max_votes,
        "used_votes": total_votes,
        "remaining_votes": remaining,
        "voted_works": voted_works_info,
        "total_works": total_works,
        "voting_open": check_voting_open(db)[0]
    }


@router.get("/my/works", response_model=PageResponse)
async def get_my_works(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取我的作品"""
    member = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.username,
        TeamMember.is_leader == True
    ).first()

    if not member:
        return PageResponse(total=0, page=page, page_size=page_size, items=[])

    query = db.query(Work).filter(Work.team_id == member.team_id)
    total = query.count()
    works = query.offset((page - 1) * page_size).limit(page_size).all()

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[WorkResponse.model_validate(w) for w in works]
    )


@router.get("/admin/list", response_model=PageResponse)
async def get_works_for_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[WorkStatus] = None,
    team_name: Optional[str] = None,
    keyword: Optional[str] = None,
    theme_id: Optional[int] = Query(None, description="主题ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """后台作品列表 - 管理员/审核员看全部，普通用户只能看自己队伍的作品"""
    query = db.query(Work).join(Team).outerjoin(CompetitionTheme, Work.theme_id == CompetitionTheme.id)

    # 权限校验：普通用户只能看自己队伍的作品
    if current_user.role == UserRole.USER:
        user_team_ids = db.query(TeamMember.team_id).filter(
            TeamMember.user_id == current_user.username
        ).all()
        team_ids = [t[0] for t in user_team_ids]
        if team_ids:
            query = query.filter(Work.team_id.in_(team_ids))
        else:
            return PageResponse(total=0, page=page, page_size=page_size, items=[])
    # 管理员/审核员可以看所有作品，不需要额外过滤

    if status:
        query = query.filter(Work.status == status)

    if team_name:
        query = query.filter(Team.name.contains(team_name))

    if keyword:
        query = query.filter(Work.name.contains(keyword))

    if theme_id:
        query = query.filter(Work.theme_id == theme_id)

    total = query.count()
    works = query.order_by(Work.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for w in works:
        item = WorkResponse.model_validate(w).model_dump()
        item["team_name"] = w.team.name
        item["team_leader_id"] = w.team.leader_id  # 添加队长ID用于前端权限判断
        if w.theme_id and w.theme_obj:
            item["theme_name"] = w.theme_obj.name
        items.append(item)

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )