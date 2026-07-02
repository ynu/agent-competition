# 评分分析页面实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现评分分析 Dashboard，包含 Top N 作品排行、各评审进度、评分分布图表等

**Architecture:** 后端新增分析 API，前端新增分析页面，通过权限码 `analysis:read` 和 `analysis:export` 控制访问

**Tech Stack:** Vue 3 + ECharts、TailwindCSS、FastAPI、SQLAlchemy

---

## 文件结构

```
backend/
├── app/api/admin/
│   └── analysis.py          # 新增：分析 API（summary, top-works, reviewer-progress, score-distribution, reviewer-details, export）
├── app/models/permission.py  # 修改：添加 analysis 权限分类和默认权限
└── backend/app/__init__.py   # 修改：注册分析路由

frontend/
├── src/api/
│   └── analysis.ts           # 新增：分析 API 客户端
├── src/router/index.ts       # 修改：添加 /admin/analysis 路由
├── src/pages/admin/
│   └── AnalysisPage.vue      # 新增：评分分析主页面
└── src/layouts/MainLayout.vue # 修改：侧边栏添加分析菜单
```

---

## Task 1: 添加分析权限配置

**Files:**
- Modify: `backend/app/models/permission.py`（在 `get_default_permissions()` 和 `PermissionCategory` 中添加）

- [ ] **Step 1: 添加 PermissionCategory.ANALYSIS**

在 `PermissionCategory` 枚举中添加：
```python
ANALYSIS = "analysis"  # 评分分析
```

- [ ] **Step 2: 在 get_default_permissions() 中添加分析权限**

在权限列表末尾添加：
```python
# 评分分析
{"code": "analysis:read", "name": "查看评分分析", "category": "analysis", "action": "read"},
{"code": "analysis:export", "name": "导出评分分析", "category": "analysis", "action": "export"},
```

- [ ] **Step 3: 在 get_default_roles() 中为 reviewer 添加 analysis:read**

修改 reviewer 角色的 permissions：
```python
{
    "code": "reviewer",
    "name": "评审用户",
    "description": "专家评审，可以审核队伍、作品，进行评审打分",
    "permissions": ["team:read", "team:audit", "work:read", "work:audit", "review:create", "review:read", "review:update", "content:read", "log:read", "analysis:read"]
},
```

- [ ] **Step 4: 提交**

```bash
git add backend/app/models/permission.py
git commit -m "feat: add analysis permissions (analysis:read, analysis:export)"
```

---

## Task 2: 创建分析 API 路由

**Files:**
- Create: `backend/app/api/admin/analysis.py`

- [ ] **Step 1: 创建 analysis.py 文件，实现分析 API**

