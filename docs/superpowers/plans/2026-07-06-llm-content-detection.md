# LLM内容检测功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为管理员提供基于大模型的内容检测功能，支持配置LLM、检测作品、管理检测结果

**Architecture:**
- 后端：新增LLM配置表字段、作品表字段、LLM调用服务、检测API接口
- 前端：设置页面新增LLM配置Tab、作品列表页新增检测列和批量检测、作品详情新增检测区域

**Tech Stack:** FastAPI, SQLAlchemy, httpx (LLM调用), Vue 3, TailwindCSS

---

## 文件结构

### 后端变更
- `backend/app/models/work.py` - Work模型新增3字段
- `backend/app/schemas/work.py` - Schemas新增字段
- `backend/app/api/settings.py` - LLM默认配置
- `backend/app/api/works.py` - 新增检测接口
- `backend/app/services/llm.py` - 新建：LLM调用服务

### 前端变更
- `frontend/src/pages/admin/SettingsPage.vue` - 新增LLM配置Tab
- `frontend/src/pages/admin/WorksPage.vue` - 新增检测列、批量检测、详情检测区域

---

## 实现步骤

### Task 1: 更新Work模型 - 新增LLM检测字段

**Files:**
- Modify: `backend/app/models/work.py:1-45`

- [ ] **Step 1: 添加新字段到Work模型**

在 `work.py` 中 Work 类新增3个字段：

```python
# 在 Work 模型中添加（约第35行后，status字段后面）
llm_result = Column(String(20), nullable=True, comment="LLM检测结果：pass/suspicious/fail/null")
llm_result_detail = Column(Text, nullable=True, comment="LLM检测详细结果JSON")
llm_checked_at = Column(DateTime, nullable=True, comment="LLM检测时间")
```

- [ ] **Step 2: 验证模型语法**

Run: `cd backend && uv run python -c "from app.models.work import Work; print('Model OK')"`

---

### Task 2: 更新Work Schemas - 新增响应字段

**Files:**
- Modify: `backend/app/schemas/work.py`

- [ ] **Step 1: 更新WorkResponse添加LLM字段**

在 `WorkResponse` 类（约第40行）中添加：

```python
# WorkResponse 中添加（约第54行后）
llm_result: Optional[str] = None
llm_result_detail: Optional[str] = None
llm_checked_at: Optional[datetime] = None
```

- [ ] **Step 2: 验证schemas语法**

Run: `cd backend && uv run python -c "from app.schemas.work import WorkResponse; print('Schema OK')"`

---

### Task 3: 添加LLM默认配置

**Files:**
- Modify: `backend/app/api/settings.py`

- [ ] **Step 1: 在DEFAULT_SETTINGS中添加LLM配置**

在 `settings.py` 的 `DEFAULT_SETTINGS` 字典中（约第60行后）添加：

```python
# ========== LLM内容检测 ==========
"llm_enabled": {"value": "false", "description": "Enable LLM content detection", "sort_order": 75},
"llm_base_url": {"value": "https://api.openai.com/v1", "description": "LLM API Base URL", "sort_order": 76},
"llm_api_key": {"value": "", "description": "LLM API Key", "sort_order": 77},
"llm_model": {"value": "gpt-4o-mini", "description": "LLM Model name", "sort_order": 78},
"llm_prompt": {"value": """请检测以下作品内容是否合规。

作品名称：{name}
作品描述：{description}
智能体URL：{agent_url}
编排URL：{agent_editor_url}
队伍名称：{team_name}
主题：{theme_name}

请返回JSON格式结果：
{
  "result": "pass|suspicious|fail",
  "reason": "简要说明"
}""", "description": "LLM detection prompt template", "sort_order": 79},
```

- [ ] **Step 2: 验证配置加载**

Run: `cd backend && uv run python -c "from app.api.settings import DEFAULT_SETTINGS; print('llm_enabled' in DEFAULT_SETTINGS)"`

---

### Task 4: 创建LLM调用服务

**Files:**
- Create: `backend/app/services/llm.py`

- [ ] **Step 1: 创建LLM服务模块**

创建 `backend/app/services/llm.py`：

