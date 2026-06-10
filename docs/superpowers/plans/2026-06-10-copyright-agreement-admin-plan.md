# 版权协议管理模块实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为管理员提供版权协议签署记录的分页查询、搜索和导出功能

**Architecture:** 后端扩展现有 `/works/copyright-agreements` API 添加搜索参数和导出功能；前端新建管理员页面组件

**Tech Stack:** Python (FastAPI), Vue 3 (Element Plus), openpyxl (Excel导出)

---

## 文件结构

| 操作 | 文件路径 |
|------|---------|
| Modify | `backend/app/api/works.py` - 扩展版权协议API |
| Modify | `backend/app/schemas/work.py` - 扩展响应schema |
| Modify | `frontend/src/api/index.ts` - 添加API接口 |
| Modify | `frontend/src/router/index.ts` - 添加路由 |
| Create | `frontend/src/pages/admin/CopyrightAgreementsPage.vue` - 页面组件 |

---

## Task 1: 扩展后端 Schema

**Files:**
- Modify: `backend/app/schemas/work.py`

- [ ] **Step 1: 添加扩展的版权协议响应 Schema**

在 `CopyrightAgreementResponse` 后添加新的 schema：

```python
class CopyrightAgreementDetailResponse(BaseModel):
    """版权协议详情响应（包含关联信息）"""
    id: int
    user_id: int
    username: Optional[str] = None
    team_name: Optional[str] = None
    work_id: Optional[int] = None
    work_name: Optional[str] = None
    signature_name: Optional[str] = None
    signature_data: Optional[str] = None  # Base64签名图片
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    agreement_content: str
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 提交**

```bash
git add backend/app/schemas/work.py
git commit -m "feat: 添加版权协议详情响应Schema"
```

---

## Task 2: 扩展后端 API

**Files:**
- Modify: `backend/app/api/works.py`

- [ ] **Step 1: 修改获取版权协议列表接口，添加搜索参数**

找到现有接口 `GET /works/copyright-agreements`，修改为：

```python
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
        # 通过 TeamMember 关联查询队伍
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
        # 获取用户名
        user = db.query(User).filter(User.id == a.user_id).first()
        # 获取队伍名
        team_name_val = None
        work_name_val = None
        if user:
            member = db.query(TeamMember).filter(TeamMember.user_id == user.username).first()
            if member:
                team = db.query(Team).filter(Team.id == member.team_id).first()
                if team:
                    team_name_val = team.name
        # 获取作品名
        if a.work_id:
            work = db.query(Work).filter(Work.id == a.work_id).first()
            if work:
                work_name_val = work.name

        items.append({
            "id": a.id,
            "user_id": a.user_id,
            "username": user.nickname if user else str(a.user_id),
            "team_name": team_name_val,
            "work_id": a.work_id,
            "work_name": work_name_val,
            "signature_name": a.signature_name,
            "signature_data": a.signature_data,
            "ip_address": a.ip_address,
            "user_agent": a.user_agent,
            "agreement_content": a.agreement_content[:100] + "..." if len(a.agreement_content) > 100 else a.agreement_content,
            "created_at": a.created_at
        })

    return PageResponse(total=total, page=page, page_size=page_size, items=items)
```

- [ ] **Step 2: 添加获取详情接口**

在文件末尾（`get_copyright_agreements` 函数之后）添加：

```python
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

    # 获取用户信息
    user = db.query(User).filter(User.id == agreement.user_id).first()
    # 获取队伍名
    team_name_val = None
    if user:
        member = db.query(TeamMember).filter(TeamMember.user_id == user.username).first()
        if member:
            team = db.query(Team).filter(Team.id == member.team_id).first()
            if team:
                team_name_val = team.name
    # 获取作品名
    work_name_val = None
    if agreement.work_id:
        work = db.query(Work).filter(Work.id == agreement.work_id).first()
        if work:
            work_name_val = work.name

    return {
        "id": agreement.id,
        "user_id": agreement.user_id,
        "username": user.nickname if user else str(agreement.user_id),
        "team_name": team_name_val,
        "work_id": agreement.work_id,
        "work_name": work_name_val,
        "signature_name": agreement.signature_name,
        "signature_data": agreement.signature_data,
        "ip_address": agreement.ip_address,
        "user_agent": agreement.user_agent,
        "agreement_content": agreement.agreement_content,
        "created_at": agreement.created_at.isoformat()
    }
