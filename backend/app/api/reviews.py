"""
评审管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.team import Team, TeamMember
from app.models.work import Work, Review, WorkStatus
from app.models.setting import Log
from app.schemas.work import ReviewCreate, ReviewUpdate, ReviewResponse, WorkResponse
from app.schemas.common import PageResponse
from app.services.webhook import trigger_webhook
from app.models.webhook import WebhookEventType

router = APIRouter(prefix="/reviews", tags=["评审管理"])


def add_log(db: Session, user_id: int, action: str, resource: str = None,
            resource_id: int = None, details: str = None):
    """添加日志"""
    log = Log(user_id=user_id, action=action, resource=resource,
              resource_id=resource_id, details=details)
    db.add(log)
    db.commit()


@router.get("", response_model=PageResponse)
async def get_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    team_name: Optional[str] = None,
    work_name: Optional[str] = None,
    is_scored: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """获取评审列表（评审/管理员）"""
    query = db.query(Work).join(Team)

    if team_name:
        query = query.filter(Team.name.contains(team_name))

    if work_name:
        query = query.filter(Work.name.contains(work_name))

    if is_scored is not None:
        if is_scored:
            query = query.filter(Work.score != None)
        else:
            query = query.filter(Work.score == None)

    total = query.count()
    works = query.order_by(Work.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 获取每个作品的评审信息
    items = []
    for work in works:
        review = db.query(Review).filter(
            Review.work_id == work.id,
            Review.user_id == current_user.id
        ).first()

        work_data = WorkResponse.model_validate(work)
        work_data_dict = work_data.model_dump()
        work_data_dict["my_review"] = ReviewResponse.model_validate(review) if review else None
        work_data_dict["team_name"] = work.team.name
        work_data_dict["reviewer_name"] = current_user.nickname or current_user.username
        items.append(work_data_dict)

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.post("", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """提交评审"""
    work = db.query(Work).filter(Work.id == review_data.work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

    # 检查是否已评审过
    existing = db.query(Review).filter(
        Review.work_id == review_data.work_id,
        Review.user_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="您已评审过该作品")

    # 创建评审
    review = Review(
        work_id=review_data.work_id,
        user_id=current_user.id,
        score=review_data.score,
        comment=review_data.comment
    )
    db.add(review)

    # 更新作品分数
    if review_data.score is not None:
        # 计算平均分
        all_reviews = db.query(Review).filter(Review.work_id == work.id).all()
        total_score = sum(r.score for r in all_reviews if r.score) + review_data.score
        work.score = total_score / (len(all_reviews) + 1)

    db.commit()
    db.refresh(review)

    add_log(db, current_user.id, "review", "work", work.id,
            f"评审作品: {work.name}, 分数: {review_data.score}")

    response = ReviewResponse(
        id=review.id,
        work_id=review.work_id,
        user_id=review.user_id,
        score=review.score,
        comment=review.comment,
        reviewer_name=current_user.nickname or current_user.username,
        created_at=review.created_at,
        updated_at=review.updated_at
    )

    # 触发 Webhook
    await trigger_webhook(db, WebhookEventType.REVIEW_CREATED, {
        "id": review.id,
        "work_id": review.work_id,
        "work_name": work.name,
        "user_id": current_user.id,
        "reviewer_name": current_user.nickname or current_user.username,
        "score": review.score,
        "comment": review.comment
    }, "created")

    return response


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """更新评审"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="评审不存在")

    # 只有评审本人可以更新
    if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")

    # 更新字段
    update_data = review_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review, key, value)

    # 更新作品分数
    work = db.query(Work).filter(Work.id == review.work_id).first()
    if work and review.score is not None:
        all_reviews = db.query(Review).filter(Review.work_id == work.id).all()
        total_score = sum(r.score for r in all_reviews if r.score)
        work.score = total_score / len(all_reviews) if all_reviews else None

    db.commit()
    db.refresh(review)

    add_log(db, current_user.id, "update_review", "work", work.id,
            f"更新评审: {work.name}")

    response = ReviewResponse(
        id=review.id,
        work_id=review.work_id,
        user_id=review.user_id,
        score=review.score,
        comment=review.comment,
        reviewer_name=current_user.nickname or current_user.username,
        created_at=review.created_at,
        updated_at=review.updated_at
    )

    # 触发 Webhook
    await trigger_webhook(db, WebhookEventType.REVIEW_UPDATED, {
        "id": review.id,
        "work_id": review.work_id,
        "work_name": work.name,
        "user_id": current_user.id,
        "score": review.score,
        "comment": review.comment,
        "updated_fields": list(update_data.keys())
    }, "updated")

    return response


@router.get("/my-reviews", response_model=PageResponse)
async def get_my_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """获取我的评审列表"""
    query = db.query(Review).filter(Review.user_id == current_user.id)

    total = query.count()
    reviews = query.order_by(Review.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for review in reviews:
        work = db.query(Work).filter(Work.id == review.work_id).first()
        if work:
            items.append({
                "review": ReviewResponse.model_validate(review),
                "work": WorkResponse.model_validate(work)
            })

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/all-by-work", response_model=PageResponse)
async def get_all_reviews_by_work(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    team_name: Optional[str] = None,
    work_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """获取所有评审（管理员）- 按作品分组显示"""
    query = db.query(Work).join(Team)

    if team_name:
        query = query.filter(Team.name.contains(team_name))

    if work_name:
        query = query.filter(Work.name.contains(work_name))

    total = query.count()
    works = query.order_by(Work.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for work in works:
        # 获取该作品的所有评审
        reviews = db.query(Review).filter(Review.work_id == work.id).all()
        reviewers = []
        for r in reviews:
            reviewer = db.query(User).filter(User.id == r.user_id).first()
            reviewers.append({
                "review_id": r.id,
                "reviewer_name": reviewer.nickname or reviewer.username if reviewer else "未知",
                "score": r.score,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None
            })

        # 计算平均分
        scored_reviews = [r for r in reviews if r.score is not None]
        avg_score = sum(r.score for r in scored_reviews) / len(scored_reviews) if scored_reviews else None

        items.append({
            "id": work.id,
            "work_id": work.id,
            "name": work.name,
            "team_id": work.team.id,
            "team_name": work.team.name,
            "theme_id": work.theme_id,
            "theme_name": work.theme_obj.name if work.theme_obj else None,
            "description": work.description,
            "agent_url": work.agent_url,
            "agent_editor_url": work.agent_editor_url,
            "pdf_file": work.pdf_file,
            "video_file": work.video_file,
            "status": work.status,
            "vote_count": work.vote_count,
            "score": avg_score,
            "review_count": len(reviews),
            "reviews": reviewers
        })

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )