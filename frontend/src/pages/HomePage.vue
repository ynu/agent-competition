<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { contentApi } from '@/api'
import { vReveal } from '@/directives/reveal'
import ComputeIcon from '@/components/ComputeIcon.vue'
import banner1 from '@/assets/images/banner_1.png'
import banner2 from '@/assets/images/banner_2.png'
import banner3 from '@/assets/images/banner_3.png'
import homeNewsImage from '@/assets/images/banner_works_detail.png'
import imgArticleYunxiaozhi from '@/assets/images/img_article_yunxiaozhi.png'
import imgMaterials from '@/assets/images/img_materials.png'

const router = useRouter()
const articles = ref<any[]>([])
const loading = ref(true)
const error = ref('')

const banners = [
  { image: banner1, alt: '2026年云南大学首届人工智能创新应用大赛', url: '/competition-plan' },
  { image: banner2, alt: '数启云大 智创未来', url: '/competition-plan' },
  { image: banner3, alt: '基于大模型的校园生活智能体创新应用', url: '/competition-plan' }
]

// 智能体广场：功能亮点
const agentFeatures = [
  { icon: 'agent', title: '什么是智能体？', desc: '智能体是能像人一样思考的AI，能够帮你解决各种知识问答、写作、数据分析等问题', hue: 'blue' },
  { icon: 'build', title: '怎么快速搭建一个智能体', desc: '可以通过一句话、一个文档、一个知识或者引用一些插件，快速搭建智能体', hue: 'violet' },
  { icon: 'experience', title: '体验一个智能体', desc: '你可以与智能体对话，智能体会根据自己掌握的知识、能力为你解答', hue: 'pink' },
  { icon: 'plaza', title: '看看大家做的智能体', desc: '智能体广场是校内师生发布备案的智能体集合，可以看到大家通过奇思妙想构建的优秀智能体', hue: 'orange' }
]

// 大模型服务：能力亮点
const llmFeatures = [
  { icon: 'speed', title: '极速响应', desc: '高并发推理加速，流式输出低至毫秒级首字延迟', hue: 'blue' },
  { icon: 'security', title: '安全合规', desc: '校内私有化部署，数据不出校，保障师生隐私安全', hue: 'green' },
  { icon: 'models', title: '多模型接入', desc: '聚合主流大模型能力，统一 API 接口，按需灵活切换', hue: 'violet' },
  { icon: 'multimodal', title: '多模态生成', desc: '提供文生图、TTS 语音合成、ASR 语音识别等多模态能力', hue: 'orange' }
]

const openArticle = (article: any) => {
  router.push(`/news/${article.id}`)
}

const goToAgentCenter = () => {
  router.push('/agent-center')
}

const openLlmPlatform = () => {
  window.open('https://new-api-itc.ynu.edu.cn/', '_blank', 'noopener,noreferrer')
}