```python
"""
评分分析 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.database import get_db
from app.core.security import require_permission
from app.models.user import User, UserRole
from app.models.work import Work, WorkStatus, Review, Vote
from pydantic import BaseModel
from collections import defaultdict
import statistics

router = APIRouter(prefix="/admin/analysis", tags=["评分分析"])


# === Schema ===

class AnalysisSummaryResponse(BaseModel):
    total_works: int
    total_reviewers: int
    total_votes: int
    avg_score: float
    pending_reviews: int


class TopWorkItem(BaseModel):
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
    works: list[TopWorkItem]


class ReviewerProgressItem(BaseModel):
    user_id: int
    username: str
    reviewed_count: int
    total_count: int
    percentage: float


class ReviewerProgressResponse(BaseModel):
    total_works: int
    progress: list[ReviewerProgressItem]


class ScoreBin(BaseModel):
    range: str
    count: int


class HistogramResponse(BaseModel):
    type: str = "histogram"
    bins: list[ScoreBin]


class LineDataItem(BaseModel):
    rank: int
    score: float


class LineResponse(BaseModel):
    type: str = "line"
    data: list[LineDataItem]


class BoxplotItem(BaseModel):
    username: str
    min_val: float
    q1: float
    median: float
    q3: float
    max_val: float


class BoxplotResponse(BaseModel):
    type: str = "boxplot"
    reviewers: list[BoxplotItem]


class WorkScoreItem(BaseModel):
    id: int
    name: str


class ReviewerDetailScore(BaseModel):
    work_id: int
    score: Optional[float]


class ReviewerDetailItem(BaseModel):
    user_id: int
    username: str
    scores: dict[str, Optional[float]]
    avg_score: Optional[float]
    progress: str


class ReviewerDetailsResponse(BaseModel):
    works: list[WorkScoreItem]
    reviewers: list[ReviewerDetailItem]


# === 辅助函数 ===

def calculate_final_score(review_score: Optional[float], vote_count: int, max_votes: int) -> float:
    """计算最终得分: 0.8 * 评审分 + 0.2 * 投票分"""
    vote_score = (vote_count / max_votes * 100) if max_votes > 0 else 0
    if review_score is None:
        return round(vote_score * 0.2, 2)  # 无评审分时只算投票分
    return round(0.8 * review_score + 0.2 * vote_score, 2)


def get_filtered_works(db: Session, theme_id: Optional[int] = None, status: Optional[str] = None):
    """获取筛选后的作品"""
    query = db.query(Work)
    if theme_id:
        query = query.filter(Work.theme_id == theme_id)
    if status:
        query = query.filter(Work.status == status)
    return query.all()


# === API Endpoints ===

@router.get("/summary", response_model=AnalysisSummaryResponse)
async def get_summary(
    theme_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("analysis:read"))
):
    """获取总体概览统计"""
    works = get_filtered_works(db, theme_id, status)

    # 总作品数
    total_works = len(works)

    # 评审人数（所有评审角色用户）
    total_reviewers = db.query(User).filter(User.role == UserRole.REVIEWER).count()

    # 总投票数
    total_votes = db.query(func.sum(Work.vote_count)).filter(Work.id.in_([w.id for w in works])).scalar() or 0

    # 计算平均分（所有作品的最终分）
    max_votes = db.query(func.max(Work.vote_count)).filter(Work.id.in_([w.id for w in works])).scalar() or 1
    max_votes = max(max_votes, 1)

    total_final_score = 0
    scored_works = 0
    for work in works:
        if work.score is not None:
            final_score = calculate_final_score(work.score, work.vote_count, max_votes)
            total_final_score += final_score
            scored_works += 1

    avg_score = total_final_score / scored_works if scored_works > 0 else 0

    # 待评审数（没有评分的作品）
    pending_reviews = sum(1 for w in works if w.score is None)

    return AnalysisSummaryResponse(
        total_works=total_works,
        total_reviewers=total_reviewers,
        total_votes=total_votes,
        avg_score=round(avg_score, 2),
        pending_reviews=pending_reviews
    )


@router.get("/top-works", response_model=TopWorksResponse)
async def get_top_works(
    top: int = Query(10, ge=1, le=100),
    theme_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("analysis:read"))
):
    """获取 Top N 作品排行"""
    works = get_filtered_works(db, theme_id, status)

    # 获取最高投票数
    max_votes = db.query(func.max(Work.vote_count)).filter(Work.id.in_([w.id for w in works])).scalar() or 1
    max_votes = max(max_votes, 1)

    # 计算每个作品的最终分
    work_scores = []
    for work in works:
        final_score = calculate_final_score(work.score, work.vote_count, max_votes)
        work_scores.append({
            "work": work,
            "final_score": final_score
        })

    # 按最终分降序排序
    work_scores.sort(key=lambda x: x["final_score"], reverse=True)

    # 取 Top N
    top_works = work_scores[:top]

    # 构建响应
    result = []
    for i, item in enumerate(top_works):
        work = item["work"]
        result.append(TopWorkItem(
            rank=i + 1,
            work_id=work.id,
            work_name=work.name,
            team_name=work.team.name if work.team else "",
            vote_count=work.vote_count,
            review_score=work.score,
            vote_score=round(work.vote_count / max_votes * 100, 2),
            final_score=item["final_score"]
        ))

    return TopWorksResponse(max_votes=max_votes, works=result)


@router.get("/reviewer-progress", response_model=ReviewerProgressResponse)
async def get_reviewer_progress(
    theme_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("analysis:read"))
):
    """获取各评审评分进度"""
    works = get_filtered_works(db, theme_id, status)
    total_works = len(works)

    # 获取所有评审
    reviewers = db.query(User).filter(User.role == UserRole.REVIEWER).all()

    progress = []
    for reviewer in reviewers:
        # 获取该评审已评分的作品数
        reviewed_ids = db.query(Review.work_id).filter(
            Review.user_id == reviewer.id,
            Review.work_id.in_([w.id for w in works])
        ).distinct().all()
        reviewed_count = len(set(r.review_id for r in reviewed_ids))
        reviewed_count = db.query(Review).filter(
            Review.user_id == reviewer.id,
            Review.work_id.in_([w.id for w in works]),
            Review.score.isnot(None)
        ).count()

        progress.append(ReviewerProgressItem(
            user_id=reviewer.id,
            username=reviewer.nickname or reviewer.username,
            reviewed_count=reviewed_count,
            total_count=total_works,
            percentage=round(reviewed_count / total_works * 100, 1) if total_works > 0 else 0
        ))

    return ReviewerProgressResponse(total_works=total_works, progress=progress)


@router.get("/score-distribution")
async def get_score_distribution(
    type: str = Query("histogram", regex="^(histogram|line|boxplot)$"),
    theme_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("analysis:read"))
):
    """获取评分分布数据（直方图/折线图/箱线图）"""
    works = get_filtered_works(db, theme_id, status)

    # 获取最高投票数
    max_votes = db.query(func.max(Work.vote_count)).filter(Work.id.in_([w.id for w in works])).scalar() or 1
    max_votes = max(max_votes, 1)

    # 计算每个作品的最终分
    work_scores = []
    for work in works:
        final_score = calculate_final_score(work.score, work.vote_count, max_votes)
        work_scores.append(final_score)

    if type == "histogram":
        # 直方图：按分数区间统计
        bins = []
        for i in range(10):
            low = i * 10
            high = (i + 1) * 10
            count = sum(1 for s in work_scores if low <= s < high)
            bins.append(ScoreBin(range=f"{low}-{high}", count=count))
        # 处理 100 分的情况
        count_100 = sum(1 for s in work_scores if s == 100)
        if count_100 > 0:
            bins[-1] = ScoreBin(range="90-100", count=bins[-1].count + count_100)
        return HistogramResponse(type="histogram", bins=bins)

    elif type == "line":
        # 折线图：按排名顺序展示分数
        work_scores_sorted = sorted(work_scores, reverse=True)
        data = [LineDataItem(rank=i + 1, score=s) for i, s in enumerate(work_scores_sorted)]
        return LineResponse(type="line", data=data)

    else:  # boxplot
        # 箱线图：各评审打分分布
        reviewers = db.query(User).filter(User.role == UserRole.REVIEWER).all()
        boxplot_data = []

        for reviewer in reviewers:
            scores = db.query(Review.score).filter(
                Review.user_id == reviewer.id,
                Review.work_id.in_([w.id for w in works]),
                Review.score.isnot(None)
            ).all()
            score_values = [s[0] for s in scores]

            if score_values:
                boxplot_data.append(BoxplotItem(
                    username=reviewer.nickname or reviewer.username,
                    min_val=min(score_values),
                    q1=statistics.quantiles(score_values, n=4)[0],
                    median=statistics.median(score_values),
                    q3=statistics.quantiles(score_values, n=4)[2],
                    max_val=max(score_values)
                ))

        return BoxplotResponse(type="boxplot", reviewers=boxplot_data)


@router.get("/reviewer-details", response_model=ReviewerDetailsResponse)
async def get_reviewer_details(
    theme_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("analysis:read"))
):
    """获取各评审评分详情"""
    works = get_filtered_works(db, theme_id, status)
    reviewers = db.query(User).filter(User.role == UserRole.REVIEWER).all()

    # 作品列表
    work_list = [WorkScoreItem(id=w.id, name=w.name) for w in works]

    # 评审评分详情
    reviewer_details = []
    for reviewer in reviewers:
        # 获取该评审所有评分
        reviews = db.query(Review).filter(
            Review.user_id == reviewer.id,
            Review.work_id.in_([w.id for w in works])
        ).all()

        scores_dict = {str(r.work_id): r.score for r in reviews}
        reviewed_count = sum(1 for s in scores_dict.values() if s is not None)

        avg_score = None
        if reviewed_count > 0:
            score_values = [s for s in scores_dict.values() if s is not None]
            avg_score = round(sum(score_values) / len(score_values), 2)

        reviewer_details.append(ReviewerDetailItem(
            user_id=reviewer.id,
            username=reviewer.nickname or reviewer.username,
            scores={str(w.id): scores_dict.get(str(w.id)) for w in works},
            avg_score=avg_score,
            progress=f"{reviewed_count}/{len(works)}"
        ))

    return ReviewerDetailsResponse(works=work_list, reviewers=reviewer_details)
```

