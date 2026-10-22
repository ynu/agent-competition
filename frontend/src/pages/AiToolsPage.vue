<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { aiToolsApi } from '@/api'

const route = useRoute()
const router = useRouter()

const allTools = ref<any[]>([])
const categories = ref<{ name: string; count: number }[]>([])
const loading = ref(true)
const error = ref('')

// Filters
const selectedCategory = ref<string>('')
const keyword = ref('')
const selectedTag = ref<string>('')

// 标签配色（免费=蓝，限免=橙，其余按散列取色）
const tagColors: Record<string, string> = {
  '免费': 'bg-[#0071e3]/10 text-[#0071e3]',
  '限免': 'bg-[#ff9f0a]/12 text-[#c77800]',
  'AI门户': 'bg-[#6a5cff]/10 text-[#6a5cff]',
  '搜索引擎': 'bg-[#30d158]/12 text-[#1f9d41]',
  '模型训练部署': 'bg-[#ff5ca8]/10 text-[#e0447f]',
  '外语学习': 'bg-[#00c6ff]/12 text-[#0087c8]'
}

function tagClass(tag: string) {
  return tagColors[tag] || 'bg-[#86868b]/10 text-[#515154]'
}

const filteredTools = computed(() => {
  let result = [...allTools.value]
  if (selectedCategory.value) {
    result = result.filter(t => t.category === selectedCategory.value)
  }
  if (selectedTag.value) {
    result = result.filter(t => (t.tags || '').split(',').map((s: string) => s.trim()).includes(selectedTag.value))
  }
  if (keyword.value.trim()) {
    const kw = keyword.value.trim().toLowerCase()
    result = result.filter(t =>
      t.title?.toLowerCase().includes(kw) ||
      t.summary?.toLowerCase().includes(kw) ||
      t.category?.toLowerCase().includes(kw) ||
      t.tags?.toLowerCase().includes(kw)
    )
  }
  return result
})

// 按分类分组展示
const groupedTools = computed(() => {
  const groups: { name: string; items: any[] }[] = []
  for (const cat of categories.value) {
    const items = filteredTools.value.filter(t => t.category === cat.name)
    if (items.length) groups.push({ name: cat.name, items })
  }
  // 未在分类列表中的分类兜底
  const known = new Set(categories.value.map(c => c.name))
  const others = filteredTools.value.filter(t => !t.category || !known.has(t.category))
  if (others.length) groups.push({ name: '其他', items: others })
  return groups
})

let searchTimeout: number | null = null

function handleKeywordInput() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = window.setTimeout(updateUrl, 300)
}

function selectCategory(name: string) {
  selectedCategory.value = selectedCategory.value === name ? '' : name
  updateUrl()
}

function selectTag(tag: string) {
  selectedTag.value = selectedTag.value === tag ? '' : tag
  updateUrl()
}

function updateUrl() {
  const query: any = {}
  if (selectedCategory.value) query.category = selectedCategory.value
  if (keyword.value.trim()) query.kw = keyword.value.trim()
  router.replace({ query })
}

function openTool(url: string) {
  if (url) window.open(url, '_blank', 'noopener,noreferrer')
}

watch(keyword, handleKeywordInput)

function scrollToCategory(name: string) {
  // 等待渲染完成后滚动到对应分类锚点
  requestAnimationFrame(() => {
    const el = document.getElementById(`cat-${name}`)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  })
}

watch(selectedCategory, (val) => {
  if (val) scrollToCategory(val)
})

onMounted(async () => {
  // 支持 /aitools#分类名 与 /aitools?category=分类名
  if (route.query.category) {
    selectedCategory.value = route.query.category as string
  } else if (route.hash) {
    selectedCategory.value = decodeURIComponent(route.hash.slice(1))
  }
  if (route.query.kw) {
    keyword.value = route.query.kw as string
  }
  try {
    const [toolsRes, catsRes] = await Promise.all([
      aiToolsApi.list(),
      aiToolsApi.categories()
    ])
    allTools.value = toolsRes.data || []
    categories.value = catsRes.data || []
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || '加载失败'
  } finally {
    loading.value = false
  }
})

// 监听锚点变化（已在 /aitools 页面时点击二级菜单切换分类）
watch(() => route.hash, (hash) => {
  if (hash) {
    selectedCategory.value = decodeURIComponent(hash.slice(1))
  }
})
</script>