const openCreateAgent = () => {
  window.open('https://agent.ynu.edu.cn/', '_blank', 'noopener,noreferrer')
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
    const articlesRes = await contentApi.latestArticles(5)
    articles.value = articlesRes.data || []
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
            <a :href="banner.url">
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
          <p class="mt-[10px] text-[15px] text-[#86868b]">门户动态，一手掌握</p>
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

    <!-- 智能体广场 -->
    <div class="relative py-[80px]">
      <!-- 清新浅色薄雾背景 -->
      <div class="absolute inset-0 bg-gradient-to-b from-white via-[#eef6ff] to-[#f7f4ff]"></div>
      <div class="pointer-events-none absolute left-[8%] top-[16%] h-56 w-56 rounded-full bg-[#9bd8ff]/35 blur-3xl"></div>
      <div class="pointer-events-none absolute right-[10%] top-[30%] h-48 w-48 rounded-full bg-[#c9b8ff]/35 blur-3xl"></div>
      <div class="pointer-events-none absolute bottom-[10%] left-[40%] h-44 w-44 rounded-full bg-[#ffc9e2]/30 blur-3xl"></div>

      <div class="relative mx-auto max-w-[1200px] px-[16px]">
        <!-- 介绍卡片 -->
        <div v-reveal class="apple-card apple-card-hover grid items-center gap-[48px] p-[40px] lg:grid-cols-[440px_1fr] lg:p-[56px]">
          <div v-reveal="{ direction: 'left', delay: 100 }" class="overflow-hidden rounded-[20px] shadow-[0_16px_48px_rgba(29,42,68,0.16)]">
            <img
              :src="imgArticleYunxiaozhi"
              alt="智能体广场"
              class="w-full transition-transform duration-700 hover:scale-105"
            />
          </div>
          <div v-reveal="{ direction: 'right', delay: 200 }">
            <p class="mb-[14px] inline-flex items-center gap-[6px] rounded-full bg-[#6a5cff]/8 px-[14px] py-[6px] text-[13px] font-[600] text-[#6a5cff]">
              <span class="h-[6px] w-[6px] rounded-full bg-gradient-to-r from-[#0090ff] to-[#6a5cff]"></span>
              AGENT PLAZA
            </p>
            <h2 class="text-[32px] font-[700] leading-[42px] lg:text-[40px] lg:leading-[52px]">
              <span class="text-gradient">智能体广场</span><br />
              <span class="text-[#1d1d1f]">发现并创造你的智能体</span>
            </h2>
            <p class="mt-[24px] text-[15px] text-[#515154] leading-[30px]">
              智能体广场汇聚了校园各场景的智能体应用，覆盖学习辅导、生活服务、科研助手等多个领域。
              在这里你可以一键体验他人创建的智能体，也可以动手搭建属于自己的智能体并分享给全校师生。
            </p>
            <p class="mt-[28px] flex flex-wrap gap-[14px]">
              <el-button type="primary" round size="large" class="!px-[32px]" @click="goToAgentCenter">进入广场</el-button>
              <el-button round size="large" class="!px-[32px]" @click="openCreateAgent">创建智能体</el-button>
            </p>
          </div>
        </div>

        <!-- 能力亮点 -->
        <div class="mt-[44px] grid gap-[20px] sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="(feature, index) in agentFeatures"
            :key="feature.title"
            v-reveal="{ delay: 100 + index * 90 }"
            class="apple-card apple-card-hover group p-[26px]"
          >
            <div
              class="flex h-[56px] w-[56px] items-center justify-center rounded-[18px] transition-transform duration-500 group-hover:scale-110 group-hover:-rotate-6"
              :class="{
                'bg-[#0090ff]/10': feature.hue === 'blue',
                'bg-[#6a5cff]/10': feature.hue === 'violet',
                'bg-[#ff5ca8]/10': feature.hue === 'pink',
                'bg-[#ff9f0a]/12': feature.hue === 'orange',
                'bg-[#30d158]/12': feature.hue === 'green'
              }"
            >
              <ComputeIcon :name="feature.icon" :size="32" />
            </div>
            <h3 class="mt-[16px] text-[17px] font-[700] text-[#1d1d1f]">{{ feature.title }}</h3>
            <p class="mt-[8px] text-[13px] leading-[22px] text-[#86868b]">{{ feature.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 大模型服务 -->
    <div class="relative py-[80px]">
      <!-- 清新浅色薄雾背景 -->
      <div class="absolute inset-0 bg-gradient-to-b from-[#f7f4ff] via-white to-[#eefaff]"></div>
      <div class="pointer-events-none absolute left-[14%] top-[22%] h-52 w-52 rounded-full bg-[#c9b8ff]/35 blur-3xl"></div>
      <div class="pointer-events-none absolute right-[8%] bottom-[16%] h-48 w-48 rounded-full bg-[#9bd8ff]/35 blur-3xl"></div>
      <div class="pointer-events-none absolute bottom-[8%] left-[36%] h-40 w-40 rounded-full bg-[#b8f0d8]/30 blur-3xl"></div>

      <div class="relative mx-auto max-w-[1200px] px-[16px]">
        <!-- 介绍卡片（右图左文） -->
        <div v-reveal class="apple-card apple-card-hover grid items-center gap-[48px] p-[40px] lg:grid-cols-[1fr_440px] lg:p-[56px]">
          <div v-reveal="{ direction: 'left', delay: 200 }" class="order-2 lg:order-1">
            <p class="mb-[14px] inline-flex items-center gap-[6px] rounded-full bg-[#0090ff]/8 px-[14px] py-[6px] text-[13px] font-[600] text-[#0090ff]">
              <span class="h-[6px] w-[6px] rounded-full bg-gradient-to-r from-[#30d158] to-[#0090ff]"></span>
              AI PLATFORM
            </p>
            <h2 class="text-[32px] font-[700] leading-[42px] lg:text-[40px] lg:leading-[52px]">
              <span class="text-gradient">大模型服务</span><br />
              <span class="text-[#1d1d1f]">校内一站式 AI 能力底座</span>
            </h2>
            <p class="mt-[24px] text-[15px] text-[#515154] leading-[30px]">
              大模型服务面向全校师生提供统一的大模型 API 服务，兼容主流接口规范，
              支持对话推理、文本生成、代码辅助等多种能力，同时提供文生图、TTS 语音合成、ASR 语音识别等多模态服务，
              其他高质量大模型持续更新维护，为教学、科研与校园应用开发提供稳定可靠的 AI 基础设施。
            </p>
            <p class="mt-[28px] flex flex-wrap gap-[14px]">
              <el-button type="primary" round size="large" class="!px-[32px]" @click="openLlmPlatform">立即使用</el-button>
            </p>
          </div>
          <div v-reveal="{ direction: 'right', delay: 100 }" class="order-1 overflow-hidden rounded-[20px] shadow-[0_16px_48px_rgba(29,42,68,0.16)] lg:order-2">
            <img
              :src="imgMaterials"
              alt="大模型服务"
              class="w-full transition-transform duration-700 hover:scale-105"
            />
          </div>
        </div>

        <!-- 能力亮点 -->
        <div class="mt-[44px] grid gap-[20px] sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="(feature, index) in llmFeatures"
            :key="feature.title"
            v-reveal="{ delay: 100 + index * 90 }"
            class="apple-card apple-card-hover group p-[26px]"
          >
            <div
              class="flex h-[56px] w-[56px] items-center justify-center rounded-[18px] transition-transform duration-500 group-hover:scale-110 group-hover:-rotate-6"
              :class="{
                'bg-[#0090ff]/10': feature.hue === 'blue',
                'bg-[#6a5cff]/10': feature.hue === 'violet',
                'bg-[#ff5ca8]/10': feature.hue === 'pink',
                'bg-[#ff9f0a]/12': feature.hue === 'orange',
                'bg-[#30d158]/12': feature.hue === 'green'
              }"
            >
              <ComputeIcon :name="feature.icon" :size="32" />
            </div>
            <h3 class="mt-[16px] text-[17px] font-[700] text-[#1d1d1f]">{{ feature.title }}</h3>
            <p class="mt-[8px] text-[13px] leading-[22px] text-[#86868b]">{{ feature.desc }}</p>
          </div>
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
