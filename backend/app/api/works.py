"""
作品管理 API 路由
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Request, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_active_user_optional, require_role, get_user_from_token
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.team import Team, TeamMember, TeamStatus
from app.models.work import Work, Review, Vote, WorkStatus
from app.models.setting import Log, CompetitionTheme
from app.schemas.work import (
    WorkCreate, WorkUpdate, WorkResponse, WorkDetailResponse,
    ReviewCreate, ReviewUpdate, ReviewResponse, VoteRequest,
    CopyrightAgreementCreate, CopyrightAgreementResponse
)
from app.schemas.common import PageResponse
from app.services.webhook import trigger_webhook_and_notification
from app.models.webhook import WebhookEventType
from app.models.work import CopyrightAgreement
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


def get_copyright_agreement(db: Session) -> str:
    """获取版权协议内容"""
    return get_setting(db, "copyright_agreement", "") or ""


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

    # # 普通用户只能查看已通过的作品
    # if not current_user or current_user.role == UserRole.USER:
    #     query = query.filter(Work.status == WorkStatus.APPROVED)
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


@router.get("/{work_id:int}", response_model=WorkDetailResponse)
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

    # 检查是否已签署版权协议
    existing_agreement = db.query(CopyrightAgreement).filter(
        CopyrightAgreement.user_id == current_user.id
    ).first()

    if not existing_agreement:
        raise HTTPException(
            status_code=400,
            detail="请先签署版权协议才能提交作品"
        )

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

    # 检查权限 - 队长或管理员可以更新
    team = work.team
    # 队长权限：team.leader_id 存储的是用户的数字 id
    is_leader = team.leader_id == current_user.id
    is_admin_or_reviewer = current_user.role in [UserRole.ADMIN, UserRole.REVIEWER]

    # 作品提交截止前，队长可以更新自己的作品
    # 检查作品提交是否还在开放时间内
    sub_open, _ = check_submission_open(db)
    if not is_leader and not is_admin_or_reviewer:
        raise HTTPException(status_code=403, detail="权限不足")

    # 如果作品提交已截止，只有管理员可以更新
    if not sub_open and not is_admin_or_reviewer:
        raise HTTPException(status_code=403, detail="作品提交已截止，只有管理员可以修改")

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

    # 检查权限 - 队长或管理员可以删除
    team = work.team
    is_leader = team.leader_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN

    if not is_leader and not is_admin:
        raise HTTPException(status_code=403, detail="权限不足")

    # 作品提交截止前，队长可以删除自己的作品
    sub_open, _ = check_submission_open(db)
    # 如果作品提交已截止，只有管理员可以删除
    if not sub_open and not is_admin:
        raise HTTPException(status_code=403, detail="作品提交已截止，只有管理员可以删除")

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

    # 如果 max_votes 是 0，表示不限制投票次数
    if max_votes != 0 and total_votes >= max_votes:
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
        # 添加队长信息
        leader = db.query(User).filter(User.id == w.team.leader_id).first()
        if leader:
            item["leader_name"] = leader.nickname or leader.username
            item["leader_username"] = leader.username
            if current_user.role == UserRole.ADMIN:
                has_agreed = db.query(CopyrightAgreement).filter(
                    CopyrightAgreement.user_id == leader.id
                ).first() is not None
                item["leader_has_copyright_agreement"] = has_agreed
        else:
            item["leader_name"] = None
            item["leader_username"] = None
        if w.theme_id and w.theme_obj:
            item["theme_name"] = w.theme_obj.name
        items.append(item)

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/copyright-agreement/check")
async def check_copyright_agreement(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """检查用户是否已签署版权协议"""
    # 检查是否已有签署记录
    existing = db.query(CopyrightAgreement).filter(
        CopyrightAgreement.user_id == current_user.id
    ).order_by(CopyrightAgreement.created_at.desc()).first()

    return {
        "has_agreed": existing is not None,
        "last_signed_at": existing.created_at.isoformat() if existing else None,
        "agreement_content": get_copyright_agreement(db)
    }


@router.post("/copyright-agreement", response_model=CopyrightAgreementResponse)
async def sign_copyright_agreement(
    agreement_data: CopyrightAgreementCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """签署版权协议"""
    # 检查是否已有签署记录
    existing = db.query(CopyrightAgreement).filter(
        CopyrightAgreement.user_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="您已经签署过版权协议，无需重复签署"
        )

    # 获取客户端IP和User-Agent
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500] if request.headers else ""

    # 创建签署记录
    agreement = CopyrightAgreement(
        user_id=current_user.id,
        signature_data=agreement_data.signature_data,
        signature_name=agreement_data.signature_name or current_user.nickname or current_user.username,
        ip_address=client_ip,
        user_agent=user_agent,
        agreement_content=get_copyright_agreement(db)
    )

    db.add(agreement)
    db.commit()
    db.refresh(agreement)

    add_log(db, current_user.id, "sign_copyright", "copyright_agreement", agreement.id, "签署版权协议")

    return agreement


@router.get("/copyright-agreements", response_model=PageResponse)
async def get_copyright_agreements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: Optional[str] = Query(None, description="用户名搜索"),
    team_name: Optional[str] = Query(None, description="队伍名称搜索"),
    start_date: Optional[str] = Query(None, description="开始时间 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束时间 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取版权协议签署记录列表（仅管理员）"""
    if current_user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
        raise HTTPException(status_code=403, detail="权限不足")

    # 基础查询
    query = db.query(CopyrightAgreement).join(User, CopyrightAgreement.user_id == User.id)

    # 搜索条件
    if username:
        query = query.filter(User.username.contains(username) | User.nickname.contains(username))

    if team_name:
        query = query.join(TeamMember, TeamMember.user_id == User.username)
        query = query.join(Team, Team.id == TeamMember.team_id)
        query = query.filter(Team.name.contains(team_name))

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(CopyrightAgreement.created_at >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            end = end.replace(hour=23, minute=59, second=59)
            query = query.filter(CopyrightAgreement.created_at <= end)
        except ValueError:
            pass

    total = query.count()
    agreements = query.order_by(CopyrightAgreement.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for a in agreements:
        user = db.query(User).filter(User.id == a.user_id).first()
        team_name_val = None
        if user:
            member = db.query(TeamMember).filter(TeamMember.user_id == user.username).first()
            if member:
                team = db.query(Team).filter(Team.id == member.team_id).first()
                if team:
                    team_name_val = team.name

        items.append({
            "id": a.id,
            "user_id": a.user_id,
            "username": user.nickname if user else str(a.user_id),
            "team_name": team_name_val,
            "signature_name": a.signature_name,
            "signature_data": a.signature_data,
            "ip_address": a.ip_address,
            "user_agent": a.user_agent,
            "agreement_content": a.agreement_content[:100] + "..." if len(a.agreement_content) > 100 else a.agreement_content,
            "created_at": a.created_at
        })

    return PageResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/copyright-agreements/{agreement_id}", response_model=dict)
async def get_copyright_agreement_detail(
    agreement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取版权协议签署详情"""
    if current_user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
        raise HTTPException(status_code=403, detail="权限不足")

    agreement = db.query(CopyrightAgreement).filter(CopyrightAgreement.id == agreement_id).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="签署记录不存在")

    user = db.query(User).filter(User.id == agreement.user_id).first()
    team_name_val = None
    if user:
        member = db.query(TeamMember).filter(TeamMember.user_id == user.username).first()
        if member:
            team = db.query(Team).filter(Team.id == member.team_id).first()
            if team:
                team_name_val = team.name

    return {
        "id": agreement.id,
        "user_id": agreement.user_id,
        "username": user.nickname if user else str(agreement.user_id),
        "team_name": team_name_val,
        "signature_name": agreement.signature_name,
        "signature_data": agreement.signature_data,
        "ip_address": agreement.ip_address,
        "user_agent": agreement.user_agent,
        "agreement_content": agreement.agreement_content,
        "created_at": agreement.created_at.isoformat()
    }


@router.get("/copyright-agreements/export")
async def export_copyright_agreements(
    username: Optional[str] = Query(None, description="用户名搜索"),
    team_name: Optional[str] = Query(None, description="队伍名称搜索"),
    start_date: Optional[str] = Query(None, description="开始时间 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束时间 (YYYY-MM-DD)"),
    request: Request = None,
    db: Session = Depends(get_db),
):
    """导出版权协议签署记录（仅管理员）"""
    # 支持从 query token 或 header 认证
    auth_header = request.headers.get("Authorization") if request else None
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
    else:
        token = request.query_params.get("token") if request else None

    current_user = get_user_from_token(token, db) if token else None
    if not current_user:
        raise HTTPException(status_code=401, detail="无效的认证凭据")
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅管理员可导出")

    query = db.query(CopyrightAgreement).join(User, CopyrightAgreement.user_id == User.id)

    if username:
        query = query.filter(User.username.contains(username) | User.nickname.contains(username))

    if team_name:
        query = query.join(TeamMember, TeamMember.user_id == User.username)
        query = query.join(Team, Team.id == TeamMember.team_id)
        query = query.filter(Team.name.contains(team_name))

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(CopyrightAgreement.created_at >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            end = end.replace(hour=23, minute=59, second=59)
            query = query.filter(CopyrightAgreement.created_at <= end)
        except ValueError:
            pass

    agreements = query.order_by(CopyrightAgreement.created_at.desc()).all()

    try:
        from openpyxl import Workbook
        from io import BytesIO

        wb = Workbook()
        ws = wb.active
        ws.title = "版权协议签署记录"

        headers = ["用户名", "队伍名称", "签名人", "签署时间", "IP地址", "User-Agent"]
        ws.append(headers)

        for a in agreements:
            user = db.query(User).filter(User.id == a.user_id).first()
            team_name_val = None
            if user:
                member = db.query(TeamMember).filter(TeamMember.user_id == user.username).first()
                if member:
                    team = db.query(Team).filter(Team.id == member.team_id).first()
                    if team:
                        team_name_val = team.name

            ws.append([
                user.nickname if user else str(a.user_id),
                team_name_val or "-",
                a.signature_name or "-",
                a.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                a.ip_address or "-",
                a.user_agent or "-"
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        from fastapi.responses import StreamingResponse
        import io

        return StreamingResponse(
            io.BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=copyright_agreements.xlsx"}
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="Excel导出功能需要安装 openpyxl")


@router.get("/admin/export")
async def export_works(
    status: Optional[WorkStatus] = None,
    team_name: Optional[str] = None,
    keyword: Optional[str] = None,
    theme_id: Optional[int] = Query(None, description="主题ID"),
    request: Request = None,
    db: Session = Depends(get_db),
):
    """导出台作品列表（仅管理员）"""
    # 支持从 query token 或 header 认证
    auth_header = request.headers.get("Authorization") if request else None
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
    else:
        token = request.query_params.get("token") if request else None

    current_user = get_user_from_token(token, db) if token else None
    if not current_user:
        raise HTTPException(status_code=401, detail="无效的认证凭据")
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅管理员可导出")

    query = db.query(Work).join(Team).outerjoin(CompetitionTheme, Work.theme_id == CompetitionTheme.id)

    if status:
        query = query.filter(Work.status == status)

    if team_name:
        query = query.filter(Team.name.contains(team_name))

    if keyword:
        query = query.filter(Work.name.contains(keyword))

    if theme_id:
        query = query.filter(Work.theme_id == theme_id)

    works = query.order_by(Work.created_at.desc()).all()

    try:
        from openpyxl import Workbook
        from io import BytesIO

        wb = Workbook()
        ws = wb.active
        ws.title = "作品列表"

        headers = ["作品名称", "队伍", "队长姓名", "队长学工号", "主题", "投票数", "评分", "状态", "创建时间"]
        ws.append(headers)

        status_map = {"pending": "待审核", "approved": "已通过", "rejected": "已拒绝"}

        for w in works:
            leader = db.query(User).filter(User.id == w.team.leader_id).first()
            leader_name = leader.nickname if leader else "-"
            leader_username = leader.username if leader else "-"

            ws.append([
                w.name,
                w.team.name,
                leader_name,
                leader_username,
                w.theme_obj.name if w.theme_obj else "-",
                w.vote_count,
                w.score if w.score else "-",
                status_map.get(w.status.value if hasattr(w.status, 'value') else w.status, w.status),
                w.created_at.strftime("%Y-%m-%d %H:%M:%S") if w.created_at else "-"
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        from fastapi.responses import StreamingResponse
        import io

        return StreamingResponse(
            io.BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=works.xlsx"}
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="Excel导出功能需要安装 openpyxl")