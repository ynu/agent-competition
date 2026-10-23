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
    available: true
  },
  {
    name: 'NVIDIA L20',
    vendor: 'NVIDIA',
    vram: '48GB GDDR6',
    scene: '推理 / 中规模训练',
    desc: '数据中心级推理卡，大显存适合大模型推理服务与中等规模训练任务。',
    available: true
  },
  {
    name: '平头哥 PPU-810E',
    vendor: '阿里平头哥（国产）',
    vram: '96GB',
    scene: '大模型训练 / 推理',
    desc: '国产自研算力卡，超大显存适合大模型训练与推理，满足自主可控的信创场景需求。',
    available: true
  },
  {
    name: '更多算力卡',
    vendor: 'NVIDIA H100 / A800 / A100 等',
    vram: '规划中',
    scene: '训练 / 推理（建设中）',
    desc: 'H100、A800、A100 等更多算力卡正在接入建设中，敬请期待。',
    available: false
  }
]

// 适用场景
const scenes = [
  {
    title: '教学实验',
    desc: '人工智能课程实验、训练营实操，学生按需申请 GPU 资源完成作业与项目实践。'
  },
  {
    title: '科研训练',
    desc: '支持研究生与科研团队开展模型训练、微调与消融实验，加速科研成果产出。'
  },
  {
    title: '竞赛支撑',
    desc: '为参赛队伍提供算力保障，支撑智能体开发、模型优化与作品打磨。'
  },
  {
    title: '应用部署',
    desc: '智能体推理服务、校园 AI 应用上线部署，提供稳定的在线算力支撑。'
  }
]

