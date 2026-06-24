<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { workApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import leaderAvatar from '@/assets/images/img_team_01.png'
import memberAvatar from '@/assets/images/img_team_02.png'
import resourceIcon1 from '@/assets/images/img_works_01.png'
import resourceIcon2 from '@/assets/images/img_works_02.png'
import resourceIcon3 from '@/assets/images/img_works_03.png'
import bannerDetail from '@/assets/images/banner_works_detail.png'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const work = ref<any>(null)
const loading = ref(true)
const error = ref('')
const votingStatus = ref<any>(null)
const votedWorks = ref<any[]>([])
const videoVisible = ref(false)

onMounted(async () => {
  await fetchWork()
  if (authStore.isLoggedIn) {
    await fetchVotingStatus()
  }
})

async function fetchWork() {
  loading.value = true
  try {
    const response = await workApi.get(Number(route.params.id))
    work.value = response.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || '加载失败'
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
      votedWorks.value = data.voted_works || []
    }
  } catch (e) {
    console.error(e)
  }
}

async function handleVote() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }

  if (hasVoted()) return

  try {
    await workApi.vote(work.value.id)
    work.value.vote_count = (work.value.vote_count || 0) + 1
    await fetchVotingStatus()
    ElMessage.success('投票成功')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '投票失败')
  }
}

function hasVoted(): boolean {
  return votedWorks.value.some((w: any) => w.id === work.value?.id)
}

function openUrl(url: string) {
  if (url) {
    window.open(url, '_blank', 'noopener,noreferrer')
  }
}

function handleResource(resource: any) {
  if (resource.type === 'video') {
    videoVisible.value = true
    return
  }

  if (resource.type === 'link') {
    openUrl(resource.value)
  } else {
    openUrl(`/${resource.value.replaceAll('\\', '/')}`)
  }
}