```python
"""
LLM内容检测服务
"""
import json
import httpx
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.setting import Setting


def get_setting(db: Session, key: str, default: str = None) -> str:
    """获取配置"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    return setting.value if setting and setting.value else default


def check_llm_enabled(db: Session) -> bool:
    """检查LLM是否启用"""
    return get_setting(db, "llm_enabled", "false") == "true"


def get_llm_config(db: Session) -> Dict[str, str]:
    """获取LLM配置"""
    return {
        "base_url": get_setting(db, "llm_base_url", "https://api.openai.com/v1"),
        "api_key": get_setting(db, "llm_api_key", ""),
        "model": get_setting(db, "llm_model", "gpt-4o-mini"),
        "prompt": get_setting(db, "llm_prompt", ""),
    }


def format_prompt(prompt_template: str, work_data: Dict[str, Any]) -> str:
    """填充prompt模板中的占位符"""
    placeholders = {
        "name": work_data.get("name", ""),
        "description": work_data.get("description", "") or "无",
        "agent_url": work_data.get("agent_url", "") or "无",
        "agent_editor_url": work_data.get("agent_editor_url", "") or "无",
        "team_name": work_data.get("team_name", "") or "无",
        "theme_name": work_data.get("theme_name", "") or "无",
        "leader_name": work_data.get("leader_name", "") or "无",
        "leader_username": work_data.get("leader_username", "") or "无",
        "vote_count": str(work_data.get("vote_count", 0)),
        "score": str(work_data.get("score", "")) or "无",
        "status": work_data.get("status", "") or "无",
        "created_at": work_data.get("created_at", "") or "无",
    }
    
    result = prompt_template
    for key, value in placeholders.items():
        result = result.replace(f"{{{key}}}", str(value))
    
    return result


async def call_llm(base_url: str, api_key: str, model: str, prompt: str) -> Dict[str, Any]:
    """调用LLM API"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"LLM API调用失败: {response.status_code} - {response.text}")
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        # 尝试解析JSON
        try:
            # 提取JSON部分（可能有markdown代码块）
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            
            result = json.loads(content)
            
            # 验证结果格式
            if "result" not in result:
                result["result"] = "suspicious"
            if "reason" not in result:
                result["reason"] = result.get("result", "检测完成")
            
            return result
        except json.JSONDecodeError:
            # 返回纯文本结果
            return {
                "result": "suspicious",
                "reason": content[:200] if len(content) > 200 else content,
                "raw": content
            }


async def detect_work_content(db: Session, work_data: Dict[str, Any]) -> Dict[str, Any]:
    """检测作品内容"""
    config = get_llm_config(db)
    
    if not config["api_key"]:
        raise Exception("LLM API Key未配置")
    
    if not config["prompt"]:
        raise Exception("LLM检测Prompt未配置")
    
    # 格式化prompt
    prompt = format_prompt(config["prompt"], work_data)
    
    # 调用LLM
    result = await call_llm(
        config["base_url"],
        config["api_key"],
        config["model"],
        prompt
    )
    
    # 限制detail长度
    result_json = json.dumps(result, ensure_ascii=False)
    if len(result_json) > 4096:
        result_json = result_json[:4093] + "..."
    
    return {
        "result": result.get("result", "suspicious"),
        "reason": result.get("reason", "检测完成"),
        "detail": result_json
    }
```

- [ ] **Step 2: 创建services目录__init__.py**

检查是否存在 `backend/app/services/__init__.py`，如果不存在则创建：

```python
# backend/app/services/__init__.py
```

- [ ] **Step 3: 验证服务模块**

Run: `cd backend && uv run python -c "from app.services.llm import check_llm_enabled; print('LLM service OK')"`

---

### Task 5: 添加LLM检测API接口

**Files:**
- Modify: `backend/app/api/works.py`

- [ ] **Step 1: 在works.py末尾添加LLM检测接口**

在 `works.py` 末尾（约第1074行后）添加：

```python
# ============== LLM内容检测 ==============

class LLMCheckRequest(BaseModel):
    work_ids: List[int] = Field(..., min_length=1, description="作品ID列表")


class LLMCheckResponse(BaseModel):
    work_id: int
    result: str
    reason: str
    detail: Optional[str] = None
    error: Optional[str] = None


class LLMBatchCheckResponse(BaseModel):
    total: int
    success: int
    failed: int
    results: List[LLMCheckResponse]


@router.post("/{work_id}/llm-check")
async def check_work_llm(
    work_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """检测单个作品内容"""
    from app.services.llm import check_llm_enabled, detect_work_content
    
    # 检查LLM是否启用
    if not check_llm_enabled(db):
        raise HTTPException(status_code=400, detail="LLM检测未启用，请在设置中开启")
    
    # 获取作品
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # 准备作品数据
    work_data = {
        "name": work.name,
        "description": work.description or "",
        "agent_url": work.agent_url or "",
        "agent_editor_url": work.agent_editor_url or "",
        "team_name": work.team.name if work.team else "",
        "theme_name": work.theme_obj.name if work.theme_obj else "",
        "vote_count": work.vote_count,
        "score": work.score,
        "status": work.status.value if hasattr(work.status, 'value') else work.status,
        "created_at": work.created_at.isoformat() if work.created_at else "",
    }
    
    try:
        result = await detect_work_content(db, work_data)
        
        # 更新作品记录
        work.llm_result = result["result"]
        work.llm_result_detail = result["detail"]
        work.llm_checked_at = datetime.utcnow()
        db.commit()
        
        add_log(db, current_user.id, "llm_check", "work", work_id, f"LLM检测: {result['result']}")
        
        return {
            "result": result["result"],
            "reason": result["reason"],
            "detail": result["detail"],
            "checked_at": work.llm_checked_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-llm-check", response_model=LLMBatchCheckResponse)
async def batch_check_works_llm(
    request: LLMCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """批量检测作品内容（串行）"""
    from app.services.llm import check_llm_enabled, detect_work_content
    
    # 检查LLM是否启用
    if not check_llm_enabled(db):
        raise HTTPException(status_code=400, detail="LLM检测未启用，请在设置中开启")
    
    work_ids = request.work_ids
    results = []
    success_count = 0
    failed_count = 0
    
    for work_id in work_ids:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            results.append(LLMCheckResponse(
                work_id=work_id,
                result="",
                reason="",
                error="作品不存在"
            ))
            failed_count += 1
            continue
        
        # 准备作品数据
        work_data = {
            "name": work.name,
            "description": work.description or "",
            "agent_url": work.agent_url or "",
            "agent_editor_url": work.agent_editor_url or "",
            "team_name": work.team.name if work.team else "",
            "theme_name": work.theme_obj.name if work.theme_obj else "",
            "vote_count": work.vote_count,
            "score": work.score,
            "status": work.status.value if hasattr(work.status, 'value') else work.status,
            "created_at": work.created_at.isoformat() if work.created_at else "",
        }
        
        try:
            result = await detect_work_content(db, work_data)
            
            # 更新作品记录
            work.llm_result = result["result"]
            work.llm_result_detail = result["detail"]
            work.llm_checked_at = datetime.utcnow()
            db.commit()
            
            results.append(LLMCheckResponse(
                work_id=work_id,
                result=result["result"],
                reason=result["reason"],
                detail=result["detail"]
            ))
            success_count += 1
            
            add_log(db, current_user.id, "llm_check", "work", work_id, f"LLM检测: {result['result']}")
            
        except Exception as e:
            results.append(LLMCheckResponse(
                work_id=work_id,
                result="",
                reason="",
                error=str(e)
            ))
            failed_count += 1
    
    return LLMBatchCheckResponse(
        total=len(work_ids),
        success=success_count,
        failed=failed_count,
        results=results
    )
```

注意：需要在文件顶部添加 `List` 和 `Field` 的导入：
```python
from typing import List, Optional
from pydantic import BaseModel, Field
```

- [ ] **Step 2: 验证API语法**

Run: `cd backend && uv run python -c "from app.api.works import router; print('API OK')"`

---

### Task 6: 迁移数据库 - 添加LLM字段

**Files:**
- Create: `backend/migrations/001_add_llm_fields.py` (可选数据库迁移脚本)

- [ ] **Step 1: 使用SQLite ALTER TABLE**

如果使用SQLite，需要重建表：

Run: `cd backend && uv run python -c "
import sqlite3
import os

db_path = './agent_competition.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查列是否存在
    cursor.execute(\"PRAGMA table_info(works)\")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'llm_result' not in columns:
        cursor.execute('ALTER TABLE works ADD COLUMN llm_result VARCHAR(20) DEFAULT NULL')
    if 'llm_result_detail' not in columns:
        cursor.execute('ALTER TABLE works ADD COLUMN llm_result_detail TEXT DEFAULT NULL')
    if 'llm_checked_at' not in columns:
        cursor.execute('ALTER TABLE works ADD COLUMN llm_checked_at DATETIME DEFAULT NULL')
    
    conn.commit()
    conn.close()
    print('Database migration completed')
else:
    print('Database file not found, will be created on first run')
"`

