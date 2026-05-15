<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { contentApi, workApi } from '@/api'
import banner1 from '@/assets/images/banner_1.png'
import banner2 from '@/assets/images/banner_2.png'
import banner3 from '@/assets/images/banner_3.png'
import overviewImage from '@/assets/images/img_home_overview.png'
import guideSignup from '@/assets/images/img_home_01.png'
import guideMaterials from '@/assets/images/img_home_02.png'
import guideEntry from '@/assets/images/img_home_03.png'
import homeNewsImage from '@/assets/images/banner_works_detail.png'
import titleIcon1 from '@/assets/images/img_title_01.png'
import titleIcon2 from '@/assets/images/img_title_02.png'
import titleIcon3 from '@/assets/images/img_title_03.png'
import titleIcon4 from '@/assets/images/img_title_04.png'
import titleIcon5 from '@/assets/images/img_title_05.png'
import timeline01 from '@/assets/images/img_timeline_01.png'
import timeline02 from '@/assets/images/img_timeline_02.png'
import timeline03 from '@/assets/images/img_timeline_03.png'
import timeline04 from '@/assets/images/img_timeline_04.png'
import timelineArrow from '@/assets/images/img_timeline_arrow.png'
import work01 from '@/assets/images/img_list01.png'
import work02 from '@/assets/images/img_list02.png'
import work03 from '@/assets/images/img_list03.png'
import work04 from '@/assets/images/img_list04.png'

const router = useRouter()
const articles = ref<any[]>([])
const works = ref<any[]>([])
const loading = ref(true)
const error = ref('')

const sectionTitleImages: Record<string, any> = {
  '大赛介绍': titleIcon1,
  '赛程安排': titleIcon2,
  '参赛指南': titleIcon5,
  '参赛作品': titleIcon3,
  '新闻资讯': titleIcon4,
}

const SectionTitle = (props: { title: string; center?: boolean }) =>
  h('div', { class: props.center ? 'flex justify-center' : '' }, [
    h('img', {
      src: sectionTitleImages[props.title] || titleIcon1,
      alt: props.title,
      class: 'h-auto w-[258px] object-contain'
    })
  ])

SectionTitle.props = {
  title: { type: String, required: true },
  center: { type: Boolean, default: false }
}

const banners = [
  { image: banner1, alt: '2026年云南大学首届人工智能创新应用大赛', url: '/competition.html' },
  { image: banner2, alt: '数启云大 智创未来', url: '/competition.html' },
  { image: banner3, alt: '基于大模型的校园生活智能体创新应用', url: '/competition.html' }
]

const timeline = [
  { title: '大赛报名', date: '2026 年 5 月 15 日 - 6 月 5 日 17:00', icon: timeline01, active: true },
  { title: '培训赋能', date: '2026 年 5 月 28 日、29 日、6 月 5 日晚上举行', icon: timeline02 },
  { title: '提交作品', date: '2026 年 6 月 22 日 17:00 截止', icon: timeline03, active: true },
  { title: '作品评审', date: '2026 年6 月 23 日 - 30 日', icon: timeline04 },
  { title: '获奖公示', date: '2026 年 7 月上旬', icon: timeline04 }
]

const defaultGuideUrl = 'https://itc.ynu.edu.cn/info/1013/1799.htm'

const guides = [
  { title: '报名与作品提交', image: guideSignup, externalUrl: '/page/notes', hasBotton: false },
  { title: '课程资料', image: guideMaterials, path: '/materials', hasBotton: false },
  { title: '报名入口', image: guideEntry, externalUrl: '/admin/teams', hasBotton: true }
]