<template>
  <section class="min-h-[calc(100vh-200px)] pb-[80px] pt-[28px]">
    <div class="mx-auto max-w-[1200px] px-[16px]">
      <div class="flex items-center gap-[6px] text-[14px] text-[#86868b]">
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#0071e3] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <span>AI工具</span>
      </div>

      <!-- 页头 -->
      <div class="anim-fade-up mt-[28px] text-center">
        <h1 class="text-[34px] font-[700] lg:text-[44px]"><span class="text-gradient">AI工具</span></h1>
        <p class="mt-[10px] text-[15px] text-[#86868b]">精选 AI 工具导航，学习科研办公的好帮手</p>
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
            placeholder="搜索工具名称、描述或标签..."
            class="h-[40px] flex-1 border-0 bg-transparent text-[15px] text-[#1d1d1f] outline-none placeholder:text-[#a1a1a6]"
          />
          <button
            v-if="keyword"
            type="button"
            class="mr-[6px] flex h-[28px] w-[28px] shrink-0 items-center justify-center rounded-full bg-[#86868b]/10 text-[#86868b] transition-colors hover:bg-[#86868b]/20"
            aria-label="清空搜索"
            @click="keyword = ''; updateUrl()"
          >
            <svg class="h-[14px] w-[14px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Category Tabs（锚点导航） -->
      <div class="anim-fade-up mt-[20px] flex flex-wrap justify-center gap-[10px]">
        <a
          v-for="cat in categories"
          :key="cat.name"
          href="javascript:;"
          class="rounded-full px-[15px] py-[7px] text-[13px] font-[500] transition-all duration-300"
          :class="selectedCategory === cat.name
            ? 'bg-gradient-to-r from-[#0090ff] to-[#00c6ff] text-white shadow-[0_6px_18px_rgba(0,144,255,0.35)]'
            : 'bg-white text-[#515154] shadow-[0_2px_8px_rgba(29,42,68,0.06)] hover:-translate-y-0.5 hover:shadow-[0_6px_14px_rgba(29,42,68,0.1)]'"
          @click="selectCategory(cat.name)"
        >
          {{ cat.name }}
          <span class="ml-[2px] opacity-60">{{ cat.count }}</span>
        </a>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="mt-[48px] text-center py-16">
        <div class="inline-block h-10 w-10 animate-spin rounded-full border-4 border-[#0071e3]/20 border-t-[#0071e3]"></div>
        <p class="mt-3 text-[#86868b]">加载中...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="mt-[48px] text-center py-16">
        <p class="mb-1 text-[#ff3b30]">{{ error }}</p>
      </div>

      <!-- Empty -->
      <div v-else-if="filteredTools.length === 0" class="mt-[48px] text-center py-16">
        <p class="text-[#86868b]">未找到相关工具</p>
        <p class="mt-1 text-sm text-[#a1a1a6]">换个关键词试试</p>
      </div>

      <!-- Tool Grid（按分类分组） -->
      <div v-else>
        <div
          v-for="group in groupedTools"
          :key="group.name"
          :id="`cat-${group.name}`"
          class="scroll-mt-[100px]"
        >
          <div class="anim-fade-up mt-[44px] flex items-center gap-[12px]">
            <h2 class="text-[22px] font-[700] text-[#1d1d1f]">{{ group.name }}</h2>
            <span class="rounded-full bg-[#0071e3]/8 px-[10px] py-[2px] text-[13px] font-[500] text-[#0071e3]">
              {{ group.items.length }}
            </span>
            <div class="h-[1px] flex-1 bg-gradient-to-r from-[#d2d2d7] to-transparent"></div>
          </div>

          <div class="anim-stagger mt-[20px] grid grid-cols-1 gap-x-[20px] gap-y-[20px] sm:grid-cols-2 lg:grid-cols-4">
            <article
              v-for="tool in group.items"
              :key="tool.id"
              class="apple-card apple-card-hover group flex cursor-pointer flex-col p-[18px]"
              @click="openTool(tool.external_url)"
            >
              <div class="flex items-start gap-[12px]">
                <div class="h-[52px] w-[52px] shrink-0 overflow-hidden rounded-[14px] bg-white shadow-[0_6px_16px_rgba(29,42,68,0.14)] ring-1 ring-black/[0.04] transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3">
                  <img
                    v-if="tool.icon"
                    :src="tool.icon"
                    :alt="tool.title"
                    class="h-full w-full object-cover"
                    loading="lazy"
                    @error="(e) => { (e.target as HTMLImageElement).style.display = 'none' }"
                  />
                  <span v-else class="flex h-full w-full items-center justify-center text-[18px] font-[800] text-[#0071e3]">AI</span>
                </div>
                <div class="min-w-0 flex-1">
                  <h3 class="truncate text-[15px] font-[700] leading-tight text-[#1d1d1f] transition-colors duration-300 group-hover:text-[#0071e3]">
                    {{ tool.title }}
                  </h3>
                  <div class="mt-[6px] flex flex-wrap gap-[4px]">
                    <span
                      v-for="tag in (tool.tags || '').split(',').map((s: string) => s.trim()).filter(Boolean)"
                      :key="tag"
                      class="rounded-full px-[8px] py-[2px] text-[11px] font-[500]"
                      :class="tagClass(tag)"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
              </div>

              <p class="mt-[12px] line-clamp-3 flex-1 text-[13px] leading-[21px] text-[#86868b]">
                {{ tool.summary || '暂无简介' }}
              </p>

              <div class="mt-[14px] flex items-center justify-between border-t border-black/[0.05] pt-[10px] text-[12px] text-[#a1a1a6]">
                <span class="truncate">{{ tool.category }}</span>
                <span class="inline-flex shrink-0 items-center gap-[4px] text-[#0071e3] opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                  打开
                  <svg class="h-[12px] w-[12px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M7 17L17 7M9 7h8v8"/>
                  </svg>
                </span>
              </div>
            </article>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
