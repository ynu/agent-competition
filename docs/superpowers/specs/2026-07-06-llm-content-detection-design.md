# LLM内容检测功能设计

**日期**: 2026-07-06
**状态**: 已批准

---

## 概述

为管理员提供基于大模型的内容检测功能，自动检测作品是否符合规范/合规要求。

---

## 1. 配置管理

### 1.1 LLM配置Tab

在设置页面新增独立的"LLM配置"标签页，包含以下配置项：

| 配置键 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `llm_enabled` | boolean | false | 是否启用LLM检测 |
| `llm_base_url` | string | `https://api.openai.com/v1` | API Base URL |
| `llm_api_key` | string | - | API密钥（加密存储） |
| `llm_model` | string | `gpt-4o-mini` | 模型名称 |
| `llm_prompt` | text | 见下方 | 检测提示词模板 |

### 1.2 默认Prompt模板

```
请检测以下作品内容是否合规。

作品名称：{name}
作品描述：{description}
智能体URL：{agent_url}
编排URL：{agent_editor_url}
队伍名称：{team_name}
主题：{theme_name}

请返回JSON格式结果：
{
  "result": "pass|suspicious|fail",  // 通过/可疑/失败
  "reason": "简要说明"  // 100字以内
}
```

### 1.3 支持的占位符

works表所有字段均可使用：
- `{name}` - 作品名称
- `{description}` - 作品描述
- `{agent_url}` - 智能体URL
- `{agent_editor_url}` - 编排URL
- `{team_name}` - 队伍名称（关联查询）
- `{leader_name}` - 队长姓名（关联查询）
- `{leader_username}` - 队长学工号（关联查询）
- `{theme_name}` - 主题名称（关联查询）
- `{vote_count}` - 投票数
- `{score}` - 评分
- `{status}` - 状态
- `{created_at}` - 创建时间

---

## 2. 数据模型

### 2.1 Works表新增字段

```sql
ALTER TABLE works ADD COLUMN llm_result VARCHAR(20) DEFAULT NULL COMMENT 'LLM检测结果：pass/suspicious/fail/null';
ALTER TABLE works ADD COLUMN llm_result_detail TEXT DEFAULT NULL COMMENT 'LLM检测详细结果JSON';
ALTER TABLE works ADD COLUMN llm_checked_at DATETIME DEFAULT NULL COMMENT 'LLM检测时间';
```

### 2.2 字段说明

| 字段 | 说明 |
|------|------|
| `llm_result` | 检测结果：pass(通过)、suspicious(可疑)、fail(失败)、null(未检测) |
| `llm_result_detail` | LLM返回的完整JSON或详细描述 |
| `llm_checked_at` | 检测时间 |

---

## 3. API设计

### 3.1 检测接口

```
POST /api/works/{id}/llm-check
```

**请求**: 无body
**响应**:
```json
{
  "result": "pass",
  "reason": "内容合规",
  "detail": {...}
}
```

**错误处理**:
- 400: LLM未配置
- 500: LLM调用失败

### 3.2 批量检测接口

```
POST /api/works/batch-llm-check
```

**请求**:
```json
{
  "work_ids": [1, 2, 3]
}
```

**响应**:
```json
{
  "total": 3,
  "success": 2,
  "failed": 1,
  "results": [
    {"work_id": 1, "result": "pass"},
    {"work_id": 2, "result": "suspicious"},
    {"work_id": 3, "error": "LLM调用超时"}
  ]
}
```

---

## 4. 前端页面

### 4.1 设置页面 - LLM配置Tab

**路径**: `SettingsPage.vue`

**UI元素**:
- 启用开关（toggle）
- Base URL 输入框
- API Key 输入框（密码类型，显示/隐藏切换）
- Model 输入框
- Prompt 文本域（支持多行，含占位符提示）
- 占位符快捷插入按钮

### 4.2 作品列表页增强

**路径**: `WorksPage.vue`

**新增列**: LLM检测
```
| LLM检测 |
| 绿色✓ 通过 |
| 黄色⚠ 可疑 |
| 红色✗ 失败 |
| 灰色- 未检测 |
```

**新增功能**:
- 批量选择后，"批量操作"区域新增"LLM检测"按钮
- 批量检测弹窗显示进度：正在检测 2/5...
- 完成后显示结果汇总

### 4.3 作品详情页增强

**路径**: `WorksPage.vue` (Dialog内)

**新增区域**:
- LLM检测状态标签
- "立即检测"按钮
- 检测时间显示
- 详细结果展开/折叠（显示LLM返回的完整内容）

---

## 5. 实现步骤

### 5.1 后端
1. 更新Work模型，新增3个字段
2. 创建LLM配置API（复用settings接口）
3. 实现 `/works/{id}/llm-check` 接口
4. 实现 `/works/batch-llm-check` 接口
5. 编写LLM调用工具类（支持OpenAI兼容API）

### 5.2 前端
1. SettingsPage新增LLM配置Tab
2. WorksPage新增LLM检测列
3. WorksPage新增批量检测功能
4. WorksPage详情Dialog新增LLM检测区域
5. 调用API更新列表数据

---

## 6. 依赖

- OpenAI兼容API（支持chat completions接口）
- 后端需安装 `openai` 或 `httpx` 库

---

## 7. 安全考虑

- API Key 在前端脱敏显示，后端加密存储
- 批量检测添加速率限制，防止API配额耗尽
- LLM返回内容做长度截断（最大4KB）