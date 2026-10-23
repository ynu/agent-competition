<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { contentApi } from '@/api'
import { vReveal } from '@/directives/reveal'
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
  { icon: 'agent', title: '什么是智能体？', desc: '智能体是能像人一样思考的AI，能够帮你解决各种知识问答、写作、数据分析等问题' },
  { icon: 'build', title: '怎么快速搭建一个智能体', desc: '可以通过一句话、一个文档、一个知识或者引用一些插件，快速搭建智能体' },
  { icon: 'experience', title: '体验一个智能体', desc: '你可以与智能体对话，智能体会根据自己掌握的知识、能力为你解答' },
  { icon: 'plaza', title: '看看大家做的智能体', desc: '智能体广场是校内师生发布备案的智能体集合，可以看到大家通过奇思妙想构建的优秀智能体' }
]

// 大模型服务：能力亮点
const llmFeatures = [
  { icon: 'speed', title: '极速响应', desc: '高并发推理加速，流式输出低至毫秒级首字延迟' },
  { icon: 'security', title: '安全合规', desc: '校内私有化部署，数据不出校，保障师生隐私安全' },
  { icon: 'models', title: '多模型接入', desc: '聚合主流大模型能力，统一 API 接口，按需灵活切换' },
  { icon: 'multimodal', title: '多模态生成', desc: '提供文生图、TTS 语音合成、ASR 语音识别等多模态能力' }
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
      <div class="pointer-events-none absolute left-[8%] top-[16%] h-56 w-56 rounded-full bg-[#9bd8ff]/35 blur-3xl anim-blob"></div>
      <div class="pointer-events-none absolute right-[10%] top-[30%] h-48 w-48 rounded-full bg-[#c9b8ff]/35 blur-3xl anim-blob anim-blob-2"></div>
      <div class="pointer-events-none absolute bottom-[10%] left-[40%] h-44 w-44 rounded-full bg-[#ffc9e2]/30 blur-3xl anim-blob anim-blob-3"></div>

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
              <span class="h-[6px] w-[6px] rounded-full bg-gradient-to-r from-[#0090ff] to-[#6a5cff] badge-dot"></span>
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
            <div class="h-[56px] w-[56px] transition-transform duration-500 group-hover:scale-110 group-hover:-rotate-6">
              <!-- 什么是智能体:会眨眼说话的机器人 -->
              <svg v-if="feature.icon === 'agent'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <path d="M24 6.5V11" stroke="#3b82f6" stroke-width="3.2" stroke-linecap="round"/>
                <circle cx="24" cy="5" r="3" fill="#f9a8d4" class="hi-pump"/>
                <path d="M5.5 20.5h-4M42.5 20.5h4" stroke="#3b82f6" stroke-width="3.4" stroke-linecap="round"/>
                <rect x="6.5" y="10.5" width="35" height="28" rx="10" fill="url(#ha-agent)" class="hi-jelly"/>
                <g class="hi-blink">
                  <circle cx="17.5" cy="21.5" r="3.6" fill="#fff"/>
                  <circle cx="18.5" cy="22.3" r="1.7" fill="#0f172a" opacity=".85"/>
                </g>
                <g class="hi-blink hi-b2">
                  <circle cx="30.5" cy="21.5" r="3.6" fill="#fff"/>
                  <circle cx="31.5" cy="22.3" r="1.7" fill="#0f172a" opacity=".85"/>
                </g>
                <path d="M18.5 29.5c3.7 3.4 7.3 3.4 11 0" stroke="#fff" stroke-width="3" stroke-linecap="round" class="hi-yap"/>
                <circle cx="11" cy="29.5" r="1.6" fill="#f9a8d4" class="hi-tw"/>
                <circle cx="37" cy="29.5" r="1.6" fill="#f9a8d4" class="hi-tw hi-d2"/>
                <defs>
                  <linearGradient id="ha-agent" x1="6.5" y1="10.5" x2="41.5" y2="38.5" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#93c5fd"/><stop offset="1" stop-color="#3b82f6"/>
                  </linearGradient>
                </defs>
              </svg>
              <!-- 怎么快速搭建:积木拼装,顶块反复落下 -->
              <svg v-else-if="feature.icon === 'build'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <rect x="3.5" y="26.5" width="18" height="18" rx="5" fill="url(#ha-build)" class="hi-jelly"/>
                <rect x="26.5" y="26.5" width="18" height="18" rx="5" fill="#fff" stroke="#ea580c" stroke-width="3"/>
                <rect x="15" y="3.5" width="18" height="18" rx="5" fill="#67e8f9" class="hi-drop"/>
                <path d="M12.5 26.5v-5a3.5 3.5 0 0 1 3.5-3.5h.5M24 21v5.5M31.5 26.5v-5a3.5 3.5 0 0 0-3.5-3.5H27.5" stroke="#fb923c" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="6 5" class="hi-flow"/>
                <circle cx="12.5" cy="35.5" r="2.2" fill="#fff" class="hi-tw"/>
                <circle cx="35.5" cy="35.5" r="2.2" fill="#fb923c" class="hi-tw hi-d2"/>
                <defs>
                  <linearGradient id="ha-build" x1="3.5" y1="26.5" x2="21.5" y2="44.5" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#fb923c"/><stop offset="1" stop-color="#ea580c"/>
                  </linearGradient>
                </defs>
              </svg>
              <!-- 体验一个智能体:对话气泡 + 播放键 + 音条 -->
              <svg v-else-if="feature.icon === 'experience'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <path d="M9 5h30a5.5 5.5 0 0 1 5.5 5.5v15.5a5.5 5.5 0 0 1-5.5 5.5H20.5L11 39.5V31.5H9A5.5 5.5 0 0 1 3.5 26V10.5A5.5 5.5 0 0 1 9 5Z" fill="url(#ha-exp)" class="hi-jelly"/>
                <path d="M13.5 12.5v12l10.5-6-10.5-6Z" fill="#fff" class="hi-beat"/>
                <rect x="29" y="15.5" width="3.6" height="7" rx="1.8" fill="#fde047" class="hi-eq"/>
                <rect x="35.5" y="12" width="3.6" height="14" rx="1.8" fill="#fff" class="hi-eq hi-e2"/>
                <defs>
                  <linearGradient id="ha-exp" x1="3.5" y1="5" x2="44.5" y2="31.5" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#f472b6"/><stop offset="1" stop-color="#db2777"/>
                  </linearGradient>
                </defs>
              </svg>
              <!-- 看看大家做的智能体:广场雷达 + 节点 -->
              <svg v-else viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <path d="M15 9.5h18M9.5 15v18M38.5 15v18M15 38.5h18" stroke="#0d9488" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="6 5" opacity=".65" class="hi-flow"/>
                <circle cx="9" cy="9" r="6" fill="url(#ha-plaza)" class="hi-bulb"/>
                <circle cx="39" cy="9" r="6" fill="#fde047" class="hi-bulb hi-b2"/>
                <circle cx="9" cy="39" r="6" fill="#fde047" class="hi-bulb hi-b3"/>
                <circle cx="39" cy="39" r="6" fill="url(#ha-plaza)" class="hi-bulb hi-b2"/>
                <circle cx="24" cy="24" r="7.5" stroke="#2dd4bf" stroke-width="2.2" class="hi-echo"/>
                <circle cx="24" cy="24" r="7.5" stroke="#fde047" stroke-width="2.2" class="hi-echo hi-e2"/>
                <circle cx="24" cy="24" r="5" fill="url(#ha-plaza)" class="hi-beat"/>
                <defs>
                  <linearGradient id="ha-plaza" x1="3" y1="3" x2="15" y2="15" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#2dd4bf"/><stop offset="1" stop-color="#0d9488"/>
                  </linearGradient>
                </defs>
              </svg>
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
      <div class="pointer-events-none absolute left-[14%] top-[22%] h-52 w-52 rounded-full bg-[#c9b8ff]/35 blur-3xl anim-blob anim-blob-2"></div>
      <div class="pointer-events-none absolute right-[8%] bottom-[16%] h-48 w-48 rounded-full bg-[#9bd8ff]/35 blur-3xl anim-blob"></div>
      <div class="pointer-events-none absolute bottom-[8%] left-[36%] h-40 w-40 rounded-full bg-[#b8f0d8]/30 blur-3xl anim-blob anim-blob-3"></div>

      <div class="relative mx-auto max-w-[1200px] px-[16px]">
        <!-- 介绍卡片（右图左文） -->
        <div v-reveal class="apple-card apple-card-hover grid items-center gap-[48px] p-[40px] lg:grid-cols-[1fr_440px] lg:p-[56px]">
          <div v-reveal="{ direction: 'left', delay: 200 }" class="order-2 lg:order-1">
            <p class="mb-[14px] inline-flex items-center gap-[6px] rounded-full bg-[#0090ff]/8 px-[14px] py-[6px] text-[13px] font-[600] text-[#0090ff]">
              <span class="h-[6px] w-[6px] rounded-full bg-gradient-to-r from-[#30d158] to-[#0090ff] badge-dot"></span>
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
            <div class="h-[56px] w-[56px] transition-transform duration-500 group-hover:scale-110 group-hover:-rotate-6">
              <!-- 极速响应:闪电劈落 + 残影 + 冲击波 -->
              <svg v-if="feature.icon === 'speed'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <circle cx="24" cy="24" r="21" stroke="#60a5fa" stroke-width="2.4" opacity=".65" class="hi-echo"/>
                <path d="M27.5 5 14 26h7.5L20.5 43 34.5 22h-8.5l1.5-17Z" fill="#60a5fa" opacity=".4" class="hi-ghost"/>
                <path d="M27.5 3 13.5 25h8L20 45 34.5 22.5h-8.5L27.5 3Z" fill="url(#hl-speed)" class="hi-strike"/>
                <path d="M2 17.5h7.5M1 25.5H9" stroke="#fde047" stroke-width="3.4" stroke-linecap="round" class="hi-zoom"/>
                <defs>
                  <linearGradient id="hl-speed" x1="13.5" y1="3" x2="34.5" y2="45" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#fde047"/><stop offset="1" stop-color="#f59e0b"/>
                  </linearGradient>
                </defs>
              </svg>
              <!-- 安全合规:盾牌 + 对勾描绘 -->
              <svg v-else-if="feature.icon === 'security'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <path d="M24 2.5 42.5 9v14c0 11-7.6 18.2-18.5 22C13.1 41.2 5.5 34 5.5 23V9L24 2.5Z" fill="url(#hl-sec)" class="hi-jelly"/>
                <path d="M24 8 37 12.9v10.1c0 7.9-5.4 13.2-13 16-7.6-2.8-13-8.1-13-16V12.9L24 8Z" fill="#fff" opacity=".16"/>
                <path d="M16 23.5l6 6 10.5-12" stroke="#fff" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round" class="hi-check"/>
                <path d="M41 29v6.5M37.8 32.2h6.4" stroke="#93c5fd" stroke-width="2.8" stroke-linecap="round" class="hi-tw"/>
                <defs>
                  <linearGradient id="hl-sec" x1="5.5" y1="2.5" x2="42.5" y2="45" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#34d399"/><stop offset="1" stop-color="#059669"/>
                  </linearGradient>
                </defs>
              </svg>
              <!-- 多模型接入:层叠卡片 + 扫描行 + 轮播点 -->
              <svg v-else-if="feature.icon === 'models'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <rect x="15" y="4.5" width="30" height="23" rx="5.5" fill="#4338ca" opacity=".6" class="hi-card"/>
                <rect x="3" y="9" width="31" height="23" rx="5.5" fill="url(#hl-models)"/>
                <path d="M8.5 16.5h20" stroke="#67e8f9" stroke-width="3.4" stroke-linecap="round" class="hi-sweep"/>
                <path d="M8.5 23.5h13" stroke="#fff" stroke-width="3.4" stroke-linecap="round" opacity=".6"/>
                <circle cx="11.5" cy="40" r="2.8" fill="#a5b4fc" class="hi-mq"/>
                <circle cx="20" cy="40" r="2.8" fill="#67e8f9" class="hi-mq hi-m2"/>
                <circle cx="28.5" cy="40" r="2.8" fill="#4338ca" class="hi-mq hi-m3"/>
                <defs>
                  <linearGradient id="hl-models" x1="3" y1="9" x2="34" y2="32" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#a5b4fc"/><stop offset="1" stop-color="#6366f1"/>
                  </linearGradient>
                </defs>
              </svg>
              <!-- 多模态生成:调色盘 + 颜料点 + 声波 -->
              <svg v-else viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <path d="M24 3.5c11.5 0 21 8.3 21 18.7 0 5.8-4.8 8.8-10 8.8h-4.2c-3.4 0-5.4 2.3-5.4 5 0 1.4.6 2.6 1.4 3.7.7 1 1.5 2.1 1.5 3.5 0 2.4-1.9 4.1-4.2 4.1C12.8 47.3 3 38.1 3 25.5S12.5 3.5 24 3.5Z" fill="url(#hl-mm)" class="hi-jelly"/>
                <circle cx="14.5" cy="18" r="3.8" fill="#67e8f9" class="hi-dancer"/>
                <circle cx="24" cy="12.5" r="3.8" fill="#fff" class="hi-dancer hi-d2"/>
                <circle cx="33.5" cy="18" r="3.8" fill="#4338ca" class="hi-dancer hi-d3"/>
                <path d="M11.5 28c2.2-2 4.4-2 6.6 0s4.4 2 6.6 0" stroke="#fff" stroke-width="2.4" stroke-linecap="round" opacity=".8" class="hi-wave"/>
                <defs>
                  <linearGradient id="hl-mm" x1="3" y1="3.5" x2="45" y2="47.3" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#fda4af"/><stop offset="1" stop-color="#e11d48"/>
                  </linearGradient>
                </defs>
              </svg>
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

/* 板块背景光斑漂移 */
.anim-blob {
  animation: blob-drift 8s ease-in-out infinite alternate;
}
.anim-blob-2 {
  animation-duration: 10s;
  animation-delay: 1.2s;
}
.anim-blob-3 {
  animation-duration: 12s;
  animation-delay: 2.4s;
}
@keyframes blob-drift {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(26px, -20px) scale(1.12);
  }
}

/* 徽章小圆点呼吸 */
.badge-dot {
  animation: dot-breathe 2s ease-in-out infinite;
}
@keyframes dot-breathe {
  0%,
  100% {
    opacity: 0.55;
    transform: scale(0.85);
  }
  50% {
    opacity: 1;
    transform: scale(1.15);
  }
}

/* ============ 首页内联图标动画 ============ */
svg [class^='hi-'],
svg [class*=' hi-'] {
  transform-box: fill-box;
  transform-origin: center;
}
.hi-jelly {
  animation: hi-jelly 1.9s ease-in-out infinite;
}
.hi-pump {
  animation: hi-pump 1.2s ease-in-out infinite;
}
.hi-blink {
  animation: hi-blink 1.8s ease-in-out infinite;
}
.hi-yap {
  stroke-dasharray: 13;
  animation: hi-yap 1.8s ease-in-out infinite;
}
.hi-tw {
  animation: hi-tw 1.3s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.hi-d2 {
  animation-delay: 0.35s;
}
.hi-d3 {
  animation-delay: 0.5s;
}
.hi-drop {
  animation: hi-drop 1.4s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.hi-flow {
  animation: hi-flow 1s linear infinite;
}
.hi-beat {
  animation: hi-beat 1s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.hi-eq {
  animation: hi-eq 0.55s ease-in-out infinite;
}
.hi-e2 {
  animation-delay: 0.16s;
}
.hi-bulb {
  animation: hi-bulb 1.5s ease-in-out infinite;
}
.hi-b2 {
  animation-delay: 0.38s;
}
.hi-b3 {
  animation-delay: 0.76s;
}
.hi-echo {
  animation: hi-echo 1.5s ease-out infinite;
}
.hi-ghost {
  animation: hi-ghost 0.65s ease-in-out infinite;
}
.hi-strike {
  animation: hi-strike 0.7s ease-in-out infinite;
}
.hi-zoom {
  animation: hi-zoom 1s ease-out infinite;
}
.hi-check {
  stroke-dasharray: 26;
  animation: hi-check 1.8s ease-in-out infinite;
}
.hi-card {
  animation: hi-card 1.8s ease-in-out infinite;
}
.hi-sweep {
  stroke-dasharray: 20 20;
  animation: hi-sweep 1.5s linear infinite;
}
.hi-mq {
  animation: hi-mq 1.2s ease-in-out infinite;
}
.hi-m2 {
  animation-delay: 0.2s;
}
.hi-m3 {
  animation-delay: 0.4s;
}
.hi-dancer {
  animation: hi-dancer 1.3s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.hi-wave {
  animation: hi-wave 1.4s ease-in-out infinite alternate;
}

@keyframes hi-jelly {
  0%, 100% { transform: scale(1, 1) rotate(0deg); }
  25% { transform: scale(0.96, 1.04) rotate(-2deg); }
  50% { transform: scale(1.03, 0.97) rotate(0deg); }
  75% { transform: scale(0.98, 1.02) rotate(2deg); }
}
@keyframes hi-pump {
  0%, 100% { transform: scale(0.85); opacity: 0.75; }
  50% { transform: scale(1.12); opacity: 1; }
}
@keyframes hi-blink {
  0%, 40%, 48%, 100% { transform: scaleY(1); }
  44% { transform: scaleY(0.06); }
}
@keyframes hi-yap {
  0% { stroke-dashoffset: 13; }
  40%, 75% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: 13; }
}
@keyframes hi-tw {
  0%, 100% { opacity: 0.1; transform: scale(0.4) rotate(-30deg); }
  50% { opacity: 1; transform: scale(1.1) rotate(0deg); }
}
@keyframes hi-drop {
  0%, 100% { transform: translateY(-7px); }
  45% { transform: translateY(3.5px) scaleY(0.92); }
  60% { transform: translateY(0) scaleY(1); }
}
@keyframes hi-flow {
  0% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -22; }
}
@keyframes hi-beat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.28); }
}
@keyframes hi-eq {
  0%, 100% { transform: scaleY(0.3); }
  50% { transform: scaleY(1); }
}
@keyframes hi-bulb {
  0%, 100% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.14); opacity: 1; }
}
@keyframes hi-echo {
  0% { transform: scale(0.4); opacity: 1; }
  100% { transform: scale(1.85); opacity: 0; }
}
@keyframes hi-ghost {
  0%, 100% { transform: translateX(0); opacity: 0.45; }
  50% { transform: translateX(-4.5px); opacity: 0.15; }
}
@keyframes hi-strike {
  0%, 100% { transform: translateX(0) scale(1); }
  30% { transform: translateX(-3px) scale(1.06); }
  60% { transform: translateX(2.5px) scale(0.96); }
}
@keyframes hi-zoom {
  0% { transform: translateX(9px); opacity: 0; }
  30% { opacity: 1; }
  100% { transform: translateX(-11px); opacity: 0; }
}
@keyframes hi-check {
  0% { stroke-dashoffset: 26; }
  45%, 75% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: 0; opacity: 0.2; }
}
@keyframes hi-card {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(2.5px, 1.5px) rotate(3deg); }
}
@keyframes hi-sweep {
  0% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -40; }
}
@keyframes hi-mq {
  0%, 100% { transform: translateX(0) scale(0.7); opacity: 0.35; }
  50% { transform: translateX(1.5px) scale(1.25); opacity: 1; }
}
@keyframes hi-dancer {
  0%, 100% { transform: scale(0.7); opacity: 0.35; }
  50% { transform: scale(1.3); opacity: 1; }
}
@keyframes hi-wave {
  from { transform: translateX(-3.5px); }
  to { transform: translateX(3.5px); }
}

@media (prefers-reduced-motion: reduce) {
  .anim-blob,
  svg [class^='hi-'],
  svg [class*=' hi-'] {
    animation: none !important;
  }
}
</style>
