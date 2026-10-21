<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { contentApi, workApi } from '@/api'
import { vReveal } from '@/directives/reveal'
import banner1 from '@/assets/images/banner_1.png'
import banner2 from '@/assets/images/banner_2.png'
import banner3 from '@/assets/images/banner_3.png'
import overviewImage from '@/assets/images/img_home_overview.png'
import guideSignup from '@/assets/images/img_home_01.png'
import guideMaterials from '@/assets/images/img_home_02.png'
import guideEntry from '@/assets/images/img_home_03.png'
import homeNewsImage from '@/assets/images/banner_works_detail.png'
import work01 from '@/assets/images/img_list01.png'
import work02 from '@/assets/images/img_list02.png'
import work03 from '@/assets/images/img_list03.png'
import work04 from '@/assets/images/img_list04.png'

const workImages = [work01, work02, work03, work04]

const router = useRouter()
const articles = ref<any[]>([])
const works = ref<any[]>([])
const loading = ref(true)
const error = ref('')

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

const defaultGuideUrl = 'https://itc.ynu.edu.cn/info/1013/1799.htm'

const guides = [
  { title: '报名与作品提交', image: guideSignup, externalUrl: '/page/notes', hasBotton: false, hue: 'from-[#0090ff] to-[#00c6ff]' },
  { title: '课程资料', image: guideMaterials, path: '/materials', hasBotton: false, hue: 'from-[#6a5cff] to-[#a18cd1]' },
  { title: '报名入口', image: guideEntry, externalUrl: '/admin/teams', hasBotton: true, hue: 'from-[#ff5ca8] to-[#ff9f45]' }
]

const openWorkDetail = (work: any) => {
  router.push(`/works/${work.id}`)
}

const openGuide = (guide: any) => {
  if (guide.externalUrl) {
    window.open(guide.externalUrl, '_blank', 'noopener,noreferrer')
    return
  }
  if (guide.path) {
    router.push(guide.path)
  }
}

const openArticle = (article: any) => {
  router.push(`/news/${article.id}`)
}

const openCompetition = () => {
  window.open('/competition.html', '_blank')
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return { day: '01', month: '2026-01' }
  const date = new Date(dateStr)
  return {
    day: date.getDate().toString().padStart(2, '0'),
    month: `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`
  }
}

