"""
日志管理 API 路由
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.setting import Log
from app.models.team import Team, TeamMember
from app.models.work import Work, Vote
from app.schemas.common import LogResponse, PageResponse

router = APIRouter(prefix="/logs", tags=["日志管理"])


@router.get("", response_model=PageResponse)
async def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    action: Optional[str] = None,
    resource: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """获取日志列表"""
    query = db.query(Log)

    if action:
        query = query.filter(Log.action == action)

    if resource:
        query = query.filter(Log.resource == resource)

    if user_id:
        query = query.filter(Log.user_id == user_id)

    if start_date:
        query = query.filter(Log.created_at >= start_date)

    if end_date:
        query = query.filter(Log.created_at <= end_date)

    total = query.count()
    logs = query.order_by(Log.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 获取用户名
    items = []
    for log in logs:
        log_data = LogResponse.model_validate(log)
        if log.user_id:
            user = db.query(User).filter(User.id == log.user_id).first()
            log_data.username = user.username if user else None
        items.append(log_data)

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/actions")
async def get_log_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """获取所有操作类型"""
    actions = db.query(Log.action).distinct().all()
    return [a[0] for a in actions]


@router.get("/resources")
async def get_log_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """获取所有资源类型"""
    resources = db.query(Log.resource).distinct().all()
    return [r[0] for r in resources if r[0]]


@router.get("/statistics")
async def get_log_statistics(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """获取日志统计"""
    start_date = datetime.utcnow() - timedelta(days=days)

    # 按操作类型统计
    action_stats = db.query(
        Log.action,
        db.func.count(Log.id)
    ).filter(Log.created_at >= start_date).group_by(Log.action).all()

    # 按日期统计
    date_stats = db.query(
        db.func.date(Log.created_at).label("date"),
        db.func.count(Log.id)
    ).filter(Log.created_at >= start_date).group_by(db.func.date(Log.created_at)).all()

    return {
        "action_stats": {a[0]: a[1] for a in action_stats},
        "date_stats": {str(d[0]): d[1] for d in date_stats},
        "total": sum(a[1] for a in action_stats)
    }


@router.get("/dashboard-stats")
async def get_dashboard_stats(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取仪表盘统计数据（用户总数、队伍总数、队员总数、作品总数、投票总数）"""
    # 统计用户总数
    total_users = db.query(func.count(User.id)).scalar() or 0

    # 统计队伍总数
    total_teams = db.query(func.count(Team.id)).scalar() or 0

    # 统计队员总数
    total_members = db.query(func.count(TeamMember.id)).scalar() or 0

    # 统计作品总数
    total_works = db.query(func.count(Work.id)).scalar() or 0

    # 统计投票总数
    total_votes = db.query(func.count(Vote.id)).scalar() or 0

    return {
        "users": total_users,
        "teams": total_teams,
        "members": total_members,
        "works": total_works,
        "votes": total_votes
    }


# 普通用户获取自己的操作日志
@router.get("/my", response_model=PageResponse)
async def get_my_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的操作日志"""
    query = db.query(Log).filter(Log.user_id == current_user.id)

    total = query.count()
    logs = query.order_by(Log.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [LogResponse.model_validate(log) for log in logs]

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )