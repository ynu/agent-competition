# 评分分析页面设计规范

> **目标：** 实现评分分析 Dashboard，展示 Top N 作品投票数、评审分数、最终分数、各评审评分进度、评分分布曲线等指标。

**架构：** 后端提供分析 API + 前端 Dashboard 页面，通过权限码 `analysis:read` 控制访问。

**技术栈：** Vue 3 + Chart.js / ECharts、TailwindCSS、后端 FastAPI。

---

## 1. 页面入口与权限

| 项目 | 内容 |
|------|------|
| 路由 | `/admin/analysis` |
| 权限码 | `analysis:read`（查看）、`analysis:export`（导出） |
| 侧边栏位置 | 管理菜单，与 Votes、Reviews 同级 |

默认权限分配：
- **admin**：拥有所有权限
- **reviewer**：拥有 `analysis:read`
- **user**：无访问权限

---

## 2. 页面布局

```
┌─────────────────────────────────────────────────────────────┐
│  [主题筛选] [状态筛选]  [TopN: 10/20/50]    [导出Excel]      │
├─────────────────────────────────────────────────────────────┤
│  总体概览卡片          │  Top N 作品排行表格                 │
│  - 作品总数            │  排名|作品名|团队|投票|评审分|总分   │
│  - 评审人数            │                                     │
│  - 平均分              │                                     │
│  - 待评审数            │                                     │
├────────────────────────┴────────────────────────────────────┤
│  各评审评分进度                                            │
│  评审A: ████████████░░░░ 80% (8/10)                        │
│  评审B: ██████████████░░ 90% (9/10)                        │
├─────────────────────────────────────────────────────────────┤
│  评分分布曲线  [直方图] [折线图] [箱线图]                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              图表区域                                 │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  各评审评分详情表格                                        │
│  评审|作品A|作品B|作品C|...|平均分|进度                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 分数计算公式

| 指标 | 计算方式 |
|------|----------|
| 评审分 | 所有评审打分的算术平均（0-100 分） |
| 投票分 | 作品投票数 / 最高投票数 × 100 |
| **最终分** | 0.8 × 评审分 + 0.2 × 投票分 |

---

## 4. 后端 API 设计

### 4.1 总体概览
```
GET /api/admin/analysis/summary
Query: theme_id?, status?
Response:
{
  "total_works": 50,
  "total_reviewers": 5,
  "total_votes": 1250,
  "avg_score": 75.5,
  "pending_reviews": 12
}
```

### 4.2 Top N 作品排行
```
GET /api/admin/analysis/top-works
Query: top=10, theme_id?, status?
Response:
{
  "max_votes": 100,
  "works": [
    {
      "rank": 1,
      "work_id": 1,
      "work_name": "智能问答助手",
      "team_name": "AI先锋队",
      "vote_count": 100,
      "review_score": 85.0,
      "vote_score": 100.0,
      "final_score": 88.0
    },
    ...
  ]
}
```

### 4.3 各评审评分进度
```
GET /api/admin/analysis/reviewer-progress
Query: theme_id?, status?
Response:
{
  "total_works": 50,
  "progress": [
    {
      "user_id": 1,
      "username": "评审A",
      "reviewed_count": 40,
      "total_count": 50,
      "percentage": 80.0
    },
    ...
  ]
}
```

### 4.4 评分分布数据
```
GET /api/admin/analysis/score-distribution
Query: type=histogram|line|boxplot, theme_id?, status?
Response (histogram):
{
  "type": "histogram",
  "bins": [
    {"range": "0-10", "count": 1},
    {"range": "10-20", "count": 2},
    ...
    {"range": "90-100", "count": 5}
  ]
}

Response (line):
{
  "type": "line",
  "data": [
    {"rank": 1, "score": 88.0},
    {"rank": 2, "score": 85.5},
    ...
  ]
}

Response (boxplot):
{
  "type": "boxplot",
  "reviewers": [
    {
      "username": "评审A",
      "min": 60,
      "q1": 70,
      "median": 80,
      "q3": 88,
      "max": 95
    },
    ...
  ]
}
```

### 4.5 各评审评分详情
```
GET /api/admin/analysis/reviewer-details
Query: theme_id?, status?
Response:
{
  "works": [{"id": 1, "name": "作品A"}, ...],
  "reviewers": [
    {
      "user_id": 1,
      "username": "评审A",
      "scores": {"1": 85, "2": 90, "3": null, ...},
      "avg_score": 87.5,
      "progress": "40/50"
    },
    ...
  ]
}
```

### 4.6 导出 Excel
```
GET /api/admin/analysis/export
Query: theme_id?, status?
Response: Excel 文件下载
```

---

## 5. 前端页面结构

```
frontend/src/pages/admin/
  └── AnalysisPage.vue    # 评分分析主页面
```

### 组件结构
- **SummaryCards**: 总体概览 4 个统计卡片
- **TopWorksTable**: Top N 作品排行表格
- **ReviewerProgress**: 各评审评分进度条
- **ScoreCharts**: 评分分布图表（直方图/折线图/箱线图）
- **ReviewerDetailsTable**: 各评审评分详情表

---

## 6. 数据库模型

无需新增模型，复用现有：
- `Work`: vote_count, score
- `Review`: work_id, user_id, score
- `User`: 评审人员

---

## 7. 权限配置

在 `get_default_permissions()` 中添加：
```python
# 评分分析
{"code": "analysis:read", "name": "查看评分分析", "category": "analysis", "action": "read"},
{"code": "analysis:export", "name": "导出评分分析", "category": "analysis", "action": "export"},
```

默认角色权限调整：
- **reviewer**: 添加 `analysis:read`
- **admin**: 拥有所有权限

---

## 8. 实现优先级

1. **Phase 1**: 后端 API（summary, top-works, reviewer-progress）
2. **Phase 2**: 前端基础布局 + SummaryCards + TopWorksTable
3. **Phase 3**: ReviewerProgress 进度条
4. **Phase 4**: 评分分布图表（直方图/折线图/箱线图）
5. **Phase 5**: ReviewerDetailsTable
6. **Phase 6**: 导出 Excel 功能