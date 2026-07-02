"""
分析 API 路由 - 评分分析相关接口
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_active_user, require_permission
from app.models.user import User
from app.models.work import Work, Review, Vote, WorkStatus

router = APIRouter(prefix="/api/admin/analysis", tags=["分析管理"])


# Pydantic Response Models
class SummaryResponse(BaseModel):
    total_works: int
    total_reviewers: int
    total_votes: int
    avg_score: Optional[float]
    pending_reviews: int


class WorkScoreItem(BaseModel):
    rank: int
    work_id: int
    work_name: str
    team_name: str
    vote_count: int
    review_score: Optional[float]
    vote_score: float
    final_score: float


class TopWorksResponse(BaseModel):
    max_votes: int
    works: List[WorkScoreItem]


class ReviewerProgressItem(BaseModel):
    user_id: int
    username: str
    reviewed_count: int
    total_count: int
    percentage: float


class ReviewerProgressResponse(BaseModel):
    total_works: int
    progress: List[ReviewerProgressItem]


class HistogramBin(BaseModel):
    range_start: float
    range_end: float
    count: int


class HistogramData(BaseModel):
    type: str
    bins: List[HistogramBin]


class LineDataPoint(BaseModel):
    rank: int
    score: float


class LineData(BaseModel):
    type: str
    data: List[LineDataPoint]


class BoxplotReviewer(BaseModel):
    reviewer: str
    min_val: float
    q1: float
    median: float
    q3: float
    max_val: float


class BoxplotData(BaseModel):
    type: str
    reviewers: List[BoxplotReviewer]


class ScoreDistributionResponse(BaseModel):
    data: Any  # Can be HistogramData, LineData, or BoxplotData


class ReviewerDetailScore(BaseModel):
    score: Optional[float]
    comment: Optional[str]


class ReviewerDetailItem(BaseModel):
    user_id: int
    username: str
    scores: Dict[str, Optional[float]]  # work_id (as string) -> score
    avg_score: Optional[float]
    progress: str  # "scored/total" format like "10/50"


class ReviewerDetailsResponse(BaseModel):
    works: List[Dict[str, Any]]
    reviewers: List[ReviewerDetailItem]


# Helper Functions
def calculate_final_score(review_score: Optional[float], vote_count: int, max_votes: int) -> float:
    """计算最终得分"""
    vote_score = (vote_count / max_votes * 100) if max_votes > 0 else 0
    if review_score is None:
        return round(vote_score * 0.2, 2)
    return round(0.8 * review_score + 0.2 * vote_score, 2)


def get_filtered_works(db: Session, theme_id: Optional[int] = None, status: Optional[str] = None) -> List[Work]:
    """获取过滤后的作品列表"""
    query = db.query(Work)
    if theme_id:
        query = query.filter(Work.theme_id == theme_id)
    if status:
        query = query.filter(Work.status == status)
    return query.all()


@router.get("/summary", response_model=SummaryResponse)
async def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("analysis:read"))
):
    """获取总体概览统计"""
    total_works = db.query(Work).count()
    total_reviewers = db.query(User).filter(User.role == "reviewer").count()
    total_votes = db.query(Vote).count()

    # 计算平均分
    avg_score = db.query(func.avg(Work.score)).scalar()
    if avg_score is not None:
        avg_score = round(float(avg_score), 2)

    # 待评审数量（分数为空的已通过作品）
    pending_reviews = db.query(Work).filter(
        Work.score == None,
        Work.status == WorkStatus.APPROVED
    ).count()

    return SummaryResponse(
        total_works=total_works,
        total_reviewers=total_reviewers,
        total_votes=total_votes,
        avg_score=avg_score,
        pending_reviews=pending_reviews
    )


@router.get("/top-works", response_model=TopWorksResponse)
async def get_top_works(
    top: int = Query(10, ge=1, le=100),
    theme_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("analysis:read"))
):
    """获取 Top N 作品排行"""
    works = get_filtered_works(db, theme_id, status)

    # 计算最大投票数
    max_votes = db.query(func.max(Work.vote_count)).scalar() or 1

    # 计算每个作品的得分
    work_scores = []
    for work in works:
        # 计算评审平均分
        reviews = db.query(Review).filter(Review.work_id == work.id).all()
        scored_reviews = [r for r in reviews if r.score is not None]
        avg_score = sum(r.score for r in scored_reviews) / len(scored_reviews) if scored_reviews else None

        # 计算投票得分
        vote_score = (work.vote_count / max_votes * 100) if max_votes > 0 else 0

        final_score = calculate_final_score(avg_score, work.vote_count, max_votes)

        work_scores.append({
            "work_id": work.id,
            "work_name": work.name,
            "team_name": work.team.name if work.team else "未知",
            "vote_count": work.vote_count,
            "review_score": avg_score,
            "vote_score": round(vote_score, 2),
            "final_score": final_score
        })

    # 按最终得分排序
    work_scores.sort(key=lambda x: x["final_score"], reverse=True)

    # 取前 N 个
    top_works = work_scores[:top]

    # 添加排名
    items = [
        WorkScoreItem(
            rank=i + 1,
            work_id=w["work_id"],
            work_name=w["work_name"],
            team_name=w["team_name"],
            vote_count=w["vote_count"],
            review_score=w["review_score"],
            vote_score=w["vote_score"],
            final_score=w["final_score"]
        )
        for i, w in enumerate(top_works)
    ]

    return TopWorksResponse(max_votes=max_votes, works=items)


@router.get("/reviewer-progress", response_model=ReviewerProgressResponse)
async def get_reviewer_progress(
    theme_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("analysis:read"))
):
    """获取各评审评分进度"""
    works = get_filtered_works(db, theme_id, status)
    total_works = len(works)

    # 获取所有评审
    reviewers = db.query(User).filter(User.role == "reviewer").all()

    progress_list = []
    for reviewer in reviewers:
        reviewed_count = db.query(Review).filter(
            Review.user_id == reviewer.id,
            Review.work_id.in_([w.id for w in works])
        ).count()

        percentage = (reviewed_count / total_works * 100) if total_works > 0 else 0

        progress_list.append(ReviewerProgressItem(
            user_id=reviewer.id,
            username=reviewer.nickname or reviewer.username,
            reviewed_count=reviewed_count,
            total_count=total_works,
            percentage=round(percentage, 2)
        ))

    return ReviewerProgressResponse(total_works=total_works, progress=progress_list)


@router.get("/score-distribution", response_model=ScoreDistributionResponse)
async def get_score_distribution(
    type: str = Query(..., description="类型: histogram|line|boxplot"),
    theme_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("analysis:read"))
):
    """获取评分分布数据"""
    works = get_filtered_works(db, theme_id, status)

    if type == "histogram":
        # 计算每个作品的平均分
        scores = []
        for work in works:
            reviews = db.query(Review).filter(Review.work_id == work.id).all()
            scored_reviews = [r for r in reviews if r.score is not None]
            if scored_reviews:
                avg_score = sum(r.score for r in scored_reviews) / len(scored_reviews)
                scores.append(avg_score)

        if not scores:
            return ScoreDistributionResponse(data=HistogramData(type="histogram", bins=[]))

        # 创建直方图（10个区间，每个10分）
        bins = []
        for i in range(10):
            range_start = i * 10
            range_end = (i + 1) * 10
            count = sum(1 for s in scores if range_start <= s < range_end)
            bins.append(HistogramBin(range_start=range_start, range_end=range_end, count=count))

        return ScoreDistributionResponse(data=HistogramData(type="histogram", bins=bins))

    elif type == "line":
        # 计算每个作品的平均分并排序
        works_with_scores = []
        for work in works:
            reviews = db.query(Review).filter(Review.work_id == work.id).all()
            scored_reviews = [r for r in reviews if r.score is not None]
            if scored_reviews:
                avg_score = sum(r.score for r in scored_reviews) / len(scored_reviews)
                works_with_scores.append((work.id, avg_score))

        works_with_scores.sort(key=lambda x: x[1], reverse=True)

        data = [
            LineDataPoint(rank=i + 1, score=round(score, 2))
            for i, (work_id, score) in enumerate(works_with_scores)
        ]

        return ScoreDistributionResponse(data=LineData(type="line", data=data))

    elif type == "boxplot":
        # 按评审分组计算每个评审的评分统计
        reviewers = db.query(User).filter(User.role == "reviewer").all()

        boxplot_reviewers = []
        for reviewer in reviewers:
            reviews = db.query(Review).filter(
                Review.user_id == reviewer.id,
                Review.score != None
            ).all()

            if reviews:
                scores = [r.score for r in reviews]
                scores.sort()
                n = len(scores)

                min_val = scores[0]
                max_val = scores[-1]
                median = scores[n // 2]
                q1 = scores[n // 4] if n > 4 else scores[0]
                q3 = scores[3 * n // 4] if n > 4 else scores[-1]

                boxplot_reviewers.append(BoxplotReviewer(
                    reviewer=reviewer.nickname or reviewer.username,
                    min_val=round(min_val, 2),
                    q1=round(q1, 2),
                    median=round(median, 2),
                    q3=round(q3, 2),
                    max_val=round(max_val, 2)
                ))

        return ScoreDistributionResponse(data=BoxplotData(type="boxplot", reviewers=boxplot_reviewers))

    else:
        raise ValueError(f"不支持的分布类型: {type}")


@router.get("/reviewer-details", response_model=ReviewerDetailsResponse)
async def get_reviewer_details(
    theme_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("analysis:read"))
):
    """获取各评审评分详情"""
    works = get_filtered_works(db, theme_id, status)
    reviewers = db.query(User).filter(User.role == "reviewer").all()

    # 构建作品列表
    works_list = [
        {
            "id": w.id,
            "name": w.name,
            "team_name": w.team.name if w.team else "未知"
        }
        for w in works
    ]

    # 构建评审详情
    reviewers_list = []
    for reviewer in reviewers:
        scores = {}
        total_score = 0
        scored_count = 0

        for work in works:
            review = db.query(Review).filter(
                Review.work_id == work.id,
                Review.user_id == reviewer.id
            ).first()

            # 使用字符串 key，JSON 中 number 会被转为 string
            scores[str(work.id)] = review.score if review else None
            if review and review.score is not None:
                total_score += review.score
                scored_count += 1

        avg_score = round(total_score / scored_count, 2) if scored_count > 0 else None
        progress_str = f"{scored_count}/{len(works)}"

        reviewers_list.append(ReviewerDetailItem(
            user_id=reviewer.id,
            username=reviewer.nickname or reviewer.username,
            scores=scores,
            avg_score=avg_score,
            progress=progress_str
        ))

    return ReviewerDetailsResponse(works=works_list, reviewers=reviewers_list)