onMounted(async () => {
  try {
    const [articlesRes, worksRes] = await Promise.all([
      contentApi.latestArticles(5),
      workApi.list({ page_size: 8 })
    ])
    // 获取文章列表
    articles.value = articlesRes.data || []
    // 获取作品列表
    if (worksRes.data) {
      works.value = worksRes.data.items || worksRes.data || []
    } else {
      works.value = []
    }
  } catch (e: any) {
    console.error('HomePage error:', e)
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
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

    <!-- 新闻资讯 -->
    <div class="py-[80px]">
      <div class="mx-auto max-w-[1200px] px-[16px]">
        <div v-reveal="{ delay: 60 }" class="text-center">
          <h2 class="text-[32px] font-[700] text-[#1d1d1f] lg:text-[40px]">
            <span class="text-gradient">新闻资讯</span>
          </h2>
          <p class="mt-[10px] text-[15px] text-[#86868b]">大赛动态，一手掌握</p>
        </div>

        <div v-if="loading" class="mt-[44px] text-center py-12">
          <div class="inline-block h-10 w-10 animate-spin rounded-full border-4 border-[#0071e3]/20 border-t-[#0071e3]"></div>
        </div>
        <template v-else>
          <div class="mt-[44px] grid gap-[28px] lg:grid-cols-[500px_1fr]">
            <!-- Featured Article -->
            <div
              v-if="articles.length > 0"
              v-reveal="{ direction: 'left' }"
              class="apple-card apple-card-hover group cursor-pointer overflow-hidden p-0"
              @click="openArticle(articles[0])"
            >
              <div class="h-[280px] overflow-hidden">
                <img
                  :src="articles[0].cover_image || homeNewsImage"
                  alt="featured article"
                  class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
                />
              </div>
              <div class="p-[24px]">
                <h3 class="line-clamp-1 text-[19px] font-[700] text-[#1d1d1f] transition-colors duration-300 group-hover:text-[#0071e3]">
                  {{ articles[0].title }}
                </h3>
                <p class="mt-[10px] line-clamp-2 text-[14px] text-[#86868b] leading-[24px]">
                  {{ articles[0].summary || articles[0].content?.substring(0, 100) || '暂无摘要' }}
                </p>
              </div>
            </div>
            <!-- Article List -->
            <div class="grid content-start gap-[14px]">
              <button
                v-for="(article, index) in articles.slice(1)"
                :key="article.id"
                v-reveal="{ delay: index * 90, direction: 'right' }"
                type="button"
                class="news-item apple-card group grid grid-cols-[74px_1fr] items-center gap-[18px] border-0 p-[16px] text-left cursor-pointer hover:shadow-[var(--shadow-card-hover)]"
                @click="openArticle(article)"
              >
                <div
                  class="news-date flex h-[70px] w-[74px] flex-col items-center justify-center rounded-[16px] text-white transition-all duration-300"
                >
                  <div class="text-[24px] font-[800] leading-[30px]">{{ formatDate(article.created_at).day }}</div>
                  <div class="text-[12px] opacity-85">{{ formatDate(article.created_at).month }}</div>
                </div>
                <div class="min-w-0">
                  <h3 class="line-clamp-1 text-[16px] font-[600] text-[#1d1d1f] transition-colors duration-300 group-hover:text-[#0071e3]">
                    {{ article.title }}
                  </h3>
                  <p class="mt-[6px] line-clamp-2 text-[13px] text-[#86868b] leading-[21px]">
                    {{ article.summary || article.content?.substring(0, 100) || '暂无摘要' }}
                  </p>
                </div>
              </button>
            </div>
          </div>
          <div class="mt-[44px] text-center">
            <el-button round size="large" class="!px-[32px]" @click="router.push('/news')">更多新闻 →</el-button>
          </div>
        </template>
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

    <!-- 参赛作品：清新浅色段 -->
    <div class="relative py-[80px]">
      <!-- 柔和薄雾背景 -->
      <div class="absolute inset-0 bg-gradient-to-b from-white via-[#eef6ff] to-[#f7f4ff]"></div>
      <div class="pointer-events-none absolute left-[8%] top-[16%] h-56 w-56 rounded-full bg-[#9bd8ff]/35 blur-3xl"></div>
      <div class="pointer-events-none absolute right-[10%] top-[30%] h-48 w-48 rounded-full bg-[#c9b8ff]/35 blur-3xl"></div>
      <div class="pointer-events-none absolute bottom-[10%] left-[40%] h-44 w-44 rounded-full bg-[#ffc9e2]/30 blur-3xl"></div>

      <div class="relative mx-auto max-w-[1200px] px-[16px]">
        <div v-reveal="{ delay: 60 }" class="text-center">
          <h2 class="text-[32px] font-[700] text-[#1d1d1f] lg:text-[40px]">
            <span class="text-gradient">参赛作品</span>
          </h2>
          <p class="mt-[10px] text-[15px] text-[#86868b]">来自同学们的奇思妙想</p>
        </div>

        <div v-if="loading" class="mt-[44px] text-center py-12">
          <div class="inline-block h-10 w-10 animate-spin rounded-full border-4 border-[#0071e3]/15 border-t-[#0071e3]"></div>
          <p class="mt-3 text-[#86868b]">加载中...</p>
        </div>
        <div v-else class="mt-[44px] grid gap-x-[24px] gap-y-[24px] sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="(work, index) in works"
            :key="work.id"
            v-reveal="{ delay: (index % 4) * 100 }"
            class="group cursor-pointer overflow-hidden rounded-[20px] border border-white bg-white/80 shadow-[0_4px_24px_rgba(120,150,220,0.12)] backdrop-blur transition-shadow duration-500 hover:shadow-[0_20px_50px_rgba(120,150,220,0.24)]"
            @click="openWorkDetail(work)"
          >
            <div class="relative">
              <span
                class="absolute left-0 top-0 z-10 rounded-br-[14px] rounded-tl-[20px] bg-gradient-to-r from-[#4d9df0] to-[#6a5cff] px-[14px] py-[5px] text-[14px] font-[800] text-white shadow-[0_4px_14px_rgba(106,92,255,0.3)]"
              >
                {{ work.id }}
              </span>
              <div class="h-[110px] overflow-hidden bg-gradient-to-br from-[#e3f2ff] via-[#eef0ff] to-[#fdeef8]">
                <img
                  :src="workImages[work.id % 4] || ''"
                  :alt="work.name"
                  class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
                  @error="(e) => { (e.target as HTMLImageElement).style.display = 'none' }"
                />
              </div>
              <div class="absolute inset-x-[16px] bottom-[10px] w-[calc(100%-32px)]">
                <h2 class="line-clamp-3 w-full text-[15px] font-[700] leading-[22px] text-[#1d3a6b] drop-shadow-[0_1px_6px_rgba(255,255,255,0.9)]">
                  {{ work.name }}
                </h2>
              </div>
            </div>
            <div class="space-y-[6px] px-[18px] py-[16px] text-[13px] leading-[20px]">
              <p class="flex items-center justify-between">
                <span class="text-[#a1a1b5]">队伍</span>
                <span class="line-clamp-1 font-[500] text-[#3a3a4a]">{{ work.team_name }}</span>
              </p>
              <p class="flex items-center justify-between">
                <span class="text-[#a1a1b5]">票数</span>
                <span class="font-[700] text-[#4d9df0]">{{ work.vote_count || 0 }}</span>
              </p>
              <p class="flex items-center justify-between">
                <span class="text-[#a1a1b5]">浏览</span>
                <span class="font-[500] text-[#3a3a4a]">{{ work.view_count || 0 }}</span>
              </p>
            </div>
          </div>
        </div>
        <div class="mt-[44px] text-center">
          <el-button
            round
            size="large"
            class="!border-[#4d9df0]/25 !bg-white/85 !px-[32px] !text-[#0071e3] shadow-[0_8px_24px_rgba(120,150,220,0.2)] backdrop-blur hover:!bg-white"
            @click="router.push('/works')"
          >
            更多作品 →
          </el-button>
        </div>
      </div>
    </div>
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

.news-date {
  background: linear-gradient(135deg, #c7c7cc 0%, #a1a1a6 100%);
}

.news-item:hover .news-date {
  background: var(--gradient-blue);
  box-shadow: 0 8px 20px rgba(0, 113, 227, 0.32);
}
</style>
