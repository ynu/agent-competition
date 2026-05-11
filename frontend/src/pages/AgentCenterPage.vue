<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { agentCenterApi } from '@/api'

const router = useRouter()
const route = useRoute()

const allAgents = ref<any[]>([])
const filteredAgents = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const page = ref(1)
const pageSize = 24

// Categories list
const categories = [
  { Code: '', Name: '全部' },
  { Code: '2026_agent_competition', Name: '2026智能体大赛' },
  { Code: 'Logistics', Name: '物流' },
  { Code: 'WorkAssistant', Name: '工作助手' },
  { Code: 'TextCreation', Name: '文本创作' },
  { Code: 'BusinessAssistant', Name: '商业助手' },
  { Code: 'Manufacture', Name: '制造业' },
  { Code: 'Finance', Name: '金融' },
  { Code: 'Law', Name: '法律' },
  { Code: 'Medical', Name: '医疗健康' },
  { Code: 'Scientific', Name: '科研' },
  { Code: 'Education', Name: '教育' }
]

// Filters
const selectedCategory = ref<string>('')
const keyword = ref('')
const sort = ref<'latest' | 'popular'>('latest')

// Debounce
let searchTimeout: number | null = null

const totalPages = computed(() => Math.ceil(filteredAgents.value.length / pageSize))

onMounted(async () => {
  if (route.query.category) {
    selectedCategory.value = route.query.category as string
  }
  if (route.query.sort) {
    sort.value = route.query.sort as 'latest' | 'popular'
  }
  await fetchAgents()
})

async function fetchAgents() {
  loading.value = true
  error.value = ''
  try {
    const res = await agentCenterApi.listAgents({
      page: 1,
      page_size: 100,
      sort: sort.value
    })
    allAgents.value = res.data.Result?.Items || []
    applyFilters()
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  let result = [...allAgents.value]

  // Category filter
  if (selectedCategory.value) {
    result = result.filter(agent =>
      agent.CategoryList?.some((c: any) => c.CategoryCode === selectedCategory.value)
    )
  }

  // Keyword filter (search name and description)
  if (keyword.value.trim()) {
    const kw = keyword.value.toLowerCase()
    result = result.filter(agent =>
      agent.Name?.toLowerCase().includes(kw) ||
      agent.Description?.toLowerCase().includes(kw)
    )
  }

  // Sort
  if (sort.value === 'latest') {
    result.sort((a, b) => (b.SubmitTimestamp || 0) - (a.SubmitTimestamp || 0))
  } else {
    result.sort((a, b) => (b.FavoriteCount || 0) - (a.FavoriteCount || 0))
  }

  // Paginate
  const start = (page.value - 1) * pageSize
  filteredAgents.value = result.slice(start, start + pageSize)
}

function handleKeywordInput() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = window.setTimeout(() => {
    page.value = 1
    applyFilters()
  }, 300)
}

function selectCategory(code: string) {
  selectedCategory.value = code
  page.value = 1
  updateUrl()
  applyFilters()
}

function handleSortChange(newSort: 'latest' | 'popular') {
  sort.value = newSort
  page.value = 1
  updateUrl()
  applyFilters()
}