---

### Task 7: 前端 - 设置页面新增LLM配置Tab

**Files:**
- Modify: `frontend/src/pages/admin/SettingsPage.vue`

- [ ] **Step 1: 在SettingsPage.vue添加LLM配置Tab**

在 `<script setup>` 中添加状态：

```javascript
// 在现有状态变量后添加（约第30行）
const activeTab = ref('general')
const showApiKey = ref(false)

// LLM配置相关
const llmConfig = ref({
  enabled: false,
  base_url: 'https://api.openai.com/v1',
  api_key: '',
  model: 'gpt-4o-mini',
  prompt: ''
})

// 加载LLM配置
async function loadLlmConfig() {
  try {
    const keys = ['llm_enabled', 'llm_base_url', 'llm_api_key', 'llm_model', 'llm_prompt']
    const results = await Promise.all(keys.map(key => api.get(`/settings/${key}`)))
    llmConfig.value = {
      enabled: results[0].data?.value === 'true',
      base_url: results[1].data?.value || 'https://api.openai.com/v1',
      api_key: results[2].data?.value || '',
      model: results[3].data?.value || 'gpt-4o-mini',
      prompt: results[4].data?.value || ''
    }
  } catch (e) {
    console.error('Failed to load LLM config:', e)
  }
}

// 保存LLM配置
async function saveLlmConfig() {
  try {
    await api.put('/settings/llm_enabled', { value: String(llmConfig.value.enabled) })
    await api.put('/settings/llm_base_url', { value: llmConfig.value.base_url })
    await api.put('/settings/llm_api_key', { value: llmConfig.value.api_key })
    await api.put('/settings/llm_model', { value: llmConfig.value.model })
    await api.put('/settings/llm_prompt', { value: llmConfig.value.prompt })
    success('保存成功', 'LLM配置已保存')
  } catch (e: any) {
    error('保存失败', e.response?.data?.detail)
  }
}

// 在onMounted中调用
onMounted(async () => {
  await fetchSettings()
  if (authStore.isAdmin) {
    await loadLlmConfig()
  }
})
```

- [ ] **Step 2: 在模板中添加LLM配置Tab**

在设置页面tab导航中添加：

```html
<!-- 在现有tab后添加 -->
<button
  @click="activeTab = 'llm'"
  :class="activeTab === 'llm' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'"
  class="px-4 py-3 font-medium transition-colors"
>
  LLM配置
</button>
```

- [ ] **Step 3: 添加LLM配置内容区域**

在tab内容区域添加：

```html
<!-- 在 tab-content 后添加 -->
<div v-if="activeTab === 'llm'" class="space-y-6">
  <div class="bg-gray-50 rounded-xl p-4">
    <h3 class="text-lg font-medium text-gray-800 mb-4">LLM内容检测配置</h3>
    
    <!-- 启用开关 -->
    <div class="flex items-center gap-3 mb-4">
      <label class="relative inline-flex items-center cursor-pointer">
        <input v-model="llmConfig.enabled" type="checkbox" class="sr-only peer">
        <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
      </label>
      <span class="text-sm text-gray-600">启用LLM内容检测</span>
    </div>
    
    <!-- Base URL -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-1">API Base URL</label>
      <input
        v-model="llmConfig.base_url"
        type="text"
        class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
        placeholder="https://api.openai.com/v1"
      />
    </div>
    
    <!-- API Key -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
      <div class="relative">
        <input
          v-model="llmConfig.api_key"
          :type="showApiKey ? 'text' : 'password'"
          class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 pr-12"
          placeholder="sk-..."
        />
        <button
          @click="showApiKey = !showApiKey"
          type="button"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        >
          <svg v-if="!showApiKey" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Model -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-1">模型</label>
      <input
        v-model="llmConfig.model"
        type="text"
        class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
        placeholder="gpt-4o-mini"
      />
    </div>
    
    <!-- Prompt -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-1">检测Prompt模板</label>
      <textarea
        v-model="llmConfig.prompt"
        rows="8"
        class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
        placeholder="请输入检测prompt，使用 {name} {description} 等占位符"
      ></textarea>
      <p class="mt-1 text-xs text-gray-400">支持的占位符：{name}, {description}, {agent_url}, {agent_editor_url}, {team_name}, {theme_name}, {leader_name}, {leader_username}, {vote_count}, {score}, {status}, {created_at}</p>
    </div>
    
    <button
      @click="saveLlmConfig"
      class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium"
    >
      保存配置
    </button>
  </div>
</div>
```