function getCleanPath(path: string): string {
  if (!path) return ''
  return '/' + path.replace(/^\.\//, '').replace(/^\//, '')
}

// 获取队伍成员（模拟数据，实际从API获取）
function getMembers() {
  if (work.value?.team_members && work.value.team_members.length > 0) {
    return work.value.team_members
  }
  return [
    { name: '队长', avatar: leaderAvatar },
    { name: '队员', avatar: memberAvatar },
  ]
}

// 获取资源列表
function getResources() {
  if (!work.value) return []

  const resources = []
  if (work.value.agent_url) {
    resources.push({
      title: '智能体URL',
      value: work.value.agent_url,
      buttonText: '打开链接',
      className: 'bg-[#e0f2ff]',
      buttonClass: '!bg-[#2d80ff]',
      icon: resourceIcon1,
      type: 'link'
    })
  }
  if (work.value.pdf_file) {
    resources.push({
      title: 'PDF文档',
      value: work.value.pdf_file,
      buttonText: '查看PDF',
      className: 'bg-[#fff0f3]',
      buttonClass: '!bg-[#ff5959]',
      icon: resourceIcon2,
      type: 'pdf'
    })
  }
  if (work.value.video_file) {
    resources.push({
      title: '演示视频',
      value: work.value.video_file,
      buttonText: '播放视频',
      className: 'bg-[#fff6e5]',
      buttonClass: '!bg-[#ff8d45]',
      icon: resourceIcon3,
      type: 'video'
    })
  }
  return resources
}

// 分割描述文本为段落
function getDescriptionParagraphs() {
  if (!work.value?.description) return []
  return work.value.description.split('\n').filter((p: string) => p.trim())
}
</script>

<template>
  <section class="work-detail-page min-h-[calc(100vh-200px)] bg-white pb-[82px] pt-[27px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px] xl:px-0">
      <div class="detail-breadcrumb flex items-center gap-[7px] text-[#777]">
        <i class="iconfont icon-shouye text-[#999999]"></i>
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#047eff] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <RouterLink to="/works" class="text-[#047eff] hover:underline">参赛作品</RouterLink>
        <span class="mx-1">/</span>
        <span>作品详情</span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="mt-[36px] text-center py-16">
        <div class="inline-block w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-3 text-gray-500">加载中...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="mt-[36px] text-center py-16">
        <p class="text-red-500">{{ error }}</p>
      </div>

      <!-- Content -->
      <article v-else-if="work" class="mt-[19px] overflow-hidden rounded-[12px] bg-white shadow-[0_4px_18px_rgba(24,42,78,0.12)]">
        <!-- Header -->
        <div class="relative h-[210px] overflow-hidden bg-[#e7f8ff]">
          <img :src="bannerDetail" alt="" class="absolute inset-0 h-full w-full object-cover" />
          <span class="absolute left-0 top-0 flex h-[37px] w-[71px] items-center justify-center rounded-br-[14px] bg-[#087fff] text-[22px] font-[800] leading-none text-white">
            {{ work.id }}
          </span>

          <div class="absolute left-[80px] top-[77px] max-w-[720px]">
            <h1 class="text-[28px] font-[800] leading-[34px] text-[#004385]">{{ work.name }}</h1>
            <div class="mt-[15px] flex items-center gap-[31px] text-[16px] leading-[20px] text-[#666]">
              <span class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-zongzhiduiwu text-[22px] text-[#999]"></i>
                {{ work.team_name || '未知队伍' }}
              </span>
              <span class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-icon- text-[22px] text-[#999]"></i>
                {{ work.view_count || 0 }}
              </span>
            </div>
          </div>

          <div class="absolute right-[72px] top-[35px] flex flex-col items-center">
            <div class="flex h-[103px] w-[103px] flex-col items-center justify-center rounded-full bg-white text-center">
              <strong class="text-[32px] font-[800] leading-[38px] text-[#ff3c3c]">{{ work.vote_count || 0 }}</strong>
              <span class="mt-[7px] text-[16px] font-[400] leading-[16px] text-[#ff3c3c]">票</span>
            </div>
            <el-button
              type="danger"
              round
              class="vote-action mt-[10px] !h-[40px] !w-[133px] !border-0 !bg-[#ff5959] !px-0 !text-[18px] !font-[500]"
              :disabled="hasVoted()"
              @click="handleVote"
            >
              <i class="iconfont icon-toupiao mr-[4px] text-[18px]"></i>
              {{ hasVoted() ? '已投票' : '我要投票' }}
            </el-button>
          </div>
        </div>

        <!-- Description -->
        <div class="pl-[39px] pr-[12px] pb-[31px] pt-[17px]">
          <h2 class="text-[20px] font-[700] leading-[34px] text-[#007dff]">作品描述</h2>
          <div class="mt-[12px] space-y-[14px] text-[16px] leading-[28px] text-[#5f5f5f] detail-scroll max-h-[303px] overflow-y-auto">
            <p v-for="(paragraph, idx) in getDescriptionParagraphs()" :key="idx" class="indent-[2em]">
              {{ paragraph }}
            </p>
          </div>
        </div>
      </article>

      <!-- Team Members -->
      <section v-if="work" class="mt-[24px] rounded-[12px] bg-white px-[36px] pb-[34px] pt-[17px] shadow-[0_4px_18px_rgba(24,42,78,0.12)]">
        <h2 class="text-[20px] font-[700] leading-[34px] text-[#007dff]">队伍成员</h2>
        <div class="mt-[9px] flex flex-wrap gap-[14px]">
          <div
            v-for="(member, idx) in getMembers()"
            :key="idx"
            class="flex h-[63px] w-[177px] items-center rounded-[8px] bg-[#f3f3f3] px-[14px]"
          >
            <img :src="member.avatar || memberAvatar" :alt="member.name" class="h-[44px] w-[44px] shrink-0 rounded-full" />
            <div class="ml-[14px] min-w-0">
              <p class="truncate text-[16px] font-[700] leading-[22px] text-[#191919]">{{ member.name || member.student_id || '成员' }}</p>
              <p class="mt-[1px] text-[14px] leading-[20px] text-[#777]">{{ member.is_leader ? '队长' : '队员' }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Resources -->
      <section v-if="work && getResources().length > 0" class="mt-[24px] rounded-[12px] bg-white px-[36px] pb-[33px] pt-[17px] shadow-[0_4px_18px_rgba(24,42,78,0.12)]">
        <h2 class="text-[20px] font-[700] leading-[34px] text-[#007dff]">作品资源</h2>
        <div class="mt-[8px] grid gap-x-[23px] gap-y-[24px] lg:grid-cols-2">
          <div
            v-for="resource in getResources()"
            :key="resource.title"
            class="resource-card flex min-h-[80px] items-center rounded-[8px] px-[15px]"
            :class="resource.className"
          >
            <img :src="resource.icon" class="w-[55px] h-[55px] rounded-full" />
            <div class="ml-[15px] min-w-0 flex-1">
              <p class="text-[16px] font-[800] leading-[22px] text-[#1d1d1d] line-clamp-1">{{ resource.title }}</p>
              <p class="mt-[3px] truncate text-[14px] leading-[20px] text-[#666]">{{ resource.value }}</p>
            </div>
            <el-button
              round
              class="resource-button ml-[16px] !h-[40px] !w-[104px] !border-0 !px-0 !text-[16px] !font-[800] !text-white"
              :class="resource.buttonClass"
              @click="handleResource(resource)"
            >
              {{ resource.buttonText }}
            </el-button>
          </div>
        </div>
      </section>
    </div>

    <!-- Video Dialog -->
    <el-dialog v-model="videoVisible" title="演示视频" width="780px" class="video-dialog" destroy-on-close>
      <div class="flex min-h-[360px] items-center justify-center rounded-[8px] bg-[#111827]">
        <video
          v-if="work?.video_file"
          :src="'/' + work.video_file.replaceAll('\\', '/')"
          controls
          class="max-h-[360px] w-full rounded-[8px]"
        >
          您的浏览器不支持视频播放
        </video>
        <span v-else class="text-[16px] text-white">暂无视频</span>
      </div>
    </el-dialog>
  </section>
</template>

<style scoped>
.work-detail-page {
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 100%);
}

.detail-breadcrumb {
  font-size: 14px;
  line-height: 20px;
}

.detail-scroll::-webkit-scrollbar,
.detail-scroll::-webkit-scrollbar-thumb,
.detail-scroll::-webkit-scrollbar-thumb:hover,
.detail-scroll::-webkit-scrollbar-thumb:active {
  background: #0a7fff;
  height: 4px;
  width: 5px;
  border-radius: 3px;
}

.detail-scroll::-webkit-scrollbar-track {
  background: #f0f0f0;
  width: 5px;
  border-radius: 3px;
}

.vote-action.is-disabled {
  opacity: 0.72;
}

.resource-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.resource-card:hover {
  box-shadow: 0 10px 22px rgba(34, 96, 170, 0.12);
  transform: translateY(-2px);
}

.resource-button {
  transition: filter 0.2s ease, transform 0.2s ease;
}

.resource-button:hover {
  filter: brightness(1.04);
  transform: translateY(-1px);
}

.video-dialog :deep(.el-dialog__body) {
  padding-top: 10px;
}

@media (max-width: 1023px) {
  .work-detail-page {
    padding-top: 20px;
  }
}

@media (max-width: 767px) {
  .work-detail-page article > div:first-child {
    height: 300px;
  }

  .work-detail-page article > div:first-child > div:nth-of-type(1) {
    left: 24px;
    top: 70px;
    right: 24px;
  }

  .work-detail-page article > div:first-child > div:nth-of-type(2) {
    left: 24px;
    right: auto;
    top: 166px;
    align-items: flex-start;
  }

  .detail-scroll {
    max-height: none;
    padding-left: 22px;
    padding-right: 22px;
  }

  .resource-card {
    align-items: flex-start;
    flex-wrap: wrap;
    padding-bottom: 18px;
    padding-top: 18px;
  }

  .resource-button {
    margin-left: 69px;
    margin-top: 14px;
  }
}
</style>