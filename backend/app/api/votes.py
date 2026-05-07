"""
投票管理 API 路由
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.work import Work, Vote
from app.models.team import Team
from app.schemas.common import PageResponse

router = APIRouter(prefix="/votes", tags=["投票管理"])


class ClearVotesRequest(BaseModel):
    """清除投票请求"""
    type: str  # "all", "user", "work"
    user_id: Optional[int] = None
    work_id: Optional[int] = None


class SetVoteCountRequest(BaseModel):
    """设置投票数请求"""
    work_id: int
    vote_count: int


@router.get("", response_model=PageResponse)
async def get_votes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    work_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """获取投票记录列表（支持按用户或作品筛选）"""
    query = db.query(Vote)

    if user_id:
        query = query.filter(Vote.user_id == user_id)
    if work_id:
        query = query.filter(Vote.work_id == work_id)

    total = query.count()
    votes = query.order_by(Vote.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 构造返回数据，包含用户和作品信息
    items = []
    for v in votes:
        items.append({
            "id": v.id,
            "user_id": v.user_id,
            "work_id": v.work_id,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "user": {
                "id": v.user.id,
                "username": v.user.username,
                "nickname": v.user.nickname
            } if v.user else None,
            "work": {
                "id": v.work.id,
                "name": v.work.name,
                "team_name": v.work.team.name if v.work.team else None
            } if v.work else None
        })

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/by-user", response_model=PageResponse)
async def get_votes_by_user(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """按用户视角查看投票情况（显示每个用户的投票记录）"""
    # 查询每个用户的投票统计
    user_query = db.query(
        User.id,
        User.username,
        User.nickname,
        func.count(Vote.id).label("vote_count")
    ).outerjoin(Vote, Vote.user_id == User.id)

    if keyword:
        user_query = user_query.filter(
            or_(
                User.username.contains(keyword),
                User.nickname.contains(keyword)
            )
        )

    # 按投票数排序
    user_query = user_query.group_by(User.id).order_by(func.count(Vote.id).desc())

    total = user_query.count()
    users = user_query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for u in users:
        # 获取该用户最近投的几票
        recent_votes = db.query(Vote).filter(Vote.user_id == u.id).order_by(Vote.created_at.desc()).limit(3).all()
        vote_details = []
        for v in recent_votes:
            vote_details.append({
                "work_id": v.work_id,
                "work_name": v.work.name if v.work else None,
                "team_name": v.work.team.name if v.work and v.work.team else None,
                "created_at": v.created_at.isoformat() if v.created_at else None
            })

        items.append({
            "user_id": u.id,
            "username": u.username,
            "nickname": u.nickname,
            "vote_count": u.vote_count,
            "recent_votes": vote_details
        })

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/by-work", response_model=PageResponse)
async def get_votes_by_work(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """按作品视角查看投票情况（显示每个作品的投票记录）"""
    # 查询每个作品的投票统计
    work_query = db.query(
        Work.id,
        Work.name,
        Work.vote_count,
        Work.status,
        Team.name.label("team_name")
    ).outerjoin(Team, Team.id == Work.team_id)

    if keyword:
        work_query = work_query.filter(
            or_(
                Work.name.contains(keyword),
                Team.name.contains(keyword)
            )
        )

    if status:
        work_query = work_query.filter(Work.status == status)

    # 按投票数排序
    work_query = work_query.order_by(Work.vote_count.desc())

    total = work_query.count()
    works = work_query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for w in works:
        # 获取该作品最近的投票者
        recent_voters = db.query(Vote).filter(Vote.work_id == w.id).order_by(Vote.created_at.desc()).limit(5).all()
        voter_details = []
        for v in recent_voters:
            voter_details.append({
                "user_id": v.user_id,
                "username": v.user.username if v.user else None,
                "nickname": v.user.nickname if v.user else None,
                "created_at": v.created_at.isoformat() if v.created_at else None
            })

        items.append({
            "work_id": w.id,
            "work_name": w.name,
            "team_name": w.team_name,
            "vote_count": w.vote_count,
            "status": w.status,
            "recent_voters": voter_details
        })

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/statistics")
async def get_vote_statistics(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """获取投票统计数据"""
    # 总投票数
    total_votes = db.query(func.count(Vote.id)).scalar() or 0

    # 总投票用户数（去重）
    total_voted_users = db.query(func.count(func.distinct(Vote.user_id))).scalar() or 0

    # 被投票的作品数
    total_voted_works = db.query(func.count(func.distinct(Vote.work_id))).scalar() or 0

    # 今日投票数
    today = datetime.utcnow().date()
    today_votes = db.query(func.count(Vote.id)).filter(
        func.date(Vote.created_at) == today
    ).scalar() or 0

    # 每日投票趋势
    start_date = datetime.utcnow() - timedelta(days=days)
    daily_stats = db.query(
        func.date(Vote.created_at).label("date"),
        func.count(Vote.id).label("count")
    ).filter(Vote.created_at >= start_date).group_by(func.date(Vote.created_at)).all()

    daily_trend = {str(d[0]): d[1] for d in daily_stats}

    # 投票最多的作品 Top 10
    top_works = db.query(
        Work.id,
        Work.name,
        Work.vote_count,
        Team.name.label("team_name")
    ).outerjoin(Team, Team.id == Work.team_id).order_by(Work.vote_count.desc()).limit(10).all()

    top_works_list = []
    for w in top_works:
        top_works_list.append({
            "work_id": w.id,
            "work_name": w.name,
            "team_name": w.team_name,
            "vote_count": w.vote_count
        })

    # 投票最多的用户 Top 10
    top_users = db.query(
        User.id,
        User.username,
        User.nickname,
        func.count(Vote.id).label("vote_count")
    ).join(Vote, Vote.user_id == User.id).group_by(User.id).order_by(func.count(Vote.id).desc()).limit(10).all()

    top_users_list = []
    for u in top_users:
        top_users_list.append({
            "user_id": u.id,
            "username": u.username,
            "nickname": u.nickname,
            "vote_count": u.vote_count
        })

    return {
        "total_votes": total_votes,
        "total_voted_users": total_voted_users,
        "total_voted_works": total_voted_works,
        "today_votes": today_votes,
        "daily_trend": daily_trend,
        "top_works": top_works_list,
        "top_users": top_users_list
    }


# ============== 投票管理操作 ==============

@router.post("/clear")
async def clear_votes(
    request: ClearVotesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """清除投票记录"""
    count = 0
    if request.type == "all":
        # 清除所有投票
        count = db.query(Vote).delete()
        # 重置所有作品的投票数
        db.query(Work).update({Work.vote_count: 0})
    elif request.type == "user" and request.user_id:
        # 清除指定用户的投票
        user_votes = db.query(Vote).filter(Vote.user_id == request.user_id).all()
        # 减少对应作品的投票数
        for vote in user_votes:
            work = db.query(Work).filter(Work.id == vote.work_id).first()
            if work and work.vote_count > 0:
                work.vote_count -= 1
        count = len(user_votes)
        db.query(Vote).filter(Vote.user_id == request.user_id).delete()
    elif request.type == "work" and request.work_id:
        # 清除指定作品的投票
        vote_count = db.query(Vote).filter(Vote.work_id == request.work_id).count()
        db.query(Vote).filter(Vote.work_id == request.work_id).delete()
        # 重置作品投票数
        work = db.query(Work).filter(Work.id == request.work_id).first()
        if work:
            work.vote_count = 0
        count = vote_count
    else:
        raise HTTPException(status_code=400, detail="无效的清除类型")

    db.commit()
    return {"message": f"已清除 {count} 条投票记录"}


@router.post("/set-vote-count")
async def set_vote_count(
    request: SetVoteCountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """设置作品投票数（用于测试）"""
    work = db.query(Work).filter(Work.id == request.work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

    old_count = work.vote_count
    work.vote_count = request.vote_count
    db.commit()

    return {
        "message": f"已设置作品投票数从 {old_count} 为 {request.vote_count}",
        "work_id": work.id,
        "work_name": work.name,
        "old_count": old_count,
        "new_count": request.vote_count
    }


@router.post("/batch-set-vote-count")
async def batch_set_vote_count(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """批量设置作品投票数"""
    work_ids = body.get("work_ids", [])
    vote_count = body.get("vote_count", 0)

    if not work_ids:
        raise HTTPException(status_code=400, detail="请选择作品")

    updated = 0
    for work_id in work_ids:
        work = db.query(Work).filter(Work.id == work_id).first()
        if work:
            work.vote_count = vote_count
            updated += 1

    db.commit()
    return {"message": f"已为 {updated} 个作品设置投票数为 {vote_count}"}