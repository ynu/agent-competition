<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { workApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const works = ref<any[]>([])
const loading = ref(true)
const keyword = ref('')
const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)

// 投票状态
const votingStatus = ref<any>({
  max_votes: 5,
  used_votes: 0,
  remaining_votes: 5,
  voted_works: [],
  total_works: 0,
  voting_open: true
})

// 绚丽卡片头部渐变
const headerClasses = [
  'bg-gradient-to-br from-[#00c6ff] to-[#0071e3]',
  'bg-gradient-to-br from-[#30d158] to-[#0090ff]',
  'bg-gradient-to-br from-[#6a5cff] to-[#a18cd1]',
  'bg-gradient-to-br from-[#ff9f45] to-[#ff5ca8]'
]

onMounted(async () => {
  await fetchWorks()
  if (authStore.isLoggedIn) {
    await fetchVotingStatus()
  }
})

async function fetchWorks() {
  loading.value = true
  try {
    const params: any = { page: currentPage.value, page_size: pageSize.value }
    if (keyword.value.trim()) {
      params.keyword = keyword.value.trim()
    }
    const response = await workApi.list(params)
    works.value = response.data?.items || []
    total.value = response.data?.total || 0
  } catch (e: any) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchVotingStatus() {
  try {
    const response = await fetch('/api/works/voting-status', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) {
      const data = await response.json()
      votingStatus.value = data
    }
  } catch (e) {
    console.error(e)
  }
}

async function handleVote(work: any, event: Event) {
  event.stopPropagation()
  event.preventDefault()

  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }

  if (hasVoted(work.id)) return

  try {
    await workApi.vote(work.id)
    work.vote_count = (work.vote_count || 0) + 1
    await fetchVotingStatus()
    ElMessage.success('投票成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '投票失败')
  }
}

function hasVoted(workId: number): boolean {
  return votingStatus.value.voted_works?.some((w: any) => w.id === workId)
}

function openWorkDetail(work: any) {
  router.push(`/works/${work.id}`)
}

function handleSearch() {
  currentPage.value = 1
  fetchWorks()
}

function handlePageChange(page: number) {
  currentPage.value = page
  fetchWorks()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  fetchWorks()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function getHeaderClass(index: number): string {
  return headerClasses[index % headerClasses.length]
}
</script>

<template>
  <section class="min-h-[calc(100vh-200px)] pb-[80px] pt-[28px]">
    <div class="mx-auto max-w-[1200px] px-[16px]">
      <div class="flex items-center gap-[6px] text-[14px] text-[#86868b]">
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#0071e3] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <span>参赛作品</span>
      </div>

      <!-- 页头 -->
      <div class="anim-fade-up mt-[28px] text-center">
        <h1 class="text-[34px] font-[700] lg:text-[44px]"><span class="text-gradient">参赛作品</span></h1>
        <p class="mt-[10px] text-[15px] text-[#86868b]">为喜欢的作品投上一票</p>
      </div>

      <!-- 搜索框：胶囊 -->
      <div class="anim-fade-up mt-[28px] flex justify-center">
        <div class="glass flex w-full max-w-[520px] items-center gap-[8px] rounded-full p-[6px] pl-[20px] shadow-[var(--shadow-card)] transition-shadow duration-300 focus-within:shadow-[0_0_0_4px_rgba(0,113,227,0.15),var(--shadow-card)]">
          <el-icon class="text-[#86868b]"><Search /></el-icon>
          <input
            v-model="keyword"
            type="text"
            placeholder="搜索作品名称或队伍..."
            class="h-[40px] flex-1 border-0 bg-transparent text-[15px] text-[#1d1d1f] outline-none placeholder:text-[#a1a1a6]"
            @keyup.enter="handleSearch"
          />
          <el-button type="primary" round class="!h-[40px] !px-[26px]" @click="handleSearch">搜索</el-button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="mt-[48px] text-center py-16">
        <div class="inline-block h-10 w-10 animate-spin rounded-full border-4 border-[#0071e3]/20 border-t-[#0071e3]"></div>
        <p class="mt-3 text-[#86868b]">加载中...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="works.length === 0" class="mt-[48px] text-center py-16">
        <p class="text-[#86868b]">暂无参赛作品</p>
      </div>

      <!-- Works Grid -->
      <div v-else class="anim-stagger mt-[44px] grid grid-cols-1 gap-x-[26px] gap-y-[26px] sm:grid-cols-2 lg:grid-cols-4">
        <article
          v-for="work in works"
          :key="work.id"
          class="apple-card apple-card-hover group cursor-pointer overflow-hidden p-0"
          role="button"
          tabindex="0"
          @click="openWorkDetail(work)"
          @keydown.enter="openWorkDetail(work)"
          @keydown.space.prevent="openWorkDetail(work)"
        >
          <!-- 绚丽渐变头部 -->
          <div class="relative h-[116px] overflow-hidden" :class="getHeaderClass(work.id)">
            <div class="absolute left-[16px] top-[10px] text-[72px] font-[900] leading-none text-white/25 transition-transform duration-700 group-hover:scale-110">
              Ai
            </div>
            <div class="absolute inset-x-0 bottom-0 h-[60px] bg-gradient-to-t from-black/25 to-transparent"></div>
            <span class="absolute left-[14px] top-[14px] rounded-full bg-white/25 px-[10px] py-[2px] text-[12px] font-[700] text-white backdrop-blur-sm">
              #{{ work.id }}
            </span>
            <div class="absolute inset-x-[16px] bottom-[12px]">
              <h2 class="line-clamp-3 w-full text-[16px] font-[700] leading-[22px] text-white drop-shadow">
                {{ work.name }}
              </h2>
            </div>
          </div>

          <div class="px-[18px] pb-[20px] pt-[16px]">
            <dl class="space-y-[8px] text-[14px] leading-[20px]">
              <div class="flex w-full items-center justify-between gap-3">
                <dt class="shrink-0 text-[#86868b]">参赛队伍</dt>
                <dd class="min-w-0 flex-1 truncate text-right font-[500] text-[#1d1d1f]">{{ work.team_name }}</dd>
              </div>
              <div class="flex w-full items-center justify-between gap-3">
                <dt class="shrink-0 text-[#86868b]">当前票数</dt>
                <dd class="min-w-0 text-right font-[700] text-[#0071e3]">{{ work.vote_count || 0 }}</dd>
              </div>
            </dl>

            <div class="mt-[18px]">
              <el-button
                round
                :type="hasVoted(work.id) ? 'info' : 'primary'"
                :disabled="hasVoted(work.id)"
                class="!h-[38px] !w-full !text-[15px] !font-[600]"
                @click="handleVote(work, $event)"
                @keydown.enter.stop
                @keydown.space.stop
              >
                <i class="iconfont icon-toupiao text-[18px] mr-1.5"></i>
                {{ hasVoted(work.id) ? '已投过票' : '我要投票' }}
              </el-button>
            </div>
          </div>
        </article>
      </div>

      <!-- Pagination -->
      <div class="mt-[54px] flex justify-center">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          background
          layout="total, sizes, prev, pager, next"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>
  </section>
</template>