```

- [ ] **Step 3: 添加导出接口**

在文件末尾添加：

```python
@router.get("/copyright-agreements/export")
async def export_copyright_agreements(
    username: Optional[str] = Query(None, description="用户名搜索"),
    team_name: Optional[str] = Query(None, description="队伍名称搜索"),
    start_date: Optional[str] = Query(None, description="开始时间 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束时间 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """导出版权协议签署记录（仅管理员）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅管理员可导出")

    # 构建查询（与列表接口相同）
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

    # 生成 Excel
    try:
        from openpyxl import Workbook
        from io import BytesIO

        wb = Workbook()
        ws = wb.active
        ws.title = "版权协议签署记录"

        # 表头
        headers = ["用户名", "队伍名称", "关联作品", "签名人", "签署时间", "IP地址", "User-Agent"]
        ws.append(headers)

        # 数据行
        for a in agreements:
            user = db.query(User).filter(User.id == a.user_id).first()
            team_name_val = None
            if user:
                member = db.query(TeamMember).filter(TeamMember.user_id == user.username).first()
                if member:
                    team = db.query(Team).filter(Team.id == member.team_id).first()
                    if team:
                        team_name_val = team.name
            work_name_val = None
            if a.work_id:
                work = db.query(Work).filter(Work.id == a.work_id).first()
                if work:
                    work_name_val = work.name

            ws.append([
                user.nickname if user else str(a.user_id),
                team_name_val or "-",
                work_name_val or "-",
                a.signature_name or "-",
                a.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                a.ip_address or "-",
                a.user_agent or "-"
            ])

        # 保存到内存
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
```

- [ ] **Step 4: 提交**

```bash
git add backend/app/api/works.py
git commit -m "feat: 扩展版权协议API - 添加搜索、详情和导出功能"
```

---

## Task 3: 添加前端 API 接口

**Files:**
- Modify: `frontend/src/api/index.ts`

- [ ] **Step 1: 在 workApi 中添加版权协议管理接口**

在 `workApi` 对象末尾添加：

```typescript
// 版权协议管理（管理员）
listCopyrightAgreements: (params?: {
  page?: number;
  page_size?: number;
  username?: string;
  team_name?: string;
  start_date?: string;
  end_date?: string;
}) => api.get('/works/copyright-agreements', { params }),
getCopyrightAgreementDetail: (id: number) => api.get(`/works/copyright-agreements/${id}`),
exportCopyrightAgreements: (params?: {
  username?: string;
  team_name?: string;
  start_date?: string;
  end_date?: string;
}) => {
  const token = localStorage.getItem('token')
  return `/api/works/copyright-agreements/export?${new URLSearchParams(params as any).toString()}${
    token ? `&token=${token}` : ''
  }`
}
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/api/index.ts
git commit -m "feat: 添加版权协议管理API接口"
```

---

## Task 4: 创建前端页面组件

**Files:**
- Create: `frontend/src/pages/admin/CopyrightAgreementsPage.vue`

- [ ] **Step 1: 创建页面组件**

创建 `frontend/src/pages/admin/CopyrightAgreementsPage.vue`：

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { workApi } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)

// 搜索条件
const searchForm = ref({
  username: '',
  team_name: '',
  start_date: '',
  end_date: ''
})

// 列表数据
const agreements = ref<any[]>([])

// 详情弹窗
const detailVisible = ref(false)
const detailData = ref<any>(null)

// 加载列表
async function fetchList() {
  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize
    }
    if (searchForm.value.username) params.username = searchForm.value.username
    if (searchForm.value.team_name) params.team_name = searchForm.value.team_name
    if (searchForm.value.start_date) params.start_date = searchForm.value.start_date
    if (searchForm.value.end_date) params.end_date = searchForm.value.end_date

    const res = await workApi.listCopyrightAgreements(params)
    agreements.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 搜索
function handleSearch() {
  page.value = 1
  fetchList()
}

// 重置
function handleReset() {
  searchForm.value = {
    username: '',
    team_name: '',
    start_date: '',
    end_date: ''
  }
  handleSearch()
}

// 分页
function handlePageChange(newPage: number) {
  page.value = newPage
  fetchList()
}

// 查看详情
async function handleViewDetail(row: any) {
  try {
    const res = await workApi.getCopyrightAgreementDetail(row.id)
    detailData.value = res.data
    detailVisible.value = true
  } catch (e) {
    console.error(e)
    ElMessage.error('加载详情失败')
  }
}

// 导出
function handleExport() {
  const params: any = {}
  if (searchForm.value.username) params.username = searchForm.value.username
  if (searchForm.value.team_name) params.team_name = searchForm.value.team_name
  if (searchForm.value.start_date) params.start_date = searchForm.value.start_date
  if (searchForm.value.end_date) params.end_date = searchForm.value.end_date

  const url = workApi.exportCopyrightAgreements(params)
  window.open(url, '_blank')
}

// 格式化日期
function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchList()
})
</script>

<template>
  <div>
    <!-- Header -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">版权协议管理</h1>
          <p class="text-sm text-gray-500 mt-1">查看和管理用户的版权协议签署记录</p>
        </div>
        <button
          @click="handleExport"
          class="px-6 py-2.5 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-xl hover:from-green-700 hover:to-green-800 transition-all shadow-lg shadow-green-600/20 font-medium flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
          </svg>
          导出 Excel
        </button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
          <input
            v-model="searchForm.username"
            type="text"
            placeholder="搜索用户名"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">队伍名称</label>
          <input
            v-model="searchForm.team_name"
            type="text"
            placeholder="搜索队伍名称"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">开始时间</label>
          <input
            v-model="searchForm.start_date"
            type="date"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">结束时间</label>
          <input
            v-model="searchForm.end_date"
            type="date"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>
      </div>
      <div class="flex justify-end gap-3 mt-4">
        <button
          @click="handleReset"
          class="px-6 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 transition-all font-medium text-gray-700"
        >
          重置
        </button>
        <button
          @click="handleSearch"
          class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium"
        >
          搜索
        </button>
      </div>
    </div>

    <!-- 表格 -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">ID</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">用户名</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">队伍名称</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">关联作品</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">签名人</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">签署时间</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="item in agreements"
            :key="item.id"
            class="hover:bg-blue-50/50 transition-colors"
          >
            <td class="px-6 py-4 text-sm text-gray-500">{{ item.id }}</td>
            <td class="px-6 py-4 text-sm text-gray-700">{{ item.username || '-' }}</td>
            <td class="px-6 py-4 text-sm text-gray-700">{{ item.team_name || '-' }}</td>
            <td class="px-6 py-4 text-sm text-gray-700">{{ item.work_name || '-' }}</td>
            <td class="px-6 py-4 text-sm text-gray-700">{{ item.signature_name || '-' }}</td>
            <td class="px-6 py-4 text-sm text-gray-500 whitespace-nowrap">{{ formatDate(item.created_at) }}</td>
            <td class="px-6 py-4 text-sm">
              <button
                @click="handleViewDetail(item)"
                class="text-blue-600 hover:text-blue-800 font-medium"
              >
                查看详情
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-flex items-center gap-2 text-gray-500">
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          加载中...
        </div>
      </div>

      <!-- Empty -->
      <div v-else-if="agreements.length === 0" class="text-center py-12 text-gray-500">
        <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        暂无数据
      </div>

      <!-- 分页 -->
      <div v-if="total > pageSize" class="px-6 py-4 border-t border-gray-100 flex justify-center">
        <div class="flex items-center gap-1">
          <button
            @click="handlePageChange(page - 1)"
            :disabled="page === 1"
            class="px-3 py-1.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            上一页
          </button>
          <div class="px-4 py-1.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg text-sm font-medium shadow-md">
            {{ page }} / {{ Math.ceil(total / pageSize) }}
          </div>
          <button
            @click="handlePageChange(page + 1)"
            :disabled="page * pageSize >= total"
            class="px-3 py-1.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="版权协议签署详情"
      width="600px"
    >
      <div v-if="detailData" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-sm font-medium text-gray-500">用户名</label>
            <p class="text-gray-900">{{ detailData.username }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">队伍名称</label>
            <p class="text-gray-900">{{ detailData.team_name || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">关联作品</label>
            <p class="text-gray-900">{{ detailData.work_name || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">签名人</label>
            <p class="text-gray-900">{{ detailData.signature_name || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">签署时间</label>
            <p class="text-gray-900">{{ formatDate(detailData.created_at) }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">IP地址</label>
            <p class="text-gray-900">{{ detailData.ip_address || '-' }}</p>
          </div>
        </div>

        <!-- 签名图片 -->
        <div>
          <label class="text-sm font-medium text-gray-500 mb-2 block">签名图片</label>
          <div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <img
              v-if="detailData.signature_data"
              :src="detailData.signature_data"
              alt="签名"
              class="max-w-full h-auto"
            />
            <span v-else class="text-gray-400">无签名图片</span>
          </div>
        </div>

        <!-- User-Agent -->
        <div>
          <label class="text-sm font-medium text-gray-500">浏览器信息</label>
          <p class="text-gray-700 text-sm break-all">{{ detailData.user_agent || '-' }}</p>
        </div>

        <!-- 协议内容 -->
        <div>
          <label class="text-sm font-medium text-gray-500 mb-2 block">协议内容</label>
          <div class="border border-gray-200 rounded-lg p-4 bg-gray-50 max-h-48 overflow-y-auto">
            <p class="text-gray-700 text-sm whitespace-pre-wrap">{{ detailData.agreement_content }}</p>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/pages/admin/CopyrightAgreementsPage.vue
git commit -m "feat: 添加版权协议管理前端页面"
```

---

## Task 5: 配置路由

**Files:**
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: 添加路由**

在 admin 子路由的 `messages` 路由后添加：

```typescript
{
  path: 'copyright-agreements',
  name: 'admin-copyright-agreements',
  component: () => import('@/pages/admin/CopyrightAgreementsPage.vue'),
  meta: { requiresAdmin: true }
}
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/router/index.ts
git commit -m "feat: 添加版权协议管理路由"
```

---

## Task 6: 安装后端依赖并测试

- [ ] **Step 1: 检查 openpyxl 是否已安装**

```bash
cd backend && pip show openpyxl
```

如果没有安装：

```bash
pip install openpyxl
```

- [ ] **Step 2: 测试 API**

启动后端服务后，测试接口：

```bash
# 测试列表接口（需要管理员token）
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/works/copyright-agreements?page=1&page_size=10"

# 测试搜索
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/works/copyright-agreements?username=张三&start_date=2026-06-01"

# 测试详情
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/works/copyright-agreements/1"

# 测试导出
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/works/copyright-agreements/export" \
  -o copyright_agreements.xlsx
```

- [ ] **Step 3: 提交**

```bash
git add -A
git commit -m "chore: 版权协议管理模块完成"
```

---

## 验证清单

- [ ] 后端 API 返回正确的分页数据
- [ ] 用户名搜索正确过滤
- [ ] 队伍名称搜索正确过滤
- [ ] 时间范围筛选正确
- [ ] 详情接口返回完整信息
- [ ] 签名图片正确显示
- [ ] Excel 导出包含所有必要字段
- [ ] 前端页面正常加载
- [ ] 分页功能正常
- [ ] 搜索功能正常
- [ ] 查看详情功能正常
- [ ] 导出功能正常