- [ ] **Step 2: 在 app/__init__.py 中注册分析路由**

```python
from app.api.admin import analysis
router.include_router(analysis.router)
```

- [ ] **Step 3: 提交**

```bash
git add backend/app/api/admin/analysis.py backend/app/__init__.py
git commit -m "feat: add analysis API endpoints for scoring dashboard"
```

---

## Task 3: 创建前端 API 客户端

**Files:**
- Create: `frontend/src/api/analysis.ts`

- [ ] **Step 1: 创建 analysis.ts API 客户端**

```typescript
import api from './index'

export interface AnalysisSummary {
  total_works: number
  total_reviewers: number
  total_votes: number
  avg_score: number
  pending_reviews: number
}

export interface TopWorkItem {
  rank: number
  work_id: number
  work_name: string
  team_name: string
  vote_count: number
  review_score: number | null
  vote_score: number
  final_score: number
}

export interface TopWorksResponse {
  max_votes: number
  works: TopWorkItem[]
}

export interface ReviewerProgressItem {
  user_id: number
  username: string
  reviewed_count: number
  total_count: number
  percentage: number
}

export interface ReviewerProgressResponse {
  total_works: number
  progress: ReviewerProgressItem[]
}

export interface ScoreBin {
  range: string
  count: number
}

export interface HistogramData {
  type: 'histogram'
  bins: ScoreBin[]
}

export interface LineDataItem {
  rank: number
  score: number
}

export interface LineData {
  type: 'line'
  data: LineDataItem[]
}

export interface BoxplotItem {
  username: string
  min_val: number
  q1: number
  median: number
  q3: number
  max_val: number
}

export interface BoxplotData {
  type: 'boxplot'
  reviewers: BoxplotItem[]
}

export type ScoreDistributionData = HistogramData | LineData | BoxplotData

export interface WorkScoreItem {
  id: number
  name: string
}

export interface ReviewerDetailItem {
  user_id: number
  username: string
  scores: Record<string, number | null>
  avg_score: number | null
  progress: string
}

export interface ReviewerDetailsResponse {
  works: WorkScoreItem[]
  reviewers: ReviewerDetailItem[]
}

export const analysisApi = {
  getSummary: (params?: { theme_id?: number; status?: string }) =>
    api.get<AnalysisSummary>('/admin/analysis/summary', { params }),

  getTopWorks: (params?: { top?: number; theme_id?: number; status?: string }) =>
    api.get<TopWorksResponse>('/admin/analysis/top-works', { params }),

  getReviewerProgress: (params?: { theme_id?: number; status?: string }) =>
    api.get<ReviewerProgressResponse>('/admin/analysis/reviewer-progress', { params }),

  getScoreDistribution: (type: 'histogram' | 'line' | 'boxplot', params?: { theme_id?: number; status?: string }) =>
    api.get<ScoreDistributionData>('/admin/analysis/score-distribution', { params: { ...params, type } }),

  getReviewerDetails: (params?: { theme_id?: number; status?: string }) =>
    api.get<ReviewerDetailsResponse>('/admin/analysis/reviewer-details', { params })
}
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/api/analysis.ts
git commit -m "feat: add analysis API client"
```

