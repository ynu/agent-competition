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

const headerClasses = ['work-header-cyan', 'work-header-green', 'work-header-blue', 'work-header-orange']

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
  <section class="works-page min-h-[calc(100vh-200px)] bg-white pb-[72px] pt-[24px]">
    <div class="mx-auto max-w-[1200px] px-[16px]">
      <div class="works-breadcrumb flex items-center gap-[6px] text-[14px] text-[#666] font-[400]">
        <i class="iconfont icon-shouye text-[#999999]"></i>
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#047EFF] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <span>参赛作品</span>
      </div>

      <!-- 搜索框 -->
      <div class="mt-[24px] flex justify-center">
        <el-input
          v-model="keyword"
          clearable
          placeholder="请输入关键字"
          class="works-search w-[460px]"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        >
          <template #prefix>
            <el-icon class="text-[#b8bdc6]"><Search /></el-icon>
          </template>
          <template #append>
            <el-button type="primary" class="!w-[86px]" @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="mt-[36px] text-center py-16">
        <div class="inline-block w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-3 text-gray-500">加载中...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="works.length === 0" class="mt-[36px] text-center py-16">
        <p class="text-gray-500">暂无参赛作品</p>
      </div>

      <!-- Works Grid -->
      <div v-else class="mt-[40px] grid grid-cols-1 gap-x-[34px] gap-y-[36px] sm:grid-cols-2 lg:grid-cols-4">
        <article
          v-for="(work, index) in works"
          :key="work.id"
          class="work-card cursor-pointer overflow-hidden rounded-[10px] bg-white shadow-[0_4px_18px_rgba(28,51,84,0.10)] transition-transform duration-200 hover:-translate-y-[4px]"
          role="button"
          tabindex="0"
          @click="openWorkDetail(work)"
          @keydown.enter="openWorkDetail(work)"
          @keydown.space.prevent="openWorkDetail(work)"
        >
          <div class="relative h-[104px] overflow-hidden" :class="getHeaderClass(index)">
            <div class="absolute left-[14px] top-[19px] text-[76px] text-white/35 font-[900] leading-none">Ai</div>
            <div class="flex items-center ml-[60px] mr-[5px] h-full py-[5px] box-border w-[calc(100%-65px)]">
              <h2 class="relative z-10 line-clamp-4 w-full text-[18px] text-[#005cae] font-[800] leading-[24px]">
                {{ work.name }}
              </h2>
            </div>
          </div>

          <div class="px-[18px] pb-[22px] pt-[20px]">
            <dl class="space-y-[8px] text-[14px] text-[#626b78] leading-[18px]">
              <div class="flex w-full">
                <dt class="tracking-[1px] w-[75px]">参赛队伍：</dt>
                <dd class="w-[calc(100%-75px)] line-clamp-1">{{ work.team_name }}</dd>
              </div>
              <div class="flex w-full">
                <dt class="tracking-[1px] w-[75px]">当前票数：</dt>
                <dd class="w-[calc(100%-75px)] line-clamp-1">{{ work.vote_count || 0 }}</dd>
              </div>
            </dl>

            <div class="mt-[24px] flex justify-center">
              <el-button
                round
                plain
                :type="hasVoted(work.id) ? 'info' : 'primary'"
                :disabled="hasVoted(work.id)"
                class="vote-button !h-[40px] !min-w-[142px] !text-[18px] !font-[400]"
                @click="handleVote(work, $event)"
                @keydown.enter.stop
                @keydown.space.stop
              >
                <i class="iconfont icon-toupiao text-[20px] mr-2"></i>
                {{ hasVoted(work.id) ? '票已投完' : '我要投票' }}
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
          class="works-pagination"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
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

.works-search :deep(.el-input__wrapper) {
  height: 40px;
  border-radius: 4px 0 0 4px;
  background-color: #f5f5f5;
  box-shadow: none;
}

.works-search :deep(.el-input-group__append) {
  overflow: hidden;
  border-radius: 0 4px 4px 0;
  background-color: #0d8bff;
  box-shadow: none;
}

.works-search :deep(.el-input-group__append .el-button) {
  height: 40px;
  border: 0;
  border-radius: 0;
  background-color: #0d8bff;
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
}

/*
.work-card {
  min-height: 314px;
}
*/

.work-header-cyan {
  background: linear-gradient(105deg, #d8fbff 0%, #bff9ff 52%, #cff8ff 100%);
}

.work-header-green {
  background: linear-gradient(105deg, #d9fff7 0%, #bffbee 52%, #cef9ef 100%);
}

.work-header-blue {
  background: linear-gradient(105deg, #d9ebff 0%, #c8dcff 52%, #d8e6ff 100%);
}

.work-header-orange {
  background: linear-gradient(105deg, #ffe9d4 0%, #ffd9b8 52%, #ffe4ca 100%);
}

.vote-button :deep(.el-icon) {
  font-size: 18px;
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