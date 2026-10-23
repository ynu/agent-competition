<script setup lang="ts">
import { vReveal } from '@/directives/reveal'

// 算力卡型号（可选择多种算力卡）
const gpuCards = [
  {
    name: 'NVIDIA RTX 4090',
    vendor: 'NVIDIA',
    vram: '24GB GDDR6X',
    scene: '实验 / 小规模微调',
    desc: '高性价比消费级旗舰，适合课程实验、毕业设计与中小模型的微调、推理验证。',
    hue: 'orange',
    icon: '🟠',
    available: true
  },
  {
    name: 'NVIDIA L20',
    vendor: 'NVIDIA',
    vram: '48GB GDDR6',
    scene: '推理 / 中规模训练',
    desc: '数据中心级推理卡，大显存适合大模型推理服务与中等规模训练任务。',
    hue: 'green',
    icon: '🟩',
    available: true
  },
  {
    name: '平头哥 PPU-810E',
    vendor: '阿里平头哥（国产）',
    vram: '96GB',
    scene: '大模型训练 / 推理',
    desc: '国产自研算力卡，超大显存适合大模型训练与推理，满足自主可控的信创场景需求。',
    hue: 'cyan',
    icon: '🟦',
    available: true
  },
  {
    name: '更多算力卡',
    vendor: 'NVIDIA H100 / A800 / A100 等',
    vram: '规划中',
    scene: '训练 / 推理（建设中）',
    desc: 'H100、A800、A100 等更多算力卡正在接入建设中，敬请期待。',
    hue: 'violet',
    icon: '✨',
    available: false
  }
]

// 适用场景
const scenes = [
  {
    icon: '🎓',
    title: '教学实验',
    desc: '人工智能课程实验、训练营实操，学生按需申请 GPU 资源完成作业与项目实践。',
    hue: 'blue'
  },
  {
    icon: '🔬',
    title: '科研训练',
    desc: '支持研究生与科研团队开展模型训练、微调与消融实验，加速科研成果产出。',
    hue: 'violet'
  },
  {
    icon: '🏆',
    title: '竞赛支撑',
    desc: '为参赛队伍提供算力保障，支撑智能体开发、模型优化与作品打磨。',
    hue: 'pink'
  },
  {
    icon: '🚀',
    title: '应用部署',
    desc: '智能体推理服务、校园 AI 应用上线部署，提供稳定的在线算力支撑。',
    hue: 'orange'
  }
]

// 提供方式：沟通 - 申请 - 审核
const processSteps = [
  {
    step: '01',
    title: '沟通咨询',
    desc: '通过联系方式与我们沟通，说明算力需求场景、规模与使用周期。',
    icon: '💬'
  },
  {
    step: '02',
    title: '提交申请',
    desc: '填写算力使用申请，包括项目背景、所需算力卡类型、时长与预期成果。',
    icon: '📝'
  },
  {
    step: '03',
    title: '审核评估',
    desc: '平台对申请进行审核评估，通过后分配算力资源并提供使用指引。',
    icon: '✅'
  }
]

const hueClass: Record<string, string> = {
  blue: 'bg-gradient-to-br from-[#0090ff] to-[#00c6ff]',
  violet: 'bg-gradient-to-br from-[#6a5cff] to-[#a18cd1]',
  pink: 'bg-gradient-to-br from-[#ff5ca8] to-[#ff9f45]',
  orange: 'bg-gradient-to-br from-[#ff9f0a] to-[#ff5ca8]',
  green: 'bg-gradient-to-br from-[#30d158] to-[#0090ff]',
  cyan: 'bg-gradient-to-br from-[#00c6ff] to-[#30d158]'
}
</script>