---

## Task 4: 添加路由和侧边栏菜单

**Files:**
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/layouts/MainLayout.vue`

- [ ] **Step 1: 在 router/index.ts 中添加路由**

在 admin 子路由中添加：
```typescript
{
  path: 'analysis',
  name: 'admin-analysis',
  component: () => import('@/pages/admin/AnalysisPage.vue'),
  meta: { requiresPermission: ['analysis:read'] }
}
```

- [ ] **Step 2: 在 MainLayout.vue 侧边栏添加菜单项**

在 Reviews 菜单项后添加：
```vue
<RouterLink
  v-if="hasPermission('analysis:read')"
  to="/admin/analysis"
  class="flex items-center px-4 py-2 text-sm hover:bg-blue-800"
  :class="route.path === '/admin/analysis' ? 'bg-blue-800' : ''"
>
  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
  </svg>
  评分分析
</RouterLink>
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/router/index.ts frontend/src/layouts/MainLayout.vue
git commit -m "feat: add analysis route and sidebar menu"
```

---

## Task 5: 创建评分分析页面

**Files:**
- Create: `frontend/src/pages/admin/AnalysisPage.vue`

- [ ] **Step 1: 创建 AnalysisPage.vue**

创建完整的评分分析页面，包含：
1. 顶部筛选栏（主题、状态、TopN、导出）
2. 总体概览卡片（4个统计卡片）
3. Top N 作品排行表格
4. 各评审评分进度条
5. 评分分布图表（直方图/折线图/箱线图 Tab 切换）
6. 各评审评分详情表格

页面结构：
```vue
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { analysisApi } from '@/api/analysis'
// ... 引入 ECharts 等

