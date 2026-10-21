<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { workApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import leaderAvatar from '@/assets/images/img_team_01.png'
import memberAvatar from '@/assets/images/img_team_02.png'
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
      hue: 'blue',
      type: 'link'
    })
  }
  if (work.value.pdf_file) {
    resources.push({
      title: 'PDF文档',
      value: work.value.pdf_file,
      buttonText: '查看PDF',
      hue: 'pink',
      type: 'pdf'
    })
  }
  if (work.value.video_file) {
    resources.push({
      title: '演示视频',
      value: work.value.video_file,
      buttonText: '播放视频',
      hue: 'orange',
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
  <section class="min-h-[calc(100vh-200px)] pb-[80px] pt-[28px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px]">
      <div class="flex items-center gap-[6px] text-[14px] text-[#86868b]">
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#0071e3] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <RouterLink to="/works" class="text-[#0071e3] hover:underline">参赛作品</RouterLink>
        <span class="mx-1">/</span>
        <span>作品详情</span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="mt-[48px] text-center py-16">
        <div class="inline-block h-10 w-10 animate-spin rounded-full border-4 border-[#0071e3]/20 border-t-[#0071e3]"></div>
        <p class="mt-3 text-[#86868b]">加载中...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="mt-[48px] text-center py-16">
        <p class="text-[#ff3b30]">{{ error }}</p>
      </div>

      <!-- Content -->
      <article v-else-if="work" class="anim-fade-up mt-[20px] overflow-hidden rounded-[24px] border border-white/70 shadow-[var(--shadow-card)]">
        <!-- 绚丽渐变 Header -->
        <div class="relative h-[240px] overflow-hidden bg-gradient-to-br from-[#0090ff] via-[#6a5cff] to-[#ff5ca8]">
          <img
            :src="bannerDetail"
            alt=""
            class="absolute inset-0 h-full w-full object-cover opacity-30 mix-blend-overlay"
          />
          <div class="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white/15 blur-3xl"></div>
          <div class="pointer-events-none absolute -bottom-24 left-1/3 h-56 w-56 rounded-full bg-white/10 blur-3xl"></div>

          <span class="absolute left-[24px] top-[24px] rounded-full bg-white/20 px-[16px] py-[4px] text-[15px] font-[800] text-white backdrop-blur-sm">
            #{{ work.id }}
          </span>

          <div class="absolute left-[32px] top-[86px] max-w-[640px]">
            <h1 class="text-[28px] font-[800] leading-[38px] text-white drop-shadow-lg lg:text-[32px]">
              {{ work.name }}
            </h1>
            <div class="mt-[14px] flex flex-wrap items-center gap-[24px] text-[15px] text-white/85">
              <span class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-zongzhiduiwu text-[20px]"></i>
                {{ work.team_name || '未知队伍' }}
              </span>
              <span class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-icon- text-[20px]"></i>
                {{ work.view_count || 0 }} 浏览
              </span>
            </div>
          </div>

          <!-- 投票胶囊 -->
          <div class="absolute right-[32px] top-[40px] flex flex-col items-center">
            <div class="flex h-[104px] w-[104px] flex-col items-center justify-center rounded-full bg-white/95 text-center shadow-[0_16px_40px_rgba(0,0,0,0.25)] backdrop-blur">
              <strong class="bg-gradient-to-r from-[#ff5ca8] to-[#ff3b30] bg-clip-text text-[30px] font-[800] leading-[36px] text-transparent">
                {{ work.vote_count || 0 }}
              </strong>
              <span class="mt-[2px] text-[14px] text-[#86868b]">票</span>
            </div>
            <el-button
              round
              class="mt-[12px] !h-[40px] !w-[132px] !border-0 !bg-white !text-[15px] !font-[700] !text-[#0071e3] shadow-[0_8px_24px_rgba(0,0,0,0.2)] hover:!bg-white/90"
              :disabled="hasVoted()"
              @click="handleVote"
            >
              <i class="iconfont icon-toupiao mr-[4px] text-[17px]"></i>
              {{ hasVoted() ? '已投票' : '我要投票' }}
            </el-button>
          </div>
        </div>

        <!-- Description -->
        <div class="bg-white/85 px-[32px] pb-[32px] pt-[22px] backdrop-blur-xl lg:px-[40px]">
          <h2 class="flex items-center gap-[10px] text-[20px] font-[700] text-[#1d1d1f]">
            <span class="inline-block h-[22px] w-[5px] rounded-full bg-gradient-to-b from-[#0090ff] to-[#6a5cff]"></span>
            作品描述
          </h2>
          <div class="detail-scroll mt-[14px] max-h-[303px] space-y-[14px] overflow-y-auto pr-2 text-[16px] leading-[30px] text-[#515154]">
            <p v-for="(paragraph, idx) in getDescriptionParagraphs()" :key="idx">
              {{ paragraph }}
            </p>
          </div>
        </div>
      </article>

      <!-- Team Members -->
      <section v-if="work" class="anim-fade-up apple-card mt-[24px] px-[32px] pb-[34px] pt-[24px] lg:px-[40px]">
        <h2 class="flex items-center gap-[10px] text-[20px] font-[700] text-[#1d1d1f]">
          <span class="inline-block h-[22px] w-[5px] rounded-full bg-gradient-to-b from-[#6a5cff] to-[#ff5ca8]"></span>
          队伍成员
        </h2>
        <div class="anim-stagger mt-[16px] flex flex-wrap gap-[16px]">
          <div
            v-for="(member, idx) in getMembers()"
            :key="idx"
            class="flex h-[64px] items-center rounded-[18px] bg-white px-[16px] shadow-[0_2px_12px_rgba(29,42,68,0.06)] ring-1 ring-black/[0.03] transition-all duration-300 hover:-translate-y-1 hover:shadow-[var(--shadow-card-hover)]"
          >
            <img :src="member.avatar || memberAvatar" :alt="member.name" class="h-[44px] w-[44px] shrink-0 rounded-full ring-2 ring-white shadow" />
            <div class="ml-[13px] min-w-0">
              <p class="truncate text-[15px] font-[700] text-[#1d1d1f]">{{ member.name || member.student_id || '成员' }}</p>
              <p class="mt-[1px] text-[13px] text-[#86868b]">
                <span :class="member.is_leader ? 'text-[#ff9f0a] font-[600]' : ''">{{ member.is_leader ? '队长' : '队员' }}</span>
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Resources -->
      <section v-if="work && getResources().length > 0" class="anim-fade-up apple-card mt-[24px] px-[32px] pb-[34px] pt-[24px] lg:px-[40px]">
        <h2 class="flex items-center gap-[10px] text-[20px] font-[700] text-[#1d1d1f]">
          <span class="inline-block h-[22px] w-[5px] rounded-full bg-gradient-to-b from-[#ff5ca8] to-[#ff9f45]"></span>
          作品资源
        </h2>
        <div class="anim-stagger mt-[14px] grid gap-x-[24px] gap-y-[18px] lg:grid-cols-2">
          <div
            v-for="resource in getResources()"
            :key="resource.title"
            class="group flex min-h-[84px] cursor-pointer items-center rounded-[18px] px-[18px] transition-all duration-300 hover:-translate-y-1"
            :class="{
              'bg-[#0071e3]/6 hover:bg-[#0071e3]/10 hover:shadow-[0_12px_32px_rgba(0,113,227,0.18)]': resource.hue === 'blue',
              'bg-[#ff5ca8]/6 hover:bg-[#ff5ca8]/10 hover:shadow-[0_12px_32px_rgba(255,92,168,0.18)]': resource.hue === 'pink',
              'bg-[#ff9f0a]/8 hover:bg-[#ff9f0a]/12 hover:shadow-[0_12px_32px_rgba(255,159,10,0.2)]': resource.hue === 'orange'
            }"
            @click="handleResource(resource)"
          >
            <div
              class="flex h-[52px] w-[52px] shrink-0 items-center justify-center rounded-[16px] text-[22px] text-white shadow-lg transition-transform duration-300 group-hover:scale-110"
              :class="{
                'bg-gradient-to-br from-[#0090ff] to-[#00c6ff]': resource.hue === 'blue',
                'bg-gradient-to-br from-[#ff5ca8] to-[#ff9f45]': resource.hue === 'pink',
                'bg-gradient-to-br from-[#ff9f0a] to-[#ff5ca8]': resource.hue === 'orange'
              }"
            >
              <span v-if="resource.type === 'link'">🔗</span>
              <span v-else-if="resource.type === 'pdf'">📄</span>
              <span v-else>🎬</span>
            </div>
            <div class="ml-[16px] min-w-0 flex-1">
              <p class="text-[16px] font-[700] text-[#1d1d1f] line-clamp-1">{{ resource.title }}</p>
              <p class="mt-[3px] truncate text-[13px] text-[#86868b]">{{ resource.value }}</p>
            </div>
            <span
              class="ml-[16px] inline-flex h-[36px] items-center rounded-full px-[20px] text-[14px] font-[600] text-white shadow-md transition-transform duration-300 group-hover:scale-105"
              :class="{
                'bg-gradient-to-r from-[#0090ff] to-[#00c6ff]': resource.hue === 'blue',
                'bg-gradient-to-r from-[#ff5ca8] to-[#ff9f45]': resource.hue === 'pink',
                'bg-gradient-to-r from-[#ff9f0a] to-[#ff5ca8]': resource.hue === 'orange'
              }"
            >
              {{ resource.buttonText }}
            </span>
          </div>
        </div>
      </section>
    </div>

    <!-- Video Dialog -->
    <el-dialog v-model="videoVisible" title="演示视频" width="780px" destroy-on-close>
      <div class="flex min-h-[360px] items-center justify-center rounded-[16px] bg-[#0b0b0f]">
        <video
          v-if="work?.video_file"
          :src="'/' + work.video_file.replaceAll('\\', '/')"
          controls
          class="max-h-[360px] w-full rounded-[16px]"
        >
          您的浏览器不支持视频播放
        </video>
        <span v-else class="text-[16px] text-white">暂无视频</span>
      </div>
    </el-dialog>
  </section>
</template>

<style scoped>
.detail-scroll::-webkit-scrollbar {
  width: 6px;
}

.detail-scroll::-webkit-scrollbar-thumb {
  background: rgba(0, 113, 227, 0.3);
  border-radius: 999px;
}

@media (max-width: 767px) {
  .anim-fade-up article > div:first-child {
    height: 320px;
  }
}
</style>