- [ ] **Step 3: 验证前端语法**

Run: `cd frontend && npm run build 2>&1 | head -30`

---

### Task 8: 前端 - 作品列表页新增LLM检测列

**Files:**
- Modify: `frontend/src/pages/admin/WorksPage.vue`

- [ ] **Step 1: 添加批量LLM检测状态和函数**

在 `<script setup>` 中添加（约第60行后）：

```javascript
// 批量LLM检测状态
const llmCheckProgress = ref({ show: false, current: 0, total: 0, results: [] as any[] })

// LLM检测结果格式化
function getLlmResultLabel(result: string | null) {
  switch (result) {
    case 'pass': return '通过'
    case 'suspicious': return '可疑'
    case 'fail': return '失败'
    default: return '未检测'
  }
}

function getLlmResultClass(result: string | null) {
  switch (result) {
    case 'pass': return 'bg-green-100 text-green-700'
    case 'suspicious': return 'bg-yellow-100 text-yellow-700'
    case 'fail': return 'bg-red-100 text-red-700'
    default: return 'bg-gray-100 text-gray-500'
  }
}

// 批量LLM检测
async function handleBatchLlmCheck() {
  if (selectedWorks.value.size === 0) {
    error('操作失败', '请先选择要检测的作品')
    return
  }
  
  llmCheckProgress.value = {
    show: true,
    current: 0,
    total: selectedWorks.value.size,
    results: []
  }
  
  try {
    const workIds = Array.from(selectedWorks.value)
    const res = await api.post('/works/batch-llm-check', { work_ids: workIds })
    
    llmCheckProgress.value.results = res.data.results || []
    llmCheckProgress.value.success = res.data.success
    llmCheckProgress.value.failed = res.data.failed
    
    clearSelection()
    await fetchWorks()
    success('检测完成', `成功 ${res.data.success} 个，失败 ${res.data.failed} 个`)
  } catch (e: any) {
    error('检测失败', e.response?.data?.detail)
  } finally {
    llmCheckProgress.value.show = false
  }
}

// 单个作品LLM检测
async function handleSingleLlmCheck(work: any, event: Event) {
  event.stopPropagation()
  
  try {
    await api.post(`/works/${work.id}/llm-check`)
    await fetchWorks()
    success('检测完成')
  } catch (e: any) {
    error('检测失败', e.response?.data?.detail)
  }
}
```

- [ ] **Step 2: 在批量操作区域添加LLM检测按钮**

在 Header 区域的批量操作按钮组中添加（约第620行）：

```html
<button
  @click="handleBatchLlmCheck"
  class="px-3 py-1.5 text-sm font-medium text-purple-600 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
>
  LLM检测
</button>
```

- [ ] **Step 3: 在表格头中添加LLM检测列**

在 `<thead>` 中添加（约第738行前）：

```html
<th class="px-4 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">LLM检测</th>
```

- [ ] **Step 4: 在表格体中添加LLM检测列**

在 `<tbody>` 中对应的 `<tr>` 内添加（约第772行后）：

```html
<td class="px-4 py-4">
  <div class="flex items-center gap-2">
    <span
      :class="getLlmResultClass(work.llm_result)"
      class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
    >
      {{ getLlmResultLabel(work.llm_result) }}
    </span>
    <button
      v-if="canAudit"
      @click="handleSingleLlmCheck(work, $event)"
      class="text-purple-600 hover:text-purple-700 text-xs font-medium"
      title="LLM检测"
    >
      检测
    </button>
  </div>
</td>
```

- [ ] **Step 5: 添加批量检测进度对话框**

在模板末尾（CopyrightAgreementDialog前）添加：