// 状态
const loading = ref(false)
const summary = ref<AnalysisSummary | null>(null)
const topWorks = ref<TopWorksResponse | null>(null)
const reviewerProgress = ref<ReviewerProgressResponse | null>(null)
const chartData = ref<ScoreDistributionData | null>(null)
const reviewerDetails = ref<ReviewerDetailsResponse | null>(null)

// 筛选条件
const topN = ref(10)
const chartType = ref<'histogram' | 'line' | 'boxplot'>('histogram')

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const [s, tw, rp, cd, rd] = await Promise.all([
      analysisApi.getSummary(),
      analysisApi.getTopWorks({ top: topN.value }),
      analysisApi.getReviewerProgress(),
      analysisApi.getScoreDistribution(chartType.value),
      analysisApi.getReviewerDetails()
    ])
    summary.value = s.data
    topWorks.value = tw.data
    reviewerProgress.value = rp.data
    chartData.value = cd.data
    reviewerDetails.value = rd.data
  } finally {
    loading.value = false
  }
}

// 切换图表类型
async function switchChartType(type: 'histogram' | 'line' | 'boxplot') {
  chartType.value = type
  const res = await analysisApi.getScoreDistribution(type)
  chartData.value = res.data
}

// 初始化
onMounted(loadData)
</script>

<template>
  <div class="p-6">
    <!-- 页面标题 -->
    <h1 class="text-2xl font-bold mb-6">评分分析</h1>

    <!-- 筛选栏 -->
    <div class="flex gap-4 mb-6">
      <select v-model="topN" @change="loadData" class="...">
        <option :value="10">Top 10</option>
        <option :value="20">Top 20</option>
        <option :value="50">Top 50</option>
      </select>
      <button @click="exportExcel" class="...">导出Excel</button>
    </div>

    <!-- 总体概览卡片 -->
    <div class="grid grid-cols-4 gap-4 mb-6">
      <!-- 4个统计卡片 -->
    </div>

    <!-- Top N 作品排行 -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <h2 class="text-lg font-semibold mb-4">Top {{ topN }} 作品排行</h2>
      <!-- 表格 -->
    </div>

    <!-- 各评审进度 -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <h2 class="text-lg font-semibold mb-4">各评审评分进度</h2>
      <!-- 进度条 -->
    </div>

    <!-- 评分分布图表 -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex gap-4 mb-4">
        <button @click="switchChartType('histogram')">直方图</button>
        <button @click="switchChartType('line')">折线图</button>
        <button @click="switchChartType('boxplot')">箱线图</button>
      </div>
      <div ref="chartRef" class="h-80"></div>
    </div>

    <!-- 各评审评分详情 -->
    <div class="bg-white rounded-lg shadow p-4">
      <h2 class="text-lg font-semibold mb-4">各评审评分详情</h2>
      <!-- 表格 -->
    </div>
  </div>
</template>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/pages/admin/AnalysisPage.vue
git commit -m "feat: add scoring analysis page"
```

---

## Task 6: 添加 ECharts 依赖（如未安装）

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: 安装 ECharts 和 vue-echarts**

```bash
cd frontend && npm install echarts vue-echarts
```

- [ ] **Step 2: 提交 package.json 变更**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "feat: add echarts dependency for analysis charts"
```

---

## Task 7: 测试和验证

- [ ] **Step 1: 启动后端服务**

```bash
cd backend && uv run python main.py
```

- [ ] **Step 2: 测试 API**

访问 http://localhost:8000/docs 测试以下接口：
- GET /api/admin/analysis/summary
- GET /api/admin/analysis/top-works
- GET /api/admin/analysis/reviewer-progress
- GET /api/admin/analysis/score-distribution
- GET /api/admin/analysis/reviewer-details

- [ ] **Step 3: 启动前端服务**

```bash
cd frontend && npm run dev
```

- [ ] **Step 4: 访问页面**

访问 http://localhost:5173/admin/analysis 测试页面功能

---

## 实现顺序

1. Task 1: 添加分析权限配置
2. Task 2: 创建分析 API 路由
3. Task 3: 创建前端 API 客户端
4. Task 4: 添加路由和侧边栏菜单
5. Task 6: 添加 ECharts 依赖
6. Task 5: 创建评分分析页面
7. Task 7: 测试和验证