<template>
  <section class="min-h-[calc(100vh-200px)] pb-[80px] pt-[28px]">
    <div class="mx-auto max-w-[1200px] px-[16px]">
      <!-- 面包屑 -->
      <div class="flex items-center gap-[6px] text-[14px] text-[#86868b]">
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#0071e3] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <span>算力服务</span>
      </div>

      <!-- 页头 -->
      <div v-reveal="{ delay: 60 }" class="mt-[28px] text-center">
        <h1 class="text-[34px] font-[700] lg:text-[44px]"><span class="text-gradient">算力服务</span></h1>
        <p class="mt-[10px] text-[15px] text-[#86868b]">面向全校师生提供 GPU 算力支撑，教学科研竞赛一站式保障</p>
      </div>

      <!-- GPU 算力介绍 -->
      <div v-reveal class="apple-card mt-[44px] grid items-center gap-[48px] p-[40px] lg:grid-cols-[1fr_420px] lg:p-[56px]">
        <div v-reveal="{ direction: 'left', delay: 100 }">
          <p class="mb-[14px] inline-flex items-center gap-[6px] rounded-full bg-[#30d158]/10 px-[14px] py-[6px] text-[13px] font-[600] text-[#1f9d41]">
            <span class="h-[6px] w-[6px] rounded-full bg-gradient-to-r from-[#30d158] to-[#00c6ff]"></span>
            GPU COMPUTING
          </p>
          <h2 class="text-[28px] font-[700] leading-[38px] text-[#1d1d1f] lg:text-[34px] lg:leading-[46px]">
            GPU 算力
            <span class="text-gradient">让 AI 触手可及</span>
          </h2>
          <p class="mt-[20px] text-[15px] leading-[30px] text-[#515154]">
            算力服务整合校内 GPU 资源，面向教学、科研与竞赛提供弹性算力服务。
            平台支持多种主流算力卡，覆盖从课程实验的小规模推理，到大模型分布式训练的高性能计算场景，
            助力师生专注模型与应用本身，无需关心底层基础设施。
          </p>
          <div class="mt-[24px] grid grid-cols-3 gap-[16px]">
            <div class="rounded-[16px] bg-[#f5f5f7] p-[16px] text-center">
              <p class="text-[24px] font-[700] text-[#0071e3]">多种</p>
              <p class="mt-[4px] text-[12px] text-[#86868b]">算力卡可选</p>
            </div>
            <div class="rounded-[16px] bg-[#f5f5f7] p-[16px] text-center">
              <p class="text-[24px] font-[700] text-[#6a5cff]">弹性</p>
              <p class="mt-[4px] text-[12px] text-[#86868b]">按需分配</p>
            </div>
            <div class="rounded-[16px] bg-[#f5f5f7] p-[16px] text-center">
              <p class="text-[24px] font-[700] text-[#ff5ca8]">一站式</p>
              <p class="mt-[4px] text-[12px] text-[#86868b]">申请即用</p>
            </div>
          </div>
        </div>
        <div v-reveal="{ direction: 'right', delay: 200 }" class="order-2 overflow-hidden rounded-[20px] shadow-[0_16px_48px_rgba(29,42,68,0.16)] lg:order-2">
          <svg viewBox="0 0 420 320" class="h-auto w-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="gpu-bg" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#0b1220"/>
                <stop offset="100%" stop-color="#16233c"/>
              </linearGradient>
              <linearGradient id="gpu-chip" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#30d158"/>
                <stop offset="100%" stop-color="#0090ff"/>
              </linearGradient>
            </defs>
            <rect width="420" height="320" rx="20" fill="url(#gpu-bg)"/>
            <!-- 电路走线 -->
            <g stroke="#2b3a55" stroke-width="2" fill="none">
              <path d="M60 80 h60 v40 h50"/>
              <path d="M360 240 h-70 v-40 h-40"/>
              <path d="M80 250 h80"/>
              <path d="M340 90 h-50"/>
            </g>
            <g fill="#3b82f6">
              <circle cx="60" cy="80" r="4"/>
              <circle cx="360" cy="240" r="4"/>
              <circle cx="80" cy="250" r="4"/>
              <circle cx="340" cy="90" r="4"/>
            </g>
            <!-- GPU 主体 -->
            <rect x="130" y="100" width="160" height="120" rx="14" fill="#1d2b45" stroke="#334a6b" stroke-width="2"/>
            <rect x="150" y="120" width="120" height="80" rx="8" fill="url(#gpu-chip)" opacity="0.9"/>
            <text x="210" y="168" text-anchor="middle" fill="#fff" font-size="26" font-weight="700" font-family="monospace">GPU</text>
            <!-- 散热纹理 -->
            <g stroke="#334a6b" stroke-width="3" stroke-linecap="round">
              <path d="M110 115 v90"/><path d="M122 115 v90"/>
              <path d="M298 115 v90"/><path d="M310 115 v90"/>
            </g>
            <!-- 状态灯 -->
            <circle cx="150" cy="230" r="5" fill="#30d158">
              <animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite"/>
            </circle>
            <circle cx="170" cy="230" r="5" fill="#0090ff">
              <animate attributeName="opacity" values="0.3;1;0.3" dur="1.6s" repeatCount="indefinite"/>
            </circle>
            <text x="352" y="296" text-anchor="end" fill="#5b6b85" font-size="12">AI COMPUTING POWER</text>
          </svg>
        </div>
      </div>

      <!-- 算力卡选择 -->
      <div class="mt-[56px]">
        <div v-reveal="{ delay: 60 }" class="text-center">
          <h2 class="text-[26px] font-[700] text-[#1d1d1f] lg:text-[32px]">多种<span class="text-gradient">算力卡</span>可选</h2>
          <p class="mt-[10px] text-[15px] text-[#86868b]">目前已提供 RTX 4090、L20、平头哥 PPU-810E 三种算力卡，更多型号建设中</p>
        </div>
        <div class="mt-[28px] grid gap-[20px] sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="(card, index) in gpuCards"
            :key="card.name"
            v-reveal="{ delay: 100 + index * 90 }"
            class="apple-card apple-card-hover group relative flex flex-col p-[24px]"
            :class="{ 'opacity-90': !card.available }"
          >
            <span
              v-if="card.available"
              class="absolute right-[16px] top-[16px] rounded-full bg-[#30d158]/12 px-[10px] py-[3px] text-[12px] font-[600] text-[#1f9d41]"
            >可提供</span>
            <span
              v-else
              class="absolute right-[16px] top-[16px] rounded-full bg-[#ff9f0a]/12 px-[10px] py-[3px] text-[12px] font-[600] text-[#c77800]"
            >建设中</span>
            <div class="flex items-center gap-[14px]">
              <div
                class="flex h-[52px] w-[52px] items-center justify-center rounded-[16px] text-[24px] shadow-[0_10px_28px_rgba(29,42,68,0.14)] transition-transform duration-500 group-hover:scale-110"
                :class="hueClass[card.hue]"
              >
                {{ card.icon }}
              </div>
              <div>
                <h3 class="text-[16px] font-[700] text-[#1d1d1f]">{{ card.name }}</h3>
                <p class="text-[12px] text-[#86868b]">{{ card.vendor }}</p>
              </div>
            </div>
            <div class="mt-[16px] flex flex-wrap gap-[8px]">
              <span class="rounded-full bg-[#0071e3]/8 px-[10px] py-[3px] text-[12px] font-[500] text-[#0071e3]">显存 {{ card.vram }}</span>
              <span class="rounded-full bg-[#6a5cff]/8 px-[10px] py-[3px] text-[12px] font-[500] text-[#6a5cff]">{{ card.scene }}</span>
            </div>
            <p class="mt-[12px] flex-1 text-[13px] leading-[21px] text-[#86868b]">{{ card.desc }}</p>
          </div>
        </div>
      </div>

      <!-- 适用场景 -->
      <div class="mt-[56px]">
        <div v-reveal="{ delay: 60 }" class="text-center">
          <h2 class="text-[26px] font-[700] text-[#1d1d1f] lg:text-[32px]">适用<span class="text-gradient">场景</span></h2>
          <p class="mt-[10px] text-[15px] text-[#86868b]">覆盖教学、科研、竞赛与应用部署全链路</p>
        </div>
        <div class="mt-[28px] grid gap-[20px] sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="(scene, index) in scenes"
            :key="scene.title"
            v-reveal="{ delay: 100 + index * 90 }"
            class="apple-card apple-card-hover group p-[26px]"
          >
            <div
              class="flex h-[56px] w-[56px] items-center justify-center rounded-[18px] text-[26px] shadow-[0_10px_28px_rgba(29,42,68,0.14)] transition-transform duration-500 group-hover:scale-110 group-hover:-rotate-6"
              :class="hueClass[scene.hue]"
            >
              {{ scene.icon }}
            </div>
            <h3 class="mt-[16px] text-[17px] font-[700] text-[#1d1d1f]">{{ scene.title }}</h3>
            <p class="mt-[8px] text-[13px] leading-[22px] text-[#86868b]">{{ scene.desc }}</p>
          </div>
        </div>
      </div>

      <!-- 提供方式：沟通-申请-审核 -->
      <div class="mt-[56px]">
        <div v-reveal="{ delay: 60 }" class="text-center">
          <h2 class="text-[26px] font-[700] text-[#1d1d1f] lg:text-[32px]">提供方式：<span class="text-gradient">沟通 · 申请 · 审核</span></h2>
          <p class="mt-[10px] text-[15px] text-[#86868b]">三步获取算力资源，保障资源合理分配与高效使用</p>
        </div>
        <div class="mt-[28px] grid gap-[20px] lg:grid-cols-3">
          <div
            v-for="(p, index) in processSteps"
            :key="p.step"
            v-reveal="{ delay: 100 + index * 120 }"
            class="apple-card apple-card-hover relative overflow-hidden p-[28px]"
          >
            <span class="pointer-events-none absolute -right-[10px] -top-[18px] text-[88px] font-[800] leading-none text-[#0071e3]/6 select-none">
              {{ p.step }}
            </span>
            <div class="flex items-center gap-[12px]">
              <div class="flex h-[48px] w-[48px] items-center justify-center rounded-[14px] bg-gradient-to-br from-[#0090ff] to-[#00c6ff] text-[22px] shadow-[0_10px_28px_rgba(0,144,255,0.3)]">
                {{ p.icon }}
              </div>
              <h3 class="text-[17px] font-[700] text-[#1d1d1f]">{{ p.title }}</h3>
            </div>
            <p class="mt-[14px] text-[13px] leading-[22px] text-[#86868b]">{{ p.desc }}</p>
            <div v-if="index < processSteps.length - 1" class="mt-[16px] hidden items-center gap-[8px] text-[12px] text-[#a1a1a6] lg:flex">
              <span>下一步</span>
              <svg class="h-[14px] w-[14px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M5 12h14M13 6l6 6-6 6"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 建设中 -->
      <div v-reveal="{ direction: 'scale' }" class="relative mt-[64px] overflow-hidden rounded-[28px] bg-gradient-to-br from-[#0b1220] via-[#16233c] to-[#0b1220] p-[48px] text-center shadow-[0_24px_80px_rgba(29,42,68,0.35)] lg:p-[64px]">
        <div class="pointer-events-none absolute left-[10%] top-[30%] h-40 w-40 rounded-full bg-[#0090ff]/25 blur-3xl"></div>
        <div class="pointer-events-none absolute right-[12%] bottom-[20%] h-44 w-44 rounded-full bg-[#6a5cff]/25 blur-3xl"></div>
        <div class="relative">
          <p class="inline-flex items-center gap-[8px] rounded-full border border-white/15 bg-white/8 px-[16px] py-[7px] text-[13px] font-[600] text-[#9bd8ff]">
            <span class="relative flex h-[8px] w-[8px]">
              <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#30d158] opacity-60"></span>
              <span class="relative inline-flex h-[8px] w-[8px] rounded-full bg-[#30d158]"></span>
            </span>
            平台正在建设中
          </p>
          <h2 class="mt-[20px] text-[28px] font-[700] text-white lg:text-[36px]">
            算力服务<span class="text-gradient">建设中</span>，敬请期待
          </h2>
          <p class="mx-auto mt-[14px] max-w-[560px] text-[14px] leading-[26px] text-[#a8b3c7]">
            算力服务正在加紧建设与调试中，上线后将开放算力申请入口。
            如有紧急算力需求，可通过「联系我们」页面与我们沟通。
          </p>
          <div class="mt-[28px] flex flex-wrap items-center justify-center gap-[14px]">
            <RouterLink
              to="/page/contact"
              class="inline-flex items-center gap-[6px] rounded-full bg-white px-[28px] py-[11px] text-[15px] font-[600] text-[#0b1220] transition-transform duration-300 hover:scale-105"
            >
              联系我们
            </RouterLink>
            <RouterLink
              to="/"
              class="inline-flex items-center gap-[6px] rounded-full border border-white/25 px-[28px] py-[11px] text-[15px] font-[600] text-white transition-colors duration-300 hover:bg-white/10"
            >
              返回首页
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
