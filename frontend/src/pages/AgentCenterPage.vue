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

// 分类胶囊的绚丽配色
const categoryHues = [
  'from-[#0090ff] to-[#00c6ff]',
  'from-[#6a5cff] to-[#a18cd1]',
  'from-[#ff5ca8] to-[#ff9f45]',
  'from-[#30d158] to-[#00c6ff]',
  'from-[#ff9f0a] to-[#ff5ca8]'
]

function categoryHue(index: number) {
  return categoryHues[index % categoryHues.length]
}

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
  <section class="min-h-[calc(100vh-200px)] pb-[80px] pt-[28px]">
    <div class="mx-auto max-w-[1200px] px-[16px]">
      <div class="flex items-center gap-[6px] text-[14px] text-[#86868b]">
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#0071e3] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <span>智能体广场</span>
      </div>

      <!-- 页头 -->
      <div class="anim-fade-up mt-[28px] text-center">
        <h1 class="text-[34px] font-[700] lg:text-[44px]"><span class="text-gradient">智能体广场</span></h1>
        <p class="mt-[10px] text-[15px] text-[#86868b]">探索同学们创造的智能体</p>
      </div>

      <!-- 搜索框：胶囊 -->
      <div class="anim-fade-up mt-[28px] flex justify-center">
        <div class="glass flex w-full max-w-[520px] items-center gap-[10px] rounded-full p-[6px] pl-[20px] shadow-[var(--shadow-card)] transition-shadow duration-300 focus-within:shadow-[0_0_0_4px_rgba(0,113,227,0.15),var(--shadow-card)]">
          <svg class="h-[18px] w-[18px] shrink-0 text-[#86868b]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input
            v-model="keyword"
            type="text"
            placeholder="搜索智能体名称或描述..."
            class="h-[40px] flex-1 border-0 bg-transparent text-[15px] text-[#1d1d1f] outline-none placeholder:text-[#a1a1a6]"
            @keyup.enter="handleKeywordInput"
          />
        </div>
      </div>

      <!-- Sort Buttons -->
      <div class="anim-fade-up mt-[20px] flex justify-center gap-[10px]">
        <button
          @click="handleSortChange('latest')"
          class="rounded-full px-[20px] py-[9px] text-[14px] font-[500] transition-all duration-300"
          :class="sort === 'latest'
            ? 'bg-gradient-to-r from-[#0090ff] to-[#00c6ff] text-white shadow-[0_6px_18px_rgba(0,144,255,0.35)]'
            : 'bg-white text-[#515154] shadow-[0_2px_10px_rgba(29,42,68,0.07)] hover:shadow-[0_6px_18px_rgba(29,42,68,0.12)] hover:-translate-y-0.5'"
        >
          最新上架
        </button>
        <button
          @click="handleSortChange('popular')"
          class="rounded-full px-[20px] py-[9px] text-[14px] font-[500] transition-all duration-300"
          :class="sort === 'popular'
            ? 'bg-gradient-to-r from-[#ff5ca8] to-[#ff9f45] text-white shadow-[0_6px_18px_rgba(255,92,168,0.35)]'
            : 'bg-white text-[#515154] shadow-[0_2px_10px_rgba(29,42,68,0.07)] hover:shadow-[0_6px_18px_rgba(29,42,68,0.12)] hover:-translate-y-0.5'"
        >
          最受欢迎
        </button>
      </div>

      <!-- Category Tabs -->
      <div class="anim-fade-up mt-[20px] flex flex-wrap justify-center gap-[10px]">
        <button
          v-for="(cat, index) in categories"
          :key="cat.Code"
          @click="selectCategory(cat.Code)"
          class="rounded-full px-[15px] py-[7px] text-[13px] font-[500] transition-all duration-300"
          :class="selectedCategory === cat.Code
            ? `bg-gradient-to-r ${categoryHue(index)} text-white shadow-[0_6px_16px_rgba(106,92,255,0.3)]`
            : 'bg-white text-[#515154] shadow-[0_2px_8px_rgba(29,42,68,0.06)] hover:-translate-y-0.5 hover:shadow-[0_6px_14px_rgba(29,42,68,0.1)]'"
        >
          {{ cat.Name }}
        </button>
      </div>

      <!-- Results Count -->
      <div class="mt-[24px] text-center text-[14px] text-[#86868b]">
        共 {{ filteredAgents.length }} 个智能体
        <span v-if="keyword"> · 搜索 "{{ keyword }}"</span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="mt-[48px] text-center py-16">
        <div class="inline-block h-10 w-10 animate-spin rounded-full border-4 border-[#0071e3]/20 border-t-[#0071e3]"></div>
        <p class="mt-3 text-[#86868b]">加载中...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="mt-[48px] text-center py-16">
        <p class="mb-1 text-[#ff3b30]">{{ error }}</p>
        <p class="text-sm text-[#86868b]">请检查火山引擎 API 配置是否正确</p>
      </div>

      <!-- Empty -->
      <div v-else-if="filteredAgents.length === 0" class="mt-[48px] text-center py-16">
        <p class="text-[#86868b]">暂无智能体</p>
        <p class="mt-1 text-sm text-[#a1a1a6]">换个关键词试试</p>
      </div>

      <!-- Agent Grid -->
      <div v-else class="anim-stagger mt-[36px] grid grid-cols-1 gap-x-[24px] gap-y-[24px] sm:grid-cols-2 lg:grid-cols-4">
        <article
          v-for="(agent, index) in filteredAgents"
          :key="agent.AppID"
          class="apple-card apple-card-hover group cursor-pointer overflow-hidden p-0"
          @click="openAgent(agent.AppID)"
        >
          <!-- Row 1: Logo + Title/Submitter -->
          <div class="flex items-start gap-3 p-[18px] pb-[12px]">
            <div
              class="h-[54px] w-[54px] shrink-0 overflow-hidden rounded-[16px] shadow-[0_8px_20px_rgba(29,42,68,0.18)] transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3"
              :class="`bg-gradient-to-br ${categoryHue(index)}`"
            >
              <img
                v-if="agent.Image"
                :src="agentCenterApi.getImageUrl(agent.Image)"
                class="h-full w-full object-cover"
                @error="(e) => { (e.target as HTMLImageElement).style.display = 'none' }"
              />
              <span v-else class="flex h-full w-full items-center justify-center text-[18px] font-[800] text-white">AI</span>
            </div>
            <div class="min-w-0 flex-1">
              <h3 class="truncate text-[16px] font-[700] leading-tight text-[#1d1d1f] transition-colors duration-300 group-hover:text-[#0071e3]">
                {{ agent.Name }}
              </h3>
              <p class="mt-1 text-[12px] text-[#a1a1a6]">
                by {{ agent.SubmitUserName || '未知' }}
              </p>
            </div>
          </div>

          <!-- Row 2: Description -->
          <div class="px-[18px] pb-[10px]">
            <p class="h-5 truncate text-[13px] leading-5 text-[#86868b]">
              {{ agent.Description || '暂无描述' }}
            </p>
          </div>

          <!-- Row 3: Category Tags -->
          <div class="px-[18px] pb-[12px]">
            <div class="flex flex-wrap gap-[6px]">
              <span
                v-for="(cat, ci) in (agent.CategoryList || []).slice(0, 3)"
                :key="cat.CategoryCode"
                class="rounded-full px-[9px] py-[3px] text-[11px] font-[500]"
                :class="`bg-gradient-to-r ${categoryHue(Number(ci))} bg-clip-text`"
                style="color: transparent; background-clip: text; -webkit-background-clip: text; border: 1px solid rgba(120,120,128,0.18)"
              >
                {{ cat.CategoryName }}
              </span>
            </div>
          </div>

          <!-- Row 4: Stats -->
          <div class="flex space-x-4 border-t border-black/[0.05] bg-black/[0.02] px-[18px] py-[10px] text-[12px] text-[#86868b]">
            <span class="inline-flex items-center gap-1">
              <span>⭐</span> {{ agent.FavoriteCount || 0 }}
            </span>
            <span class="inline-flex items-center gap-1">
              <span>📖</span> {{ agent.UseCount || 0 }}
            </span>
            <span class="inline-flex items-center gap-1">
              <span>💬</span> {{ agent.ChatCount || 0 }}
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
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </section>
</template>