```html
<!-- LLM检测进度对话框 -->
<Dialog
  :show="llmCheckProgress.show"
  title="LLM批量检测中"
  width="lg"
  :closeOnClickOverlay="false"
>
  <div class="p-6">
    <div class="flex items-center gap-3 mb-4">
      <svg class="animate-spin w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-gray-600">正在检测作品... ({{ llmCheckProgress.current }}/{{ llmCheckProgress.total }})</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-2">
      <div
        class="bg-blue-600 h-2 rounded-full transition-all"
        :style="{ width: `${(llmCheckProgress.current / llmCheckProgress.total) * 100}%` }"
      ></div>
    </div>
  </div>
</Dialog>
```

- [ ] **Step 6: 验证前端**

Run: `cd frontend && npm run build 2>&1 | head -30`

---

### Task 9: 前端 - 作品详情页新增LLM检测区域

**Files:**
- Modify: `frontend/src/pages/admin/WorksPage.vue`

- [ ] **Step 1: 在详情Dialog中添加LLM检测区域**

在详情Dialog的内容区域（作品详情表格后）添加（约第952行，审核按钮前）：

```html
<!-- LLM检测结果区域 -->
<div v-if="canAudit" class="mt-6 pt-6 border-t border-gray-200">
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-lg font-medium text-gray-800">LLM内容检测</h3>
    <div class="flex items-center gap-2">
      <span
        v-if="editingWork?.llm_checked_at"
        class="text-xs text-gray-400"
      >
        检测时间：{{ new Date(editingWork.llm_checked_at).toLocaleString() }}
      </span>
      <button
        @click="handleSingleLlmCheck(editingWork, $event)"
        class="px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all shadow-lg shadow-purple-600/20 text-sm font-medium"
      >
        立即检测
      </button>
    </div>
  </div>
  
  <div class="bg-purple-50 rounded-xl p-4">
    <div class="flex items-start gap-4">
      <div class="flex-shrink-0">
        <span
          :class="getLlmResultClass(editingWork?.llm_result)"
          class="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium"
        >
          <template v-if="editingWork?.llm_result === 'pass'">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            通过
          </template>
          <template v-else-if="editingWork?.llm_result === 'suspicious'">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            可疑
          </template>
          <template v-else-if="editingWork?.llm_result === 'fail'">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
            失败
          </template>
          <template v-else>
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            未检测
          </template>
        </span>
      </div>
      
      <div class="flex-1" v-if="editingWork?.llm_result_detail">
        <p class="text-sm text-gray-600 mb-2">检测详情：</p>
        <pre class="text-xs text-gray-700 bg-white rounded-lg p-3 overflow-auto max-h-48 whitespace-pre-wrap">{{ formatLlmDetail(editingWork?.llm_result_detail) }}</pre>
      </div>
      <div v-else class="text-sm text-gray-400">
        暂无检测结果，请点击"立即检测"进行内容检测
      </div>
    </div>
  </div>
</div>
```

- [ ] **Step 2: 添加formatLlmDetail函数**

在 `<script setup>` 中添加：

```javascript
// 格式化LLM检测详情
function formatLlmDetail(detail: string | null) {
  if (!detail) return ''
  try {
    const parsed = JSON.parse(detail)
    if (parsed.reason) {
      return parsed.reason + (parsed.raw ? '\n\n原始响应：\n' + parsed.raw : '')
    }
    return JSON.stringify(parsed, null, 2)
  } catch {
    return detail
  }
}
```

- [ ] **Step 3: 验证前端**

Run: `cd frontend && npm run build 2>&1 | head -30`

---

### Task 10: 测试与验证

- [ ] **Step 1: 启动后端服务**

Run: `cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

- [ ] **Step 2: 启动前端服务**

Run: `cd frontend && npm run dev`

- [ ] **Step 3: 配置LLM**

1. 登录管理后台
2. 进入设置页面
3. 点击"LLM配置"Tab
4. 填写API配置并保存
5. 启用LLM检测

- [ ] **Step 4: 测试LLM检测功能**

1. 进入作品管理页面
2. 查看列表是否显示LLM检测列
3. 点击作品的"检测"按钮测试单个检测
4. 选择多个作品，点击"LLM检测"测试批量检测
5. 打开作品详情，查看LLM检测区域

---

## 自检清单

- [ ] 所有占位符已替换为实际代码
- [ ] 类型一致性检查（函数名、参数）
- [ ] API路径与设计文档一致
- [ ] 前端组件引用正确

---

**Plan complete and saved to `docs/superpowers/plans/2026-07-06-llm-content-detection.md`**

Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?