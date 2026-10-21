<script setup lang="ts">
// 大赛方案页：由原首页大赛内容迁移而来（去掉新闻资讯），参赛作品区沿用 /works 卡片样式
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { workApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { vReveal } from '@/directives/reveal'
import banner1 from '@/assets/images/banner_1.png'
import banner2 from '@/assets/images/banner_2.png'
import banner3 from '@/assets/images/banner_3.png'
import overviewImage from '@/assets/images/img_home_overview.png'
import guideSignup from '@/assets/images/img_home_01.png'
import guideMaterials from '@/assets/images/img_home_02.png'
import guideEntry from '@/assets/images/img_home_03.png'

const router = useRouter()
const authStore = useAuthStore()

const banners = [
  { image: banner1, alt: '2026年云南大学首届人工智能创新应用大赛', url: '/competition.html' },
  { image: banner2, alt: '数启云大 智创未来', url: '/competition.html' },
  { image: banner3, alt: '基于大模型的校园生活智能体创新应用', url: '/competition.html' }
]

const timeline = [
  { title: '大赛报名', date: '2026 年 5 月 15 日 - 6 月 5 日 17:00', icon: '📝', hue: 'blue' },
  { title: '培训赋能', date: '2026 年 5 月 28 日、29 日、6 月 5 日晚上举行', icon: '🎓', hue: 'violet' },
  { title: '提交作品', date: '2026 年 6 月 22 日 17:00 截止', icon: '🚀', hue: 'pink' },
  { title: '作品评审', date: '2026 年 6 月 23 日 - 30 日', icon: '⚖️', hue: 'orange' },
  { title: '获奖公示', date: '2026 年 7 月上旬', icon: '🏆', hue: 'green' }
]

const guides = [
  { title: '报名与作品提交', image: guideSignup, externalUrl: '/page/notes', hasBotton: false },
  { title: '课程资料', image: guideMaterials, path: '/materials', hasBotton: false },
  { title: '报名入口', image: guideEntry, externalUrl: '/admin/teams', hasBotton: true }
]

// 参赛作品（沿用 /works 卡片样式）
const works = ref<any[]>([])
const loading = ref(true)
const pageSize = ref(12)

const votingStatus = ref<any>({
  max_votes: 5,
  used_votes: 0,
  remaining_votes: 5,
  voted_works: [],
  total_works: 0,
  voting_open: true
})

// 绚丽卡片头部渐变（与 /works 一致）
const headerClasses = [
  'bg-gradient-to-br from-[#00c6ff] to-[#0071e3]',
  'bg-gradient-to-br from-[#30d158] to-[#0090ff]',
  'bg-gradient-to-br from-[#6a5cff] to-[#a18cd1]',
  'bg-gradient-to-br from-[#ff9f45] to-[#ff5ca8]'
]

const openGuide = (guide: any) => {
  if (guide.externalUrl) {
    window.open(guide.externalUrl, '_blank', 'noopener,noreferrer')
    return
  }
  if (guide.path) {
    router.push(guide.path)
  }
}

const openCompetition = () => {
  window.open('/competition.html', '_blank')
}

async function fetchWorks() {
  loading.value = true
  try {
    const response = await workApi.list({ page: 1, page_size: pageSize.value })
    works.value = response.data?.items || []
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
      votingStatus.value = await response.json()
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

const goWorks = () => {
  router.push('/works')
}

function getHeaderClass(index: number): string {
  return headerClasses[index % headerClasses.length]
}

onMounted(async () => {
  await fetchWorks()
  if (authStore.isLoggedIn) {
    await fetchVotingStatus()
  }
})
</script>

<template>
  <div class="overflow-hidden bg-transparent">
    <!-- Banner：圆角悬浮大卡片 -->
    <div class="mx-auto max-w-[1280px] px-[16px] pt-[24px]">
      <div class="home-banner anim-fade-up relative h-[420px] overflow-hidden rounded-[28px] shadow-[0_24px_80px_rgba(29,42,68,0.22)] lg:h-[500px]">
        <el-carousel height="100%" :interval="3000" trigger="click" arrow="never" indicator-position="inside">
          <el-carousel-item v-for="(banner, index) in banners" :key="index">
            <a :href="banner.url" target="_blank" rel="noopener noreferrer">
              <img :src="banner.image" :alt="banner.alt" class="h-full w-full object-cover transition-transform duration-700 hover:scale-[1.02]" />
            </a>
          </el-carousel-item>
        </el-carousel>
      </div>
    </div>

    <!-- Main Content -->
    <div class="mx-auto max-w-[1200px] px-[16px] pb-[70px] pt-[80px]">
      <!-- 大赛介绍 -->
      <a href="/competition.html" target="_blank" rel="noopener noreferrer">
        <div v-reveal class="apple-card apple-card-hover grid items-center gap-[48px] p-[40px] lg:grid-cols-[480px_1fr] lg:p-[56px]">
          <div v-reveal="{ direction: 'left', delay: 100 }" class="overflow-hidden rounded-[20px] shadow-[0_16px_48px_rgba(29,42,68,0.16)]">
            <img
              :src="overviewImage"
              alt="基于大模型的校园生活智能体创新应用"
              class="w-full transition-transform duration-700 hover:scale-105"
            />
          </div>
          <div v-reveal="{ direction: 'right', delay: 200 }">
            <p class="mb-[14px] inline-flex items-center gap-[6px] rounded-full bg-[#0071e3]/8 px-[14px] py-[6px] text-[13px] font-[600] text-[#0071e3]">
              <span class="h-[6px] w-[6px] rounded-full bg-gradient-to-r from-[#0090ff] to-[#6a5cff]"></span>
              COMPETITION
            </p>
            <h2 class="text-[32px] font-[700] leading-[42px] lg:text-[40px] lg:leading-[52px]">
              <span class="text-gradient">基于大模型的</span><br />
              <span class="text-[#1d1d1f]">校园生活智能体创新应用</span>
            </h2>
            <p class="mt-[24px] text-[15px] text-[#515154] leading-[30px]">
              为响应国家"人工智能+"行动建设战略部署，在国家教育数字化、AI融合发展等政策指引下，AI人工智能正迈入场景化落地关键期。
              智能体作为融合大模型能力、链接技术与需求的核心载体，在教育、校园服务等领域的应用潜力加速释放。
            </p>
            <p class="mt-[14px] text-[15px] text-[#515154] leading-[30px]">
              在此背景下，为进一步落实学校"提升师生数字素养与技能实施方案"，云南大学联合火山引擎举办首届"火山杯"AI应用创新大赛。
              赛事鼓励学生运用AI能力，在多元场景中探索技术创新应用，为数智化校园建设提供助力。
            </p>
            <p class="mt-[28px]">
              <el-button type="primary" round size="large" class="!px-[32px]" @click.stop="openCompetition">查看更多</el-button>
            </p>
          </div>
        </div>
      </a>

      <!-- 赛程安排 -->
      <div v-reveal class="pt-[72px]">
        <div v-reveal="{ delay: 80 }" class="text-center">
          <h2 class="text-[32px] font-[700] text-[#1d1d1f] lg:text-[40px]">
            <span class="text-gradient">赛程安排</span>
          </h2>
          <p class="mt-[10px] text-[15px] text-[#86868b]">五大赛段，一路晋级</p>
        </div>
        <div class="mt-[44px] grid gap-[20px] md:grid-cols-5">
          <div
            v-for="(item, index) in timeline"
            :key="item.title"
            v-reveal="{ delay: 100 + index * 90 }"
            class="apple-card apple-card-hover group p-[26px] text-center"
          >
            <div
              class="mx-auto flex h-[64px] w-[64px] items-center justify-center rounded-[20px] text-[28px] shadow-[0_10px_28px_rgba(29,42,68,0.14)] transition-transform duration-500 group-hover:scale-110 group-hover:-rotate-6"
              :class="{
                'bg-gradient-to-br from-[#0090ff] to-[#00c6ff]': item.hue === 'blue',
                'bg-gradient-to-br from-[#6a5cff] to-[#a18cd1]': item.hue === 'violet',
                'bg-gradient-to-br from-[#ff5ca8] to-[#ff9f45]': item.hue === 'pink',
                'bg-gradient-to-br from-[#ff9f0a] to-[#ff5ca8]': item.hue === 'orange',
                'bg-gradient-to-br from-[#30d158] to-[#00c6ff]': item.hue === 'green'
              }"
            >
              {{ item.icon }}

            </div>
            <h3 class="mt-[18px] text-[17px] font-[700] text-[#1d1d1f]">{{ item.title }}</h3>
            <p class="mt-[8px] text-[13px] leading-[22px] text-[#86868b]">{{ item.date }}</p>
          </div>
        </div>
      </div>

      <!-- 参赛指南 -->
      <div v-reveal class="pt-[72px]">
        <div v-reveal="{ delay: 80 }" class="text-center">
          <h2 class="text-[32px] font-[700] text-[#1d1d1f] lg:text-[40px]">
            <span class="text-gradient">参赛指南</span>
          </h2>
          <p class="mt-[10px] text-[15px] text-[#86868b]">三步开启你的智能体之旅</p>
        </div>
        <div class="mt-[44px] grid gap-[28px] md:grid-cols-3">
          <button
            v-for="(guide, index) in guides"
            :key="guide.title"
            v-reveal="{ delay: 100 + index * 120, direction: 'scale' }"
            type="button"
            class="apple-card apple-card-hover group relative overflow-hidden border-0 p-0 text-left cursor-pointer"
            @click="openGuide(guide)"
          >
            <div class="relative h-[190px] overflow-hidden">
              <img
                :src="guide.image"
                :alt="guide.title"
                class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
              />
              <div class="absolute inset-0 bg-gradient-to-t from-black/45 via-transparent to-transparent"></div>
              <span
                class="absolute bottom-[14px] left-[18px] rounded-full bg-white/90 px-[14px] py-[5px] text-[13px] font-[600] text-[#1d1d1f] backdrop-blur-sm"
              >
                {{ guide.title }}
              </span>
            </div>
            <div class="p-[22px]">
              <p class="text-[20px] font-[700] text-[#1d1d1f] transition-colors duration-300 group-hover:text-[#0071e3]">
                {{ guide.title }}
              </p>
              <div class="mt-[10px] flex items-center justify-between">
                <p v-if="guide.hasBotton" class="text-[13px] text-[#86868b]">截止时间：6月5日 17:00</p>
                <p v-else class="text-[13px] text-[#86868b]">了解更多</p>
                <span
                  v-if="guide.hasBotton"
                  class="inline-flex items-center rounded-full bg-gradient-to-r from-[#ff5ca8] to-[#ff9f45] px-[18px] py-[7px] text-[13px] font-[600] text-white shadow-[0_6px_18px_rgba(255,92,168,0.35)] transition-transform duration-300 group-hover:scale-105"
                >
                  立即报名
                </span>
                <span
                  v-else
                  class="inline-flex h-[28px] w-[28px] items-center justify-center rounded-full bg-[#0071e3]/8 text-[#0071e3] transition-transform duration-300 group-hover:translate-x-1"
                >
                  →
                </span>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- 参赛作品：沿用 /works 卡片样式 -->
    <section class="pb-[80px]">
      <div class="mx-auto max-w-[1200px] px-[16px]">
        <div v-reveal="{ delay: 60 }" class="text-center">
          <h2 class="text-[32px] font-[700] text-[#1d1d1f] lg:text-[40px]">
            <span class="text-gradient">参赛作品</span>
          </h2>
          <p class="mt-[10px] text-[15px] text-[#86868b]">为喜欢的作品投上一票</p>
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

        <!-- Works Grid：与 /works 一致的渐变头部卡片 -->
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
                <h3 class="line-clamp-3 w-full text-[16px] font-[700] leading-[22px] text-white drop-shadow">
                  {{ work.name }}
                </h3>
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

        <!-- 更多作品 -->
        <div class="mt-[54px] text-center">
          <el-button
            round
            size="large"
            class="!px-[40px]"
            @click="goWorks"
          >
            更多作品 →
          </el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-banner :deep(.el-carousel) {
  height: 100%;
}

.home-banner :deep(.el-carousel__container) {
  height: 100%;
}

.home-banner :deep(.el-carousel__indicators) {
  bottom: 20px;
}

.home-banner :deep(.el-carousel__button) {
  width: 24px;
  height: 5px;
  border-radius: 999px;
  background-color: rgba(255, 255, 255, 0.55);
  opacity: 1;
}

.home-banner :deep(.el-carousel__indicator.is-active .el-carousel__button) {
  width: 36px;
  background-color: #ffffff;
}
</style>