function handlePageChange(newPage: number) {
  page.value = newPage
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function updateUrl() {
  const query: any = {}
  if (selectedCategory.value) query.category = selectedCategory.value
  if (sort.value !== 'latest') query.sort = sort.value
  router.replace({ query })
}

function openAgent(appId: string) {
  window.open(`https://agent.ynu.edu.cn/product/llm/mall/application/${appId}/chat`, '_blank')
}

watch(keyword, handleKeywordInput)
</script>

<template>
  <section class="works-page min-h-[calc(100vh-200px)] bg-white pb-[72px] pt-[24px]">
    <div class="mx-auto max-w-[1200px] px-[16px]">
      <div class="works-breadcrumb flex items-center gap-[6px] text-[14px] text-[#666] font-[400]">
        <i class="iconfont icon-shouye text-[#999999]"></i>
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#047EFF] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <span>智能体广场</span>
      </div>

      <!-- 搜索框 -->
      <div class="mt-[24px] flex justify-center">
        <div class="relative w-[460px]">
          <input
            v-model="keyword"
            type="text"
            placeholder="搜索智能体名称或描述..."
            class="works-search w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-[#f5f5f5]"
            @keyup.enter="handleKeywordInput"
          />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#b8bdc6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
      </div>

      <!-- Sort Buttons -->
      <div class="mt-[20px] flex justify-center gap-[10px]">
        <button
          @click="handleSortChange('latest')"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
          :class="sort === 'latest' ? 'bg-[#0d8bff] text-white' : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'"
        >
          最新上架
        </button>
        <button
          @click="handleSortChange('popular')"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
          :class="sort === 'popular' ? 'bg-[#0d8bff] text-white' : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'"
        >
          最受欢迎
        </button>
      </div>

      <!-- Category Tabs -->
      <div class="mt-[20px] flex flex-wrap gap-[10px]">
        <button
          v-for="cat in categories"
          :key="cat.Code"
          @click="selectCategory(cat.Code)"
          class="px-3 py-1.5 rounded-full text-xs font-medium transition-all"
          :class="selectedCategory === cat.Code ? 'bg-[#0d8bff] text-white' : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'"
        >
          {{ cat.Name }}
        </button>
      </div>

      <!-- Results Count -->
      <div class="mt-[20px] text-sm text-gray-500 text-center">
        共 {{ filteredAgents.length }} 个智能体
        <span v-if="keyword"> · 搜索 "{{ keyword }}"</span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="mt-[36px] text-center py-16">
        <div class="inline-block w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-3 text-gray-500">加载中...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="mt-[36px] text-center py-16">
        <p class="text-red-500 mb-1">{{ error }}</p>
        <p class="text-gray-400 text-sm">请检查火山引擎 API 配置是否正确</p>
      </div>

      <!-- Empty -->
      <div v-else-if="filteredAgents.length === 0" class="mt-[36px] text-center py-16">
        <p class="text-gray-500">暂无智能体</p>
        <p class="text-gray-400 text-sm mt-1">换个关键词试试</p>
      </div>

      <!-- Agent Grid -->
      <div v-else class="mt-[30px] grid grid-cols-1 gap-x-[24px] gap-y-[24px] sm:grid-cols-2 lg:grid-cols-4">
        <article
          v-for="(agent, index) in filteredAgents"
          :key="agent.AppID"
          class="agent-card cursor-pointer rounded-2xl bg-white shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden"
          @click="openAgent(agent.AppID)"
        >
          <!-- Row 1: Logo + Title/Submitter -->
          <div class="flex items-start gap-3 p-4">
            <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center flex-shrink-0 overflow-hidden">
              <img
                v-if="agent.Image"
                :src="agentCenterApi.getImageUrl(agent.Image)"
                class="w-full h-full object-cover"
                @error="$event.target.style.display='none'"
              />
              <span v-else class="text-white text-xl font-bold">AI</span>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-base font-semibold text-gray-800 truncate leading-tight">
                {{ agent.Name }}
              </h3>
              <p class="text-xs text-gray-400 mt-0.5">
                by {{ agent.SubmitUserName || '未知' }}
              </p>
            </div>
          </div>

          <!-- Row 2: Description -->
          <div class="px-4 pb-3">
            <p class="text-sm text-gray-500 truncate leading-normal h-5 overflow-hidden">
              {{ agent.Description || '暂无描述' }}
            </p>
          </div>

          <!-- Row 3: Category Tags -->
          <div class="px-4 pb-3">
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="cat in (agent.CategoryList || []).slice(0, 3)"
                :key="cat.CategoryCode"
                class="px-2 py-0.5 bg-blue-50 text-blue-600 text-xs rounded-full font-medium"
              >
                {{ cat.CategoryName }}
              </span>
            </div>
          </div>

          <!-- Row 4: Stats -->
          <div class="px-4 py-2 text-xs text-gray-400 bg-gray-50 border-t border-gray-100 text-left space-x-4">
            <span class="inline-flex items-center gap-1 text-xs text-gray-500">
              <span>⭐</span>
              {{ agent.FavoriteCount || 0 }}
            </span>
            <span class="inline-flex items-center gap-1 text-xs text-gray-500">
              <span>📖</span>
              {{ agent.UseCount || 0 }}
            </span>
            <span class="inline-flex items-center gap-1 text-xs text-gray-500">
              <span>💬</span>
              {{ agent.ChatCount || 0 }}
            </span>
          </div>
        </article>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="mt-[54px] flex justify-center">
        <el-pagination
          v-model:current-page="page"
          background
          layout="prev, pager, next"
          :page-size="pageSize"
          :total="filteredAgents.length"
          class="works-pagination"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.works-page {
  background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(255, 255, 255, 0.98) 34%, #ffffff 100%);
}

.works-breadcrumb {
  --el-text-color-regular: #8f96a3;
  --el-color-primary: #1288ff;
  font-size: 14px;
}

.agent-card {
  display: flex;
  flex-direction: column;
  min-height: 180px;
}

.works-pagination :deep(.el-pager li),
.works-pagination :deep(.btn-prev),
.works-pagination :deep(.btn-next) {
  width: 30px;
  min-width: 30px;
  height: 30px;
  border-radius: 0;
  background-color: #f0f1f3;
  color: #a7adb7;
  font-size: 14px;
  font-weight: 700;
}

.works-pagination :deep(.el-pager li.is-active) {
  background-color: #1288ff;
  color: #ffffff;
}

@media (min-width: 1024px) {
  .works-page > div {
    max-width: 1190px;
  }
}
</style>