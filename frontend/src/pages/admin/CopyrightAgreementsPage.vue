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