// 提供方式：沟通 - 申请 - 审核
const processSteps = [
  {
    step: '01',
    title: '沟通咨询',
    desc: '通过联系方式与我们沟通，说明算力需求场景、规模与使用周期。'
  },
  {
    step: '02',
    title: '提交申请',
    desc: '填写算力使用申请，包括项目背景、所需算力卡类型、时长与预期成果。'
  },
  {
    step: '03',
    title: '审核评估',
    desc: '平台对申请进行审核评估，通过后分配算力资源并提供使用指引。'
  }
]
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
            <span class="h-[6px] w-[6px] rounded-full bg-gradient-to-r from-[#30d158] to-[#00c6ff] badge-dot"></span>
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
                <stop offset="50%" stop-color="#00c6ff"/>
                <stop offset="100%" stop-color="#7b5cff">
                  <animate attributeName="stop-color" values="#7b5cff;#30d158;#7b5cff" dur="3s" repeatCount="indefinite"/>
                </stop>
              </linearGradient>
              <linearGradient id="gpu-trace" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="#00c6ff"/>
                <stop offset="100%" stop-color="#30d158"/>
              </linearGradient>
              <filter id="gpu-glow" x="-60%" y="-60%" width="220%" height="220%">
                <feGaussianBlur stdDeviation="3" result="b"/>
                <feMerge>
                  <feMergeNode in="b"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            <rect width="420" height="320" rx="20" fill="url(#gpu-bg)"/>
            <!-- 电路走线:光脉冲沿线路流动 -->
            <g stroke="#2b3a55" stroke-width="2" fill="none">
              <path id="gpu-t1" d="M60 80 h60 v40 h50"/>
              <path id="gpu-t2" d="M360 240 h-70 v-40 h-40"/>
              <path d="M80 250 h80"/>
              <path d="M340 90 h-50"/>
            </g>
            <circle r="4" fill="#00c6ff" filter="url(#gpu-glow)">
              <animateMotion dur="1.6s" repeatCount="indefinite" keyPoints="0;1" keyTimes="0;1" calcMode="linear">
                <mpath href="#gpu-t1"/>
              </animateMotion>
              <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" dur="1.6s" repeatCount="indefinite"/>
            </circle>
            <circle r="4" fill="#30d158" filter="url(#gpu-glow)">
              <animateMotion dur="1.9s" begin="0.6s" repeatCount="indefinite">
                <mpath href="#gpu-t2"/>
              </animateMotion>
              <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" dur="1.9s" begin="0.6s" repeatCount="indefinite"/>
            </circle>
            <g fill="#3b82f6">
              <circle cx="60" cy="80" r="4"/>
              <circle cx="360" cy="240" r="4"/>
              <circle cx="80" cy="250" r="4"/>
              <circle cx="340" cy="90" r="4"/>
            </g>
            <!-- GPU 主体:整体呼吸浮动 -->
            <g class="gpu-float">
              <rect x="130" y="100" width="160" height="120" rx="14" fill="#1d2b45" stroke="#334a6b" stroke-width="2"/>
              <!-- 核心渐变芯片 + 辉光脉冲 -->
              <rect x="150" y="120" width="120" height="80" rx="8" fill="url(#gpu-chip)" filter="url(#gpu-glow)" class="gpu-core"/>
              <text x="210" y="168" text-anchor="middle" fill="#fff" font-size="26" font-weight="700" font-family="monospace">GPU</text>
              <!-- 扫描光束在芯片内往返 -->
              <rect x="152" y="122" width="6" height="76" rx="3" fill="#fff" opacity=".7" class="gpu-scan"/>
              <!-- 散热纹理 -->
              <g stroke="#334a6b" stroke-width="3" stroke-linecap="round">
                <path d="M110 115 v90"/><path d="M122 115 v90"/>
                <path d="M298 115 v90"/><path d="M310 115 v90"/>
              </g>
              <!-- 状态灯 -->
              <circle cx="150" cy="230" r="5" fill="#30d158">
                <animate attributeName="opacity" values="1;0.25;1" dur="1s" repeatCount="indefinite"/>
              </circle>
              <circle cx="170" cy="230" r="5" fill="#0090ff">
                <animate attributeName="opacity" values="0.25;1;0.25" dur="1s" repeatCount="indefinite"/>
              </circle>
              <!-- 数据吞吐指示条 -->
              <g class="gpu-bars">
                <rect x="252" y="222" width="6" height="10" rx="3" fill="#00c6ff"/>
                <rect x="262" y="218" width="6" height="14" rx="3" fill="#30d158"/>
                <rect x="272" y="224" width="6" height="8" rx="3" fill="#7b5cff"/>
              </g>
            </g>
            <!-- 环绕粒子 -->
            <circle r="3" fill="#00c6ff" opacity=".8" class="gpu-orb"/>
            <circle r="2.2" fill="#30d158" opacity=".7" class="gpu-orb gpu-orb2"/>
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
              <div class="h-[52px] w-[52px] shrink-0 transition-transform duration-500 group-hover:scale-110">
                <!-- RTX 4090:游戏旗舰 → 芯片矩阵 + 扫描光扫过核心 -->
                <svg v-if="card.name === 'NVIDIA RTX 4090'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                  <rect x="7" y="7" width="34" height="34" rx="8" fill="url(#cg-4090)" class="ic-breathe"/>
                  <g stroke="#fff" stroke-width="1.6" opacity=".55">
                    <path d="M14 14h6M14 20h6M14 28h6M14 34h6M28 14h6M28 20h6M28 28h6M28 34h6"/>
                  </g>
                  <rect x="21" y="21" width="6" height="6" rx="1.5" fill="#fff">
                    <animate attributeName="opacity" values="1;.4;1" dur="1.1s" repeatCount="indefinite"/>
                  </rect>
                  <rect x="12" y="10" width="4" height="28" rx="2" fill="#fff" opacity=".65" class="ic-sweep-x"/>
                  <defs>
                    <linearGradient id="cg-4090" x1="7" y1="7" x2="41" y2="41" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#ff9f1c"/><stop offset="1" stop-color="#ff4d6d"/>
                    </linearGradient>
                  </defs>
                </svg>
                <!-- L20:数据中心 → 数据柱状流 + 充能读数 -->
                <svg v-else-if="card.name === 'NVIDIA L20'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                  <rect x="4" y="10" width="40" height="28" rx="6" fill="url(#cg-l20)"/>
                  <g class="ic-eq" fill="#fff">
                    <rect x="11" y="20" width="4" height="8" rx="2"/>
                    <rect x="18" y="16" width="4" height="16" rx="2"/>
                    <rect x="25" y="22" width="4" height="6" rx="2"/>
                  </g>
                  <rect x="33" y="18" width="7" height="12" rx="2" fill="#fff" opacity=".85"/>
                  <rect x="35" y="26" width="3" height="2.4" rx="1" fill="#2563eb" class="ic-dot"/>
                  <path d="M13 38v4M24 38v4M35 38v4" stroke="#2563eb" stroke-width="3.4" stroke-linecap="round"/>
                  <defs>
                    <linearGradient id="cg-l20" x1="4" y1="10" x2="44" y2="38" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#38bdf8"/><stop offset="1" stop-color="#2563eb"/>
                    </linearGradient>
                  </defs>
                </svg>
                <!-- PPU-810E:国产超大显存 → 环绕轨道核心(信创卫星) -->
                <svg v-else-if="card.name === '平头哥 PPU-810E'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                  <circle cx="24" cy="24" r="20" stroke="#7c3aed" stroke-width="2" stroke-dasharray="9 7" opacity=".5" class="ic-spin-slow"/>
                  <ellipse cx="24" cy="24" rx="21" ry="9" stroke="#67e8f9" stroke-width="1.8" opacity=".55" class="ic-spin-rev"/>
                  <g class="ic-spin-rev"><circle cx="45" cy="24" r="3" fill="#67e8f9"/></g>
                  <circle cx="24" cy="24" r="11" fill="url(#cg-ppu)" class="ic-pump"/>
                  <path d="M20 24l3 3 5-6" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" class="ic-draw"/>
                  <defs>
                    <linearGradient id="cg-ppu" x1="13" y1="13" x2="35" y2="35" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#a78bfa"/><stop offset="1" stop-color="#7c3aed"/>
                    </linearGradient>
                  </defs>
                </svg>
                <!-- 更多算力卡:规划中 → 加号框点亮序列 -->
                <svg v-else viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                  <rect x="5" y="5" width="38" height="38" rx="9" stroke="#e11d48" stroke-width="2.6" stroke-dasharray="8 6" class="ic-spin-slow" opacity=".7"/>
                  <path d="M24 15v18M15 24h18" stroke="url(#cg-more)" stroke-width="4.6" stroke-linecap="round" class="ic-pulse"/>
                  <circle cx="40" cy="9" r="3" fill="#fde047" class="ic-tw"/>
                  <circle cx="8" cy="38" r="2.4" fill="#fb7185" class="ic-tw ic-d2"/>
                  <defs>
                    <linearGradient id="cg-more" x1="15" y1="15" x2="33" y2="33" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#fb7185"/><stop offset="1" stop-color="#e11d48"/>
                    </linearGradient>
                  </defs>
                </svg>
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
            <div class="h-[56px] w-[56px] transition-transform duration-500 group-hover:scale-110 group-hover:-rotate-6">
              <!-- 教学实验:黑板 + 粉笔书写 -->
              <svg v-if="scene.title === '教学实验'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <rect x="5" y="8" width="38" height="27" rx="5" fill="url(#cs-teach)"/>
                <rect x="5" y="8" width="38" height="27" rx="5" fill="none" stroke="#4f46e5" stroke-width="2.4"/>
                <path d="M24 35v5M15 41h18" stroke="#4f46e5" stroke-width="3" stroke-linecap="round"/>
                <path d="M12 16h9M12 22h13" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity=".85" class="ic-draw"/>
                <path d="M28 25l9-9 3.5 3.5-9 9-4 1z" fill="#fde047" class="ic-pen"/>
                <circle cx="37" cy="13" r="2" fill="#fde047" class="ic-tw"/>
                <defs>
                  <linearGradient id="cs-teach" x1="5" y1="8" x2="43" y2="35" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#60a5fa"/><stop offset="1" stop-color="#4f46e5"/>
                  </linearGradient>
                </defs>
              </svg>
              <!-- 科研训练:烧瓶沸腾 -->
              <svg v-else-if="scene.title === '科研训练'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <path d="M19 5h10" stroke="#0d9488" stroke-width="3.6" stroke-linecap="round"/>
                <path d="M20.8 5.5v11L9 36.2A4.2 4.2 0 0 0 12.8 42h22.4a4.2 4.2 0 0 0 3.8-5.8L27.2 16.5v-11Z" fill="url(#cs-research)" opacity=".28"/>
                <path class="ic-surf" d="M13.8 29h20.4l4.3 7.6a2.3 2.3 0 0 1-2 3.4H11.5a2.3 2.3 0 0 1-2-3.4L13.8 29Z" fill="url(#cs-research)"/>
                <path d="M11.5 29.5c2.5-2.2 4.9-2.2 7.4 0s4.9 2.2 7.4 0 4.9-2.2 7.4 0" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".85" class="ic-wave"/>
                <circle class="ic-fizz" cx="19" cy="25" r="2" fill="#fff"/>
                <circle class="ic-fizz ic-d2" cx="26" cy="23" r="1.6" fill="#fda4af"/>
                <circle class="ic-fizz ic-d3" cx="22.5" cy="20" r="1.3" fill="#fda4af"/>
                <defs>
                  <linearGradient id="cs-research" x1="10" y1="10" x2="38" y2="42" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#34d399"/><stop offset="1" stop-color="#0d9488"/>
                  </linearGradient>
                </defs>
              </svg>
              <!-- 竞赛支撑:奖杯闪耀 -->
              <svg v-else-if="scene.title === '竞赛支撑'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <path d="M16 6h16v9.5a8 8 0 0 1-16 0Z" fill="url(#cs-comp)" class="ic-breathe"/>
                <path d="M16 8.5h-4a4.5 4.5 0 0 0-4.5 4.5c0 4 3.4 7 7.9 7.3M32 8.5h4a4.5 4.5 0 0 1 4.5 4.5c0 4-3.4 7-7.9 7.3" stroke="#f97316" stroke-width="3.4" stroke-linecap="round"/>
                <path d="M24 23.5v6M17.5 33h13M14 38h20" stroke="#f97316" stroke-width="4" stroke-linecap="round"/>
                <rect x="18.5" y="7" width="3.6" height="14" rx="1.8" fill="#fff" opacity=".55" class="ic-glint"/>
                <path d="M40 4v7M36.5 7.5h7" stroke="#fb7185" stroke-width="2.8" stroke-linecap="round" class="ic-tw"/>
                <circle class="ic-rise" cx="8" cy="26" r="2" fill="#fb7185"/>
                <circle class="ic-rise ic-d2" cx="40" cy="28" r="1.8" fill="#fbbf24"/>
                <defs>
                  <linearGradient id="cs-comp" x1="16" y1="6" x2="32" y2="24" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#fbbf24"/><stop offset="1" stop-color="#f97316"/>
                  </linearGradient>
                </defs>
              </svg>
              <!-- 应用部署:火箭升空 -->
              <svg v-else viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                <g class="ic-launch">
                  <path d="M16 21 8.5 31H16M32 21l7.5 10H32" stroke="#6d28d9" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M24 3c5.4 5.1 7.9 11.6 7.9 18.4V28H16.1v-6.6C16.1 14.6 18.6 8.1 24 3Z" fill="url(#cs-deploy)"/>
                  <circle cx="24" cy="16.5" r="3.8" fill="#fff"/>
                  <circle cx="24" cy="16.5" r="3.8" stroke="#6d28d9" stroke-width="2"/>
                  <path class="ic-flame" d="M20.3 29.5c0 5.8 3.7 10.8 3.7 10.8s3.7-5 3.7-10.8c0-2-1.7-3.3-3.7-3.3s-3.7 1.3-3.7 3.3Z" fill="#fda4af"/>
                  <path class="ic-flame ic-f2" d="M22.1 29.5c0 3.5 1.9 6.6 1.9 6.6s1.9-3.1 1.9-6.6c0-1.2-.9-2-1.9-2s-1.9.8-1.9 2Z" fill="#fff"/>
                </g>
                <path class="ic-zoom" d="M2.5 15h6M1.5 22h7" stroke="#6d28d9" stroke-width="3" stroke-linecap="round"/>
                <defs>
                  <linearGradient id="cs-deploy" x1="16" y1="3" x2="32" y2="28" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#818cf8"/><stop offset="1" stop-color="#6d28d9"/>
                  </linearGradient>
                </defs>
              </svg>
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
              <div class="h-[48px] w-[48px] shrink-0">
                <!-- 沟通咨询:双气泡往复 -->
                <svg v-if="p.title === '沟通咨询'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                  <path d="M12 6h18a7 7 0 0 1 7 7v6a7 7 0 0 1-7 7H20l-7.5 7V26H12a7 7 0 0 1-7-7v-6a7 7 0 0 1 7-7Z" fill="url(#cp-chat1)" class="ic-jelly"/>
                  <circle class="ic-hop" cx="16" cy="16.5" r="2.6" fill="#fff"/>
                  <circle class="ic-hop ic-h2" cx="23" cy="16.5" r="2.6" fill="#fff"/>
                  <circle class="ic-hop ic-h3" cx="30" cy="16.5" r="2.6" fill="#fff"/>
                  <g class="ic-reply">
                    <path d="M36 26h2a5 5 0 0 1 5 5v3a5 5 0 0 1-5 5h-6l-4 3.5V39h-2" fill="none"/>
                    <circle cx="38.5" cy="32.5" r="4.8" fill="url(#cp-chat2)"/>
                    <circle cx="36.6" cy="32.5" r="1" fill="#fff"/>
                    <circle cx="38.5" cy="32.5" r="1" fill="#fff"/>
                    <circle cx="40.4" cy="32.5" r="1" fill="#fff"/>
                  </g>
                  <defs>
                    <linearGradient id="cp-chat1" x1="5" y1="6" x2="37" y2="26" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#22d3ee"/><stop offset="1" stop-color="#0891b2"/>
                    </linearGradient>
                    <linearGradient id="cp-chat2" x1="34" y1="28" x2="43" y2="38" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#bef264"/><stop offset="1" stop-color="#22d3ee"/>
                    </linearGradient>
                  </defs>
                </svg>
                <!-- 提交申请:文档 + 笔疾书 -->
                <svg v-else-if="p.title === '提交申请'" viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                  <g class="ic-bob">
                    <path d="M12 4h13l11 11v24a4 4 0 0 1-4 4H12a4 4 0 0 1-4-4V8a4 4 0 0 1 4-4Z" fill="#fff" stroke="url(#cp-apply)" stroke-width="3"/>
                    <path d="M25 4v11h11" stroke="url(#cp-apply)" stroke-width="3" stroke-linejoin="round"/>
                    <path d="M14 21h9" stroke="#9333ea" stroke-width="3.2" stroke-linecap="round"/>
                    <path d="M14 28h12" stroke="#fbbf24" stroke-width="3.2" stroke-linecap="round" class="ic-ink"/>
                    <g class="ic-scribe">
                      <path d="M25.5 28 35 18.5l4.2 4.2-9.5 9.5-5.4 1.2 1.2-5.4Z" fill="url(#cp-apply)"/>
                    </g>
                  </g>
                  <circle cx="42" cy="9" r="2.6" fill="#fbbf24" class="ic-tw"/>
                  <defs>
                    <linearGradient id="cp-apply" x1="8" y1="4" x2="39" y2="43" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#c084fc"/><stop offset="1" stop-color="#9333ea"/>
                    </linearGradient>
                  </defs>
                </svg>
                <!-- 审核评估:对勾盖章 + 双环对转 -->
                <svg v-else viewBox="0 0 48 48" class="h-full w-full" fill="none" aria-hidden="true">
                  <circle cx="24" cy="24" r="21.5" stroke="#16a34a" stroke-width="2.4" stroke-dasharray="6 8" opacity=".55" class="ic-spin-slow"/>
                  <circle cx="24" cy="24" r="16.5" stroke="#93c5fd" stroke-width="2.4" stroke-dasharray="13 8" opacity=".75" class="ic-spin-rev"/>
                  <circle cx="24" cy="24" r="12.5" fill="url(#cp-review)" class="ic-pump"/>
                  <path d="M17 24.5l5 5 9.5-11" stroke="#fff" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" class="ic-draw"/>
                  <defs>
                    <linearGradient id="cp-review" x1="12" y1="12" x2="36" y2="36" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#4ade80"/><stop offset="1" stop-color="#16a34a"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <h3 class="text-[17px] font-[700] text-[#1d1d1f]">{{ p.title }}</h3>
            </div>
            <p class="mt-[14px] text-[13px] leading-[22px] text-[#86868b]">{{ p.desc }}</p>
            <div v-if="index < processSteps.length - 1" class="mt-[16px] hidden items-center gap-[8px] text-[12px] text-[#a1a1a6] lg:flex">
              <span>下一步</span>
              <svg class="next-arrow h-[14px] w-[14px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M5 12h14M13 6l6 6-6 6"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 建设中 -->
      <div v-reveal="{ direction: 'scale' }" class="relative mt-[64px] overflow-hidden rounded-[28px] bg-gradient-to-br from-[#0b1220] via-[#16233c] to-[#0b1220] p-[48px] text-center shadow-[0_24px_80px_rgba(29,42,68,0.35)] lg:p-[64px]">
        <div class="pointer-events-none absolute left-[10%] top-[30%] h-40 w-40 rounded-full bg-[#0090ff]/25 blur-3xl anim-blob"></div>
        <div class="pointer-events-none absolute right-[12%] bottom-[20%] h-44 w-44 rounded-full bg-[#6a5cff]/25 blur-3xl anim-blob anim-blob-2"></div>
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
              to="/contact"
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

<style scoped>
/* ============ 图标通用动画 ============ */
svg [class^='ic-'],
svg [class*=' ic-'] {
  transform-box: fill-box;
  transform-origin: center;
}
.ic-breathe {
  animation: ic-breathe 2.2s ease-in-out infinite;
}
.ic-pump {
  animation: ic-pump 1.3s ease-in-out infinite;
}
.ic-pulse {
  animation: ic-pump 1.2s ease-in-out infinite;
}
.ic-tw {
  animation: ic-tw 1.3s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.ic-d2 {
  animation-delay: 0.35s;
}
.ic-h2 {
  animation-delay: 0.2s;
}
.ic-h3 {
  animation-delay: 0.4s;
}
.ic-d3 {
  animation-delay: 0.7s;
}
.ic-sweep-x {
  animation: ic-sweep-x 1.3s ease-in-out infinite;
}
.ic-dot {
  animation: ic-blink 1s ease-in-out infinite;
}
.ic-eq {
  animation: ic-eq 0.8s ease-in-out infinite;
}
.ic-spin-slow {
  animation: ic-spin 7s linear infinite;
}
.ic-spin-rev {
  animation: ic-spin 5s linear infinite reverse;
}
.ic-draw {
  stroke-dasharray: 20;
  animation: ic-draw 2.2s ease-in-out infinite;
}
.ic-pen {
  transform-origin: 90% 90%;
  animation: ic-pen 1.6s ease-in-out infinite;
}
.ic-surf {
  animation: ic-surf 1.7s ease-in-out infinite;
}
.ic-wave {
  animation: ic-wave 1.5s ease-in-out infinite alternate;
}
.ic-fizz {
  animation: ic-fizz 1.3s ease-out infinite;
}
.ic-glint {
  animation: ic-glint 1.9s ease-in-out infinite;
}
.ic-rise {
  animation: ic-rise 1.4s ease-out infinite;
}
.ic-launch {
  animation: ic-launch 1.6s cubic-bezier(0.34, 0, 0.64, 1) infinite;
}
.ic-flame {
  transform-origin: 50% 0%;
  animation: ic-flame 0.4s ease-in-out infinite alternate;
}
.ic-f2 {
  animation-duration: 0.32s;
}
.ic-zoom {
  animation: ic-zoom 1s ease-out infinite;
}
.ic-jelly {
  animation: ic-jelly 1.9s ease-in-out infinite;
}
.ic-hop {
  animation: ic-hop 0.95s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.ic-reply {
  animation: ic-popup 2.2s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.ic-bob {
  animation: ic-bob 1.5s ease-in-out infinite;
}
.ic-ink {
  stroke-dasharray: 12;
  animation: ic-ink 1.5s ease-in-out infinite;
}
.ic-scribe {
  transform-origin: 0% 100%;
  animation: ic-scribe 1.5s ease-in-out infinite;
}

@keyframes ic-breathe {
  0%, 100% { opacity: 0.85; transform: scale(0.96); }
  50% { opacity: 1; transform: scale(1.03); }
}
@keyframes ic-pump {
  0%, 100% { transform: scale(0.88); opacity: 0.8; }
  50% { transform: scale(1.08); opacity: 1; }
}
@keyframes ic-blink {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}
@keyframes ic-tw {
  0%, 100% { opacity: 0.1; transform: scale(0.4) rotate(-30deg); }
  50% { opacity: 1; transform: scale(1.1) rotate(0deg); }
}
@keyframes ic-sweep-x {
  0% { transform: translateX(0); opacity: 0; }
  15% { opacity: 0.65; }
  85% { opacity: 0.65; }
  100% { transform: translateX(24px); opacity: 0; }
}
@keyframes ic-eq {
  0%, 100% { transform: scaleY(0.45); }
  50% { transform: scaleY(1); }
}
@keyframes ic-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes ic-draw {
  0% { stroke-dashoffset: 20; }
  45%, 75% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: 0; opacity: 0.2; }
}
@keyframes ic-pen {
  0%, 100% { transform: rotate(0deg); }
  30% { transform: rotate(-8deg); }
  65% { transform: rotate(5deg); }
}
@keyframes ic-surf {
  0%, 100% { transform: scaleY(0.94); opacity: 0.85; }
  50% { transform: scaleY(1.05); opacity: 1; }
}
@keyframes ic-wave {
  from { transform: translateX(-3px); }
  to { transform: translateX(3px); }
}
@keyframes ic-fizz {
  0% { transform: translateY(4px) scale(0.6); opacity: 0; }
  30% { opacity: 1; }
  100% { transform: translateY(-10px) scale(1.2); opacity: 0; }
}
@keyframes ic-glint {
  0%, 100% { opacity: 0.15; transform: scaleX(0.5); }
  50% { opacity: 0.7; transform: scaleX(1); }
}
@keyframes ic-rise {
  0% { transform: translateY(4px) scale(0.7); opacity: 0; }
  30% { opacity: 1; }
  100% { transform: translateY(-10px) scale(1.1); opacity: 0; }
}
@keyframes ic-launch {
  0%, 100% { transform: translateY(2px) scale(1.02, 0.96); }
  45% { transform: translateY(-4px) scale(0.97, 1.05); }
  70% { transform: translateY(-2px) scale(1, 1); }
}
@keyframes ic-flame {
  from { transform: scale(0.62, 0.55); opacity: 0.65; }
  to { transform: scale(1.15, 1.3); opacity: 1; }
}
@keyframes ic-zoom {
  0% { transform: translateX(8px); opacity: 0; }
  30% { opacity: 1; }
  100% { transform: translateX(-9px); opacity: 0; }
}
@keyframes ic-jelly {
  0%, 100% { transform: scale(1, 1) rotate(0deg); }
  25% { transform: scale(0.96, 1.04) rotate(-2deg); }
  50% { transform: scale(1.03, 0.97) rotate(0deg); }
  75% { transform: scale(0.98, 1.02) rotate(2deg); }
}
@keyframes ic-hop {
  0%, 100% { transform: translateY(2.5px) scale(0.9); opacity: 0.45; }
  40% { transform: translateY(-4.5px) scale(1.08); opacity: 1; }
}
@keyframes ic-popup {
  0%, 50%, 100% { transform: translateY(8px) scale(0.3); opacity: 0; }
  62% { transform: translateY(-1px) scale(1.15); opacity: 1; }
  75% { transform: translateY(0) scale(1); opacity: 1; }
  92% { transform: translateY(0) scale(1); opacity: 0.85; }
}
@keyframes ic-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}
@keyframes ic-ink {
  0% { stroke-dashoffset: 12; }
  45%, 70% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: 12; }
}
@keyframes ic-scribe {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  30% { transform: translate(-2.5px, 1.5px) rotate(-9deg); }
  60% { transform: translate(1.5px, -0.5px) rotate(6deg); }
}

/* ============ GPU 插图动画 ============ */
.gpu-float {
  animation: gpu-float 3s ease-in-out infinite;
  transform-box: fill-box;
  transform-origin: center;
}
.gpu-core {
  transform-box: fill-box;
  transform-origin: center;
  animation: gpu-core 3s ease-in-out infinite;
}
.gpu-scan {
  transform-box: fill-box;
  animation: gpu-scan 1.4s ease-in-out infinite;
}
.gpu-bars {
  transform-box: fill-box;
  transform-origin: 50% 100%;
  animation: gpu-bars 0.9s ease-in-out infinite;
}
.gpu-orb {
  animation: gpu-orb 6s linear infinite;
}
.gpu-orb2 {
  animation-duration: 8s;
  animation-direction: reverse;
}

@keyframes gpu-float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}
@keyframes gpu-core {
  0%,
  100% {
    opacity: 0.85;
  }
  50% {
    opacity: 1;
  }
}
@keyframes gpu-scan {
  0% {
    transform: translateX(0);
    opacity: 0;
  }
  15% {
    opacity: 0.75;
  }
  85% {
    opacity: 0.75;
  }
  100% {
    transform: translateX(110px);
    opacity: 0;
  }
}
@keyframes gpu-bars {
  0%,
  100% {
    transform: scaleY(0.55);
  }
  50% {
    transform: scaleY(1);
  }
}
@keyframes gpu-orb {
  from {
    transform: rotate(0deg) translateX(190px) rotate(0deg);
  }
  to {
    transform: rotate(360deg) translateX(190px) rotate(-360deg);
  }
}
.anim-blob {
  animation: blob-drift 7s ease-in-out infinite alternate;
}
.anim-blob-2 {
  animation-duration: 9s;
  animation-delay: 1.5s;
}
@keyframes blob-drift {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(24px, -18px) scale(1.15);
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

/* 下一步箭头:向右滑动提示 */
.next-arrow {
  animation: next-slide 1.2s ease-in-out infinite;
}
@keyframes next-slide {
  0%,
  100% {
    transform: translateX(0);
    opacity: 0.7;
  }
  50% {
    transform: translateX(4px);
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .gpu-float,
  .gpu-core,
  .gpu-scan,
  .gpu-bars,
  .gpu-orb,
  .anim-blob,
  .badge-dot,
  .next-arrow,
  svg [class^='ic-'],
  svg [class*=' ic-'] {
    animation: none !important;
  }
}
</style>
