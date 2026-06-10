# 版权协议管理模块设计

## 概述

为管理员提供版权协议签署记录的管理功能，支持分页查询、搜索和导出。

## 后端 API

### 1. 分页查询接口扩展
**端点:** `GET /api/works/copyright-agreements`

**参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |
| username | string | 否 | 用户名搜索 |
| team_name | string | 否 | 队伍名称搜索 |
| start_date | string | 否 | 开始时间 (ISO格式) |
| end_date | string | 否 | 结束时间 (ISO格式) |

**权限:** 仅 ADMIN/REVIEWER

**响应:**
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "username": "张三",
      "team_name": "智能先锋队",
      "work_id": 10,
      "work_name": "智能客服系统",
      "signature_name": "张三",
      "signature_data": "data:image/png;base64,...",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "agreement_content_hash": "sha256:...",
      "created_at": "2026-06-10T10:00:00"
    }
  ]
}
```

### 2. 详情接口
**端点:** `GET /api/works/copyright-agreements/{id}`

**权限:** 仅 ADMIN/REVIEWER

**响应:** 返回单条签署记录的完整信息，包含完整的 agreement_content

### 3. 导出接口
**端点:** `GET /api/works/copyright-agreements/export`

**参数:** 同分页查询（不含分页参数）

**权限:** 仅 ADMIN

**响应:** Excel 文件 (.xlsx)

**Excel 字段:**
- 用户名
- 队伍名称
- 关联作品
- 签名人
- 签署时间
- IP地址
- User-Agent

## 前端页面

### 文件位置
`frontend/src/pages/admin/CopyrightAgreementsPage.vue`

### 功能模块

1. **搜索栏**
   - 用户名输入框
   - 队伍名称输入框
   - 时间范围选择器

2. **数据表格**
   - 列：ID、用户名、队伍名、关联作品、签名人、签署时间、操作
   - 分页组件
   - 支持排序（按签署时间）

3. **详情弹窗**
   - 用户信息
   - 队伍信息
   - 关联作品
   - 签名图片预览（base64渲染）
   - IP地址、User-Agent
   - 协议内容摘要

4. **导出功能**
   - 导出按钮
   - 根据当前搜索条件导出

### 路由配置
```typescript
{
  path: 'copyright-agreements',
  name: 'admin-copyright-agreements',
  component: () => import('@/pages/admin/CopyrightAgreementsPage.vue'),
  meta: { requiresAdmin: true }
}
```

## 数据模型

### CopyrightAgreement 扩展字段
现有模型已包含所有必要字段，无需修改。

```python
class CopyrightAgreement(Base):
    id: int
    user_id: int
    work_id: Optional[int]
    signature_data: str  # Base64编码的签名图片
    signature_name: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    agreement_content: str  # 签署时的协议快照
    created_at: datetime
```

## 依赖

- 后端：`openpyxl` (Excel导出)
- 前端：Element Plus (已有)

## 实现顺序

1. 后端：扩展 API 端点
2. 前端：添加 API 接口定义
3. 前端：创建页面组件
4. 配置路由