const workImages = [work01, work02, work03, work04]

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
  <div class="overflow-hidden bg-white">
    <!-- Banner -->
    <div class="home-banner h-[500px] overflow-hidden bg-[#07148f]">
      <el-carousel height="500px" :interval="2500" trigger="click" arrow="never" indicator-position="inside">
        <el-carousel-item v-for="(banner, index) in banners" :key="index">
          <a :href="banner.url" target="_blank" rel="noopener noreferrer">
            <img :src="banner.image" :alt="banner.alt" class="h-full w-full object-cover" />
          </a>
        </el-carousel-item>
      </el-carousel>
    </div>

    <!-- Main Content -->
    <div class="bg-[url('@/assets/images/bg_home_01.png')] bg-no-repeat bg-cover bg-top pb-[58px] pt-[54px]">
      <div class="mx-auto max-w-[1200px]">
        <!-- 大赛介绍 -->
        <a href="/competition.html" target="_blank" rel="noopener noreferrer">
          <div class="grid items-center gap-[48px] lg:grid-cols-[520px_1fr]">
            <img :src="overviewImage" alt="基于大模型的校园生活智能体创新应用" class="w-full rounded-[2px]" />
            <div>
              <component :is="() => SectionTitle({ title: '大赛介绍', center: false })" />
              <p class="mt-[24px] text-[15px] text-[#5d6472] leading-[30px]">
                为响应国家"人工智能+"行动建设战略部署，在国家教育数字化、AI融合发展等政策指引下，AI人工智能正迈入场景化落地关键期。
                智能体作为融合大模型能力、链接技术与需求的核心载体，在教育、校园服务等领域的应用潜力加速释放。
              </p>
              <p class="mt-[14px] text-[15px] text-[#5d6472] leading-[30px]">
                在此背景下，为进一步落实学校"提升师生数字素养与技能实施方案"，云南大学联合火山引擎举办首届"火山杯"AI应用创新大赛。
                赛事鼓励学生运用AI能力，在多元场景中探索技术创新应用，为数智化校园建设提供助力。
              </p>
              <p class="mt-[24px]">
                <el-button type="primary" round @click.stop="openCompetition">查看更多</el-button>
              </p>
            </div>
          </div>
        </a>

        <!-- 赛程安排 -->
        <div class="pt-[62px]">
          <component :is="() => SectionTitle({ title: '赛程安排', center: true })" />
          <div class="mt-[30px] rounded-[12px] bg-white/92 px-[66px] py-[50px] shadow-[0_18px_45px_rgba(42,126,255,0.10)]">
            <div class="relative grid gap-[26px] md:grid-cols-5">
              <div class="absolute left-[11%] right-[11%] top-[150px] hidden border-t border-dashed border-[#1b8cff] md:block" />
              <div v-for="(item, index) in timeline" :key="item.title" class="relative text-center">
                <img :src="item.icon" :alt="item.title" class="h-[155px] w-full rounded-t-[12px] object-contain" />
                <img
                  v-if="index < timeline.length - 1"
                  :src="timelineArrow"
                  alt=""
                  class="absolute right-[-35px] top-[36px] hidden h-[50px] w-[50px] object-contain md:block"
                />
                <h3 class="mt-[18px] text-[18px] font-[700]" :class="item.active ? 'text-[#ff8832]' : 'text-[#1687ff]'">
                  {{ item.title }}
                </h3>
                <p class="mt-[6px] text-[16px]" :class="item.active ? 'text-[#ff8832]' : 'text-[#1687ff]'">
                  {{ item.date }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 参赛指南 -->
        <div class="pt-[62px]">
          <component :is="() => SectionTitle({ title: '参赛指南', center: true })" />
          <div class="mt-[32px] grid gap-[32px] md:grid-cols-3">
            <button
              v-for="guide in guides"
              :key="guide.title"
              type="button"
              class="group overflow-hidden relative rounded-[8px] border-0 bg-transparent p-0 text-left shadow-[0_10px_24px_rgba(37,116,210,0.08)] cursor-pointer"
              @click="openGuide(guide)"
            >
              <img :src="guide.image" :alt="guide.title" class="h-[180px] w-full object-cover transition-transform group-hover:scale-105" />
              <div class="absolute top-0 left-[157px] h-full w-[calc(100%-157px)] z-20 flex flex-col justify-center">
                <p class="text-[28px] font-[800] text-[#004385]">{{ guide.title }}</p>
                <div v-if="guide.hasBotton" class="w-full">
                  <p class="text-[16px] font-[400] text-[#666] mb-10">截止时间：6月5日 17:00</p>
                  <el-button type="primary" round @click.stop="openGuide(guide)">立即报名</el-button>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 参赛作品 -->
    <div class="">
      <div class="mx-auto max-w-[1200px] bg-[url('@/assets/images/bg_home_02.png')] bg-no-repeat bg-cover bg-top py-[70px]">
        <component :is="() => SectionTitle({ title: '参赛作品', center: true })" />
        <div v-if="loading" class="mt-[36px] text-center py-12">
          <div class="inline-block w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p class="mt-3 text-gray-500">加载中...</p>
        </div>
        <div v-else class="mt-[36px] grid gap-x-[32px] gap-y-[28px] sm:grid-cols-2 lg:grid-cols-4">
          <el-card
            v-for="work in works"
            :key="work.id"
            shadow
            class="home-work-card !rounded-[10px] border-0 cursor-pointer"
            @click="openWorkDetail(work)"
          >
            <template #default>
              <div class="relative">
                <span class="absolute left-[-1px] top-[-1px] z-10 rounded-br-[8px] rounded-tl-[8px] bg-[#1189ff] px-[14px] py-[5px] text-[16px] text-white font-[800]">
                  {{ work.id }}
                </span>
                <img :src="workImages[work.id % 4]" :alt="work.name" class="h-[104px] rounded-t-[8px] w-full" />
                <div class="flex items-center ml-[60px] mr-[5px] h-full py-[5px] box-border w-[calc(100%-65px)] absolute top-0 right-0">
                  <h2 class="relative z-10 line-clamp-4 w-full text-[18px] text-[#005cae] font-[800] leading-[24px]">
                    {{ work.name }}
                  </h2>
                </div>
              </div>
              <div class="px-[16px] py-[18px] text-[13px] text-[#5e6673] leading-[26px]">
                <p class="line-clamp-1">作品名称：{{ work.name }}</p>
                <p class="line-clamp-1">参赛队伍：{{ work.team_name }}</p>
                <p class="line-clamp-1">当前票数：{{ work.vote_count || 0 }}</p>
                <p class="line-clamp-1">浏览量：{{ work.view_count || 0 }}</p>
              </div>
            </template>
          </el-card>
          <el-card v-if="works.length === 0" class="home-work-card !rounded-[10px] border-0">
            <template #default>
              <!--
              <div class="text-center py-8 text-gray-400">
                <p>暂无参赛作品</p>
              </div>
              -->
            </template>
          </el-card>
        </div>
        <div class="mt-[36px] text-center">
          <el-button type="primary" round @click="router.push('/works')">更多作品 》</el-button>
        </div>
      </div>
    </div>

    <!-- 新闻资讯 -->
    <div class="bg-white py-[70px]">
      <div class="mx-auto max-w-[1200px]">
        <component :is="() => SectionTitle({ title: '新闻资讯', center: true })" />
        <div v-if="loading" class="mt-[36px] text-center py-12">
          <div class="inline-block w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <template v-else>
          <div class="mt-[36px] grid gap-[44px] lg:grid-cols-[520px_1fr]">
            <!-- Featured Article -->
            <div v-if="articles.length > 0" class="cursor-pointer" @click="openArticle(articles[0])">
              <img
                :src="articles[0].cover_image || homeNewsImage"
                alt="featured article"
                class="h-[300px] cursor-pointer w-full rounded-[2px] bg-[#eefaff] object-cover"
              />
              <h3 class="mt-[22px] text-[18px] text-[#202734] font-[800] line-clamp-1 hover:text-[#1189ff]">
                {{ articles[0].title }}
              </h3>
              <p class="mt-[12px] text-[14px] text-[#9aa1ad] leading-[26px] line-clamp-1">
                {{ articles[0].summary || articles[0].content?.substring(0, 100) || '暂无摘要' }}
              </p>
            </div>
            <!-- Article List -->
            <div class="grid gap-[16px]">
              <button
                v-for="article in articles.slice(1)"
                :key="article.id"
                type="button"
                class="news-item grid grid-cols-[74px_1fr] gap-[18px] border-0 bg-transparent p-0 text-left cursor-pointer"
                @click="openArticle(article)"
              >
                <div class="news-date h-[74px] text-center text-white">
                  <div class="pt-[8px] text-[26px] font-[800] leading-[32px]">{{ formatDate(article.created_at).day }}</div>
                  <div class="text-[14px]">{{ formatDate(article.created_at).month }}</div>
                </div>
                <div class="border-b border-[#eef0f4] pb-[12px]">
                  <h3 class="text-[16px] text-[#333] font-[500] line-clamp-1">{{ article.title }}</h3>
                  <p class="mt-[8px] line-clamp-2 text-[13px] text-[#9aa1ad] leading-[23px]">
                    {{ article.summary || article.content?.substring(0, 100) || '暂无摘要' }}
                  </p>
                </div>
              </button>
            </div>
          </div>
          <div class="mt-[36px] text-center">
            <el-button round @click="router.push('/news')">更多新闻 》</el-button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-banner :deep(.el-carousel__indicators) {
  bottom: 24px;
}

.home-banner :deep(.el-carousel__indicator) {
  padding: 0 5px;
}

.home-banner :deep(.el-carousel__button) {
  width: 28px;
  height: 4px;
  border-radius: 999px;
  background-color: #ffffff;
  opacity: 1;
}

.home-banner :deep(.el-carousel__indicator.is-active .el-carousel__button) {
  width: 30px;
  background-color: #16d8ff;
}

.home-work-card :deep(.el-card__body) {
  padding: 0;
}

.news-date {
  background-color: #B1B1B1;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.news-date.is-active,
.news-item:hover .news-date {
  background-color: #1189ff;
  box-shadow: 0 8px 18px rgba(17, 137, 255, 0.18);
}

.news-item h3 {
  transition: color 0.2s ease;
}

.news-item:hover h3 {
  color: #1189ff;
}
</style>