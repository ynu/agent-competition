<script setup lang="ts">
// 算力服务/首页 动态 SVG 图标(绚丽版)
// 48x48 视口,流动多彩渐变 + 辉光滤镜 + 多组并发动画
const props = withDefaults(
  defineProps<{
    name: string
    size?: number
  }>(),
  { size: 26 }
)

// 三色绚丽渐变(渐变色会随时间流动变换)
const palettes: Record<string, string[]> = {
  rtx4090: ['#ffd60a', '#ff2d78', '#ff9f0a'],
  l20: ['#00f5a0', '#00d4ff', '#0090ff'],
  ppu810e: ['#00e5ff', '#7b5cff', '#00ff9d'],
  more: ['#b14cff', '#ff4cd8', '#4c9dff'],
  teaching: ['#2d9cff', '#00d4ff', '#00f5a0'],
  research: ['#ff4cd8', '#7b5cff', '#00d4ff'],
  competition: ['#ffd60a', '#ff9f0a', '#ff2d55'],
  deploy: ['#ff9f0a', '#ff2d78', '#b14cff'],
  chat: ['#00d4ff', '#2d7dff', '#b14cff'],
  apply: ['#7b5cff', '#b14cff', '#ff4cd8'],
  review: ['#00f5a0', '#00d4ff', '#7b5cff'],
  agent: ['#00d4ff', '#2d7dff', '#b14cff'],
  build: ['#b14cff', '#00d4ff', '#ff4cd8'],
  experience: ['#ff4c8f', '#ff9f0a', '#ff2d78'],
  plaza: ['#ffb14c', '#ff2d78', '#b14cff'],
  speed: ['#00d4ff', '#00f5a0', '#ffd60a'],
  security: ['#00f5a0', '#00d4ff', '#7b5cff'],
  models: ['#b14cff', '#00d4ff', '#00f5a0'],
  multimodal: ['#ff9f0a', '#ff2d78', '#b14cff']
}

const colors = palettes[props.name] ?? ['#00d4ff', '#2d7dff', '#b14cff']
const c1 = colors[0]
const c2 = colors[1]
const c3 = colors[2]

// 每个实例独立 id,避免同页多实例冲突
const uid = Math.random().toString(36).slice(2, 9)
const gid = `${uid}-g`
const fid = `${uid}-f`
const cid = `${uid}-c`
const gref = `url(#${gid})`
const fref = `url(#${fid})`
const cref = `url(#${cid})`
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 48 48"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="ci"
    aria-hidden="true"
  >
    <defs>
      <!-- 流动渐变:三个色标循环变换 -->
      <linearGradient :id="gid" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
        <stop offset="0" :stop-color="c1">
          <animate attributeName="stop-color" :values="`${c1};${c2};${c1}`" dur="2.5s" repeatCount="indefinite" />
        </stop>
        <stop offset="0.5" :stop-color="c2">
          <animate attributeName="stop-color" :values="`${c2};${c3};${c2}`" dur="2.5s" repeatCount="indefinite" />
        </stop>
        <stop offset="1" :stop-color="c3">
          <animate attributeName="stop-color" :values="`${c3};${c1};${c3}`" dur="2.5s" repeatCount="indefinite" />
        </stop>
      </linearGradient>
      <!-- 辉光滤镜 -->
      <filter :id="fid" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="1.6" result="b" />
        <feMerge>
          <feMergeNode in="b" />
          <feMergeNode in="b" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
      <clipPath v-if="name === 'competition'" :id="cid">
        <path d="M17 7h14v9a7 7 0 0 1-14 0Z" />
      </clipPath>
    </defs>

    <!-- RTX 4090:芯片 + 扫描光束 + 四角闪烁 -->
    <g v-if="name === 'rtx4090'" :stroke="gref" stroke-width="2.2" stroke-linecap="round">
      <path d="M17 5v5M24 5v5M31 5v5M17 38v5M24 38v5M31 38v5M5 20h5M5 28h5M38 20h5M38 28h5" opacity=".75" />
      <rect x="9.5" y="9.5" width="29" height="29" rx="6" fill="#fff" fill-opacity=".05" stroke-width="2.4" />
      <rect class="a-pulse" x="17.5" y="17.5" width="13" height="13" rx="3.5" :fill="gref" stroke="none" :filter="fref" />
      <rect x="18.5" y="18.5" width="3" height="11" rx="1.5" fill="#fff" opacity=".9" stroke="none">
        <animateTransform attributeName="transform" type="translate" values="0 0;8 0;0 0" dur="1s" calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1" repeatCount="indefinite" />
      </rect>
      <circle class="a-blink" cx="13.5" cy="13.5" r="1.6" :fill="c2" stroke="none" />
      <circle class="a-blink a-d2" cx="34.5" cy="13.5" r="1.6" :fill="c1" stroke="none" />
      <circle class="a-blink a-d3" cx="13.5" cy="34.5" r="1.6" :fill="c1" stroke="none" />
      <circle class="a-blink a-d2" cx="34.5" cy="34.5" r="1.6" :fill="c2" stroke="none" />
    </g>

    <!-- L20:数据流虚线滚动 + 状态灯 -->
    <g v-else-if="name === 'l20'" :stroke="gref" stroke-width="2.4" stroke-linecap="round">
      <rect x="6" y="13" width="36" height="22" rx="5" fill="#fff" fill-opacity=".05" />
      <path class="a-flow" d="M11 20.5h26" :stroke="c1" stroke-width="2.2" stroke-dasharray="5 8" fill="none" />
      <path class="a-flow a-flow2" d="M11 27.5h26" :stroke="c2" stroke-width="2.2" stroke-dasharray="5 8" fill="none" />
      <path d="M15 35v5M24 35v5M33 35v5" opacity=".7" />
      <circle class="a-pulse" cx="38.5" cy="24" r="2" :fill="c2" stroke="none" :filter="fref" />
    </g>

    <!-- PPU-810E:双轨道反向旋转 + 脉冲核心 -->
    <g v-else-if="name === 'ppu810e'" :stroke="gref" stroke-width="2.2" stroke-linecap="round">
      <circle class="a-spin" cx="24" cy="24" r="18" fill="none" stroke-width="1.6" stroke-dasharray="6 10" opacity=".6" />
      <ellipse class="a-spin-rev" cx="24" cy="24" rx="19" ry="8" fill="none" :stroke="c2" stroke-width="1.5" opacity=".45" />
      <g class="a-spin">
        <circle cx="24" cy="6" r="3" :fill="c1" stroke="none" :filter="fref" />
      </g>
      <g class="a-spin-rev">
        <circle cx="43" cy="24" r="2.2" :fill="c2" stroke="none" />
      </g>
      <rect class="a-pulse" x="16" y="16" width="16" height="16" rx="5" :fill="gref" stroke="none" :filter="fref" />
      <rect x="21" y="21" width="6" height="6" rx="2" fill="#fff" opacity=".95" stroke="none" />
    </g>

    <!-- 更多算力卡:旋转虚线环 + 呼吸星芒 -->
    <g v-else-if="name === 'more'" stroke-linecap="round">
      <circle class="a-spin" cx="24" cy="24" r="19" fill="none" :stroke="c2" stroke-width="1.5" stroke-dasharray="3 9" opacity=".55" />
      <path
        class="a-star"
        d="M24 6C25.8 19 29 22.2 42 24 29 25.8 25.8 29 24 42 22.2 29 19 25.8 6 24 19 22.2 22.2 19 24 6Z"
        :fill="gref"
        :filter="fref"
      />
      <path class="a-tw" d="M39 5.5v8M35 9.5h8" :stroke="c1" stroke-width="2.4" />
      <path class="a-tw a-d2" d="M8.5 34v6M5.5 37h6" :stroke="c3" stroke-width="2.2" />
      <path class="a-tw a-d3" d="M36 32.5v6M33 35.5h6" :stroke="c2" stroke-width="2" />
    </g>

    <!-- 教学实验:学士帽 + 摆动流苏 + 上升星光 -->
    <g v-else-if="name === 'teaching'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M24 9 44 17.5 24 26 4 17.5Z" fill="#fff" fill-opacity=".05" />
      <path d="M13.5 22.5V32c0 3.2 4.7 5.8 10.5 5.8s10.5-2.6 10.5-5.8v-9.5" fill="none" />
      <g class="a-tassel">
        <path d="M43 17.5v10" :stroke="c1" stroke-width="2.2" />
        <circle class="a-pulse" cx="43" cy="30.5" r="2.4" :fill="c1" stroke="none" :filter="fref" />
      </g>
      <path class="a-rise" d="M8 37.5v4M6 39.5h4" :stroke="c2" stroke-width="1.8" />
      <path class="a-rise a-d2" d="M14.5 41v3.4M12.8 42.7h3.4" :stroke="c1" stroke-width="1.6" />
      <path class="a-tw" d="M24 3v4M22 5h4" :stroke="c2" stroke-width="1.8" />
    </g>

    <!-- 科研训练:锥形瓶 + 渐变液体 + 波浪气泡 -->
    <g v-else-if="name === 'research'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M19.5 5.5h9" />
      <path d="M21.5 5.5v11L10.5 36.5A3.4 3.4 0 0 0 13.6 41.5h20.8a3.4 3.4 0 0 0 3.1-5L26.5 16.5v-11" fill="#fff" fill-opacity=".05" />
      <path class="a-liquid" d="M15.2 30.5h17.6l3.6 6.4a1.9 1.9 0 0 1-1.7 2.8H13.3a1.9 1.9 0 0 1-1.7-2.8l3.6-6.4Z" :fill="gref" stroke="none" opacity=".85" />
      <path class="a-wave" d="M13 30.5c2.2-1.8 4.2-1.8 6.4 0s4.2 1.8 6.4 0 4.2-1.8 6.4 0" fill="none" stroke="#fff" stroke-width="1.8" opacity=".85" />
      <circle class="a-bub" cx="19.5" cy="27.5" r="1.8" fill="#fff" stroke="none" opacity=".9" />
      <circle class="a-bub a-d2" cx="26" cy="26" r="1.4" :fill="c1" stroke="none" />
      <circle class="a-bub a-d3" cx="23" cy="23.5" r="1.2" :fill="c2" stroke="none" />
      <path class="a-tw" d="M36 8.5v5M33.5 11h5" :stroke="c1" stroke-width="2" />
    </g>

    <!-- 竞赛支撑:渐变奖杯 + 高光扫过 + 闪耀 -->
    <g v-else-if="name === 'competition'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M17 7h14v9a7 7 0 0 1-14 0Z" :fill="gref" :filter="fref" opacity=".92" />
      <g :clip-path="cref">
        <rect class="a-shine" x="17.5" y="7" width="3.5" height="17" rx="1.75" fill="#fff" opacity=".6" stroke="none" />
      </g>
      <path d="M17 9.5h-3.5a3.5 3.5 0 0 0-3.5 3.5c0 3.5 3 6.2 6.8 6.4" fill="none" />
      <path d="M31 9.5h3.5a3.5 3.5 0 0 1 3.5 3.5c0 3.5-3 6.2-6.8 6.4" fill="none" />
      <path d="M24 23v6M18 33h12M15 37.5h18" />
      <path class="a-tw" d="M38 4.5v6M35 7.5h6" :stroke="c1" stroke-width="2.2" />
      <path class="a-tw a-d3" d="M9 12v5M6.5 14.5h5" :stroke="c2" stroke-width="2" />
      <path class="a-rise" d="M35.5 27v4M33.5 29h4" :stroke="c3" stroke-width="1.8" />
    </g>

    <!-- 应用部署:火箭悬浮 + 跳动尾焰 + 星点 -->
    <g v-else-if="name === 'deploy'" stroke-linecap="round" stroke-linejoin="round">
      <path class="a-tw" d="M10.5 7.5v4M8.5 9.5h4" :stroke="c2" stroke-width="1.8" />
      <path class="a-tw a-d2" d="M40 14v4M38 16h4" :stroke="c1" stroke-width="1.8" />
      <g class="a-bob">
        <path d="M24 4.5c5 4.8 7.3 10.8 7.3 17V28H16.7v-6.5c0-6.2 2.3-12.2 7.3-17Z" :fill="gref" :filter="fref" opacity=".92" />
        <circle cx="24" cy="17.5" r="3.4" fill="#fff" fill-opacity=".92" stroke="none" />
        <circle cx="24" cy="17.5" r="3.4" fill="none" :stroke="c2" stroke-width="1.6" />
        <path d="M16.7 22 10 31h6.7M31.3 22 38 31h-6.7" fill="none" :stroke="gref" stroke-width="2.4" />
        <path class="a-flame" d="M20.8 30.5c0 5 3.2 9.5 3.2 9.5s3.2-4.5 3.2-9.5c0-1.7-1.4-2.9-3.2-2.9s-3.2 1.2-3.2 2.9Z" :fill="c1" stroke="none" opacity=".95" />
      </g>
      <path class="a-speed" d="M5 17h5M3.5 23H9" :stroke="c2" stroke-width="2.2" />
    </g>

    <!-- 沟通咨询:对话气泡 + 弹跳打字点 + 小气泡 -->
    <g v-else-if="name === 'chat'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path class="a-float" d="M13 8h22a6.5 6.5 0 0 1 6.5 6.5v9A6.5 6.5 0 0 1 35 30H23.5L15 38v-8h-2A6.5 6.5 0 0 1 6.5 23.5v-9A6.5 6.5 0 0 1 13 8Z" fill="#fff" fill-opacity=".05" />
      <circle class="a-bounce" cx="17.5" cy="21.5" r="2.6" :fill="c1" stroke="none" :filter="fref" />
      <circle class="a-bounce a-d2" cx="24" cy="21.5" r="2.6" :fill="c2" stroke="none" />
      <circle class="a-bounce a-d3" cx="30.5" cy="21.5" r="2.6" :fill="c3" stroke="none" />
      <g class="a-pop">
        <circle cx="40" cy="37" r="4.5" :fill="c2" stroke="none" opacity=".85" />
        <circle cx="38.2" cy="37" r=".9" fill="#fff" stroke="none" />
        <circle cx="40.6" cy="37" r=".9" fill="#fff" stroke="none" />
        <circle cx="43" cy="37" r=".9" fill="#fff" stroke="none" />
      </g>
    </g>

    <!-- 提交申请:文档 + 书写笔迹 + 笔尖高光 -->
    <g v-else-if="name === 'apply'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M13 5.5h13.5L35 14v22.5a4 4 0 0 1-4 4H13a4 4 0 0 1-4-4v-27a4 4 0 0 1 4-4Z" fill="#fff" fill-opacity=".05" />
      <path d="M26.5 5.5V14H35" fill="none" opacity=".75" />
      <path d="M14.5 20.5h11" :stroke="c2" />
      <path class="a-write" d="M14.5 26.5h13" :stroke="c1" />
      <g class="a-pen">
        <path d="M27.5 27.5 36.5 18.5l3.2 3.2-9 9-4.4 1.2 1.2-4.4Z" :fill="c1" stroke="none" :filter="fref" opacity=".95" />
      </g>
      <path class="a-tw" d="M40 8.5v5M37.5 11h5" :stroke="c3" stroke-width="2" />
    </g>

    <!-- 审核评估:双向旋转刻度环 + 辉光对勾 -->
    <g v-else-if="name === 'review'" stroke-linecap="round" stroke-linejoin="round">
      <circle class="a-spin" cx="24" cy="24" r="20" fill="none" :stroke="gref" stroke-width="2" stroke-dasharray="4 7" opacity=".55" />
      <circle class="a-spin-rev" cx="24" cy="24" r="15.5" fill="none" :stroke="c2" stroke-width="2" stroke-dasharray="10 6" opacity=".7" />
      <path class="a-check" d="M15.5 24.5l6.5 6.5L33 17.5" fill="none" :stroke="c1" stroke-width="3.2" :filter="fref" />
    </g>

    <!-- 什么是智能体:机器人 + 扫描线 + 眨眼 -->
    <g v-else-if="name === 'agent'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M24 5v4.5" />
      <circle class="a-pulse" cx="24" cy="4.5" r="2.2" :fill="c1" stroke="none" :filter="fref" />
      <rect class="a-float" x="8.5" y="12" width="31" height="25" rx="7.5" fill="#fff" fill-opacity=".05" />
      <rect class="a-scan" x="10.5" y="14" width="27" height="2.4" rx="1.2" :fill="c2" stroke="none" opacity=".65" />
      <circle class="a-eye" cx="17.5" cy="22.5" r="2.8" :fill="c1" stroke="none" :filter="fref" />
      <circle class="a-eye a-d2" cx="30.5" cy="22.5" r="2.8" :fill="c2" stroke="none" />
      <path class="a-smile" d="M18.5 29.5c3.5 3.2 7.5 3.2 11 0" fill="none" :stroke="c1" />
      <path d="M8.5 20.5h-3M39.5 20.5h3" opacity=".6" />
      <circle class="a-blink" cx="13.8" cy="27" r="1.4" :fill="c3" stroke="none" opacity=".8" />
      <circle class="a-blink a-d3" cx="34.2" cy="27" r="1.4" :fill="c3" stroke="none" opacity=".8" />
    </g>

    <!-- 快速搭建:积木逐块点亮 + 连接线流动 -->
    <g v-else-if="name === 'build'" stroke-linecap="round" stroke-linejoin="round">
      <rect class="a-blk" x="4.5" y="27" width="16" height="16" rx="4" :fill="c1" fill-opacity=".18" :stroke="c1" stroke-width="2.2" />
      <rect class="a-blk a-d2" x="27.5" y="27" width="16" height="16" rx="4" :fill="c2" fill-opacity=".18" :stroke="c2" stroke-width="2.2" />
      <rect class="a-blk a-d3" x="16" y="6" width="16" height="16" rx="4" :fill="c3" fill-opacity=".2" :stroke="c3" stroke-width="2.2" />
      <path class="a-link" d="M12.5 27v-5.5a3 3 0 0 1 3-3h.5M24 22.5v4.5M31.5 27v-5.5a3 3 0 0 0-3-3h-.5" fill="none" :stroke="gref" stroke-width="2" stroke-dasharray="28" opacity=".85" />
    </g>

    <!-- 体验智能体:播放键脉动 + 均衡器音波 -->
    <g v-else-if="name === 'experience'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path class="a-float" d="M8.5 7h31A4 4 0 0 1 43.5 11v16a4 4 0 0 1-4 4H20l-8.5 8v-8h-3A4 4 0 0 1 4.5 27V11A4 4 0 0 1 8.5 7Z" fill="#fff" fill-opacity=".05" />
      <path class="a-play" d="M17.5 13v12l10-6-10-6Z" :fill="gref" stroke="none" :filter="fref" />
      <rect class="a-bar" x="32" y="16.5" width="2.6" height="7" rx="1.3" :fill="c1" stroke="none" />
      <rect class="a-bar a-d2" x="37" y="14" width="2.6" height="12" rx="1.3" :fill="c2" stroke="none" />
    </g>

    <!-- 智能体广场:四色节点 + 脉冲扩散 -->
    <g v-else-if="name === 'plaza'" :stroke="gref" stroke-width="2" stroke-linecap="round">
      <path d="M14.5 10h19M10 14.5v19M38 14.5v19M14.5 38h19" opacity=".45" />
      <circle class="a-node" cx="10" cy="10" r="4.5" :fill="c1" fill-opacity=".2" :stroke="c1" stroke-width="2.2" />
      <circle class="a-node a-d2" cx="38" cy="10" r="4.5" :fill="c2" fill-opacity=".2" :stroke="c2" stroke-width="2.2" />
      <circle class="a-node a-d3" cx="10" cy="38" r="4.5" :fill="c3" fill-opacity=".2" :stroke="c3" stroke-width="2.2" />
      <circle class="a-node a-d2" cx="38" cy="38" r="4.5" :fill="c1" fill-opacity=".2" :stroke="c1" stroke-width="2.2" />
      <circle class="a-pulse" cx="24" cy="24" r="3.2" :fill="c1" stroke="none" :filter="fref" />
      <circle class="a-ring" cx="24" cy="24" r="6" fill="none" :stroke="c2" stroke-width="1.6" />
    </g>

    <!-- 极速响应:双层旋转环 + 辉光闪电 -->
    <g v-else-if="name === 'speed'" stroke-linecap="round" stroke-linejoin="round">
      <circle class="a-spin" cx="24" cy="24" r="19.5" fill="none" :stroke="c2" stroke-width="2" stroke-dasharray="24 12 6 12" opacity=".8" />
      <circle class="a-spin-rev" cx="24" cy="24" r="14" fill="none" :stroke="c3" stroke-width="1.5" stroke-dasharray="4 8" opacity=".5" />
      <path class="a-bolt" d="M27 8 14.5 26.5H22L21 40 33.5 21.5H26L27 8Z" :fill="gref" :filter="fref" />
      <path class="a-speed" d="M3.5 24h4" :stroke="c1" stroke-width="2.4" />
    </g>

    <!-- 安全合规:双层盾牌 + 辉光对勾 -->
    <g v-else-if="name === 'security'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path class="a-float" d="M24 4.5 40.5 10.5v13c0 10.3-7 16.7-16.5 20-9.5-3.3-16.5-9.7-16.5-20v-13L24 4.5Z" fill="#fff" fill-opacity=".05" />
      <path class="a-shield" d="M24 9.5 36 13.8v9.7c0 7.4-5 12-12 14.6-7-2.6-12-7.2-12-14.6v-9.7L24 9.5Z" :fill="gref" stroke="none" opacity=".22" />
      <path class="a-check2" d="M16.5 23.5l5.5 5.5 10.5-11.5" fill="none" :stroke="c1" stroke-width="3" :filter="fref" />
      <path class="a-tw" d="M40.5 30.5v5M38 33h5" :stroke="c2" stroke-width="2" />
    </g>

    <!-- 多模型接入:面板文字扫描 + 指示点轮播 -->
    <g v-else-if="name === 'models'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <rect class="a-float" x="5" y="8" width="29" height="21" rx="4.5" fill="#fff" fill-opacity=".05" />
      <path d="M38 10.5a4.5 4.5 0 0 1 4.5 4.5v13a4.5 4.5 0 0 1-4.5 4.5H17" fill="none" opacity=".45" />
      <path class="a-line" d="M10.5 15h18" :stroke="c2" />
      <path class="a-line a-d2" d="M10.5 21h12" :stroke="c1" />
      <g class="a-dots">
        <circle class="a-blink" cx="12" cy="35.5" r="2" :fill="c1" stroke="none" />
        <circle class="a-blink a-d2" cx="19" cy="35.5" r="2" :fill="c2" stroke="none" />
        <circle class="a-blink a-d3" cx="26" cy="35.5" r="2" :fill="c3" stroke="none" />
      </g>
    </g>

    <!-- 多模态生成:调色盘 + 彩点脉冲 + 波纹 -->
    <g v-else-if="name === 'multimodal'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path class="a-float" d="M24 6c9.9 0 18 7.2 18 16.3 0 5.1-4.1 7.7-8.7 7.7h-3.6c-2.9 0-4.6 2-4.6 4.3 0 1.2.5 2.2 1.2 3.2.6.9 1.2 1.8 1.2 3 0 2.1-1.6 3.5-3.5 3.5C14.1 44 6 35.5 6 25S14.1 6 24 6Z" fill="#fff" fill-opacity=".05" />
      <circle class="a-dotc" cx="16" cy="19.5" r="2.8" :fill="c1" stroke="none" :filter="fref" />
      <circle class="a-dotc a-d2" cx="24" cy="14.5" r="2.8" :fill="c2" stroke="none" />
      <circle class="a-dotc a-d3" cx="32" cy="19.5" r="2.8" :fill="c3" stroke="none" />
      <path class="a-wave" d="M12 27.5c1.8-1.5 3.6-1.5 5.4 0s3.6 1.5 5.4 0" fill="none" :stroke="c2" stroke-width="1.8" opacity=".6" />
    </g>
  </svg>
</template>

<style scoped>
.ci {
  display: block;
}

/* 所有动画元素默认围绕自身中心变换 */
.ci [class^='a-'],
.ci [class*=' a-'] {
  transform-box: fill-box;
  transform-origin: center;
}

.a-pulse {
  animation: ci-pulse 1s ease-in-out infinite;
}
.a-spin {
  animation: ci-spin 3s linear infinite;
}
.a-spin-rev {
  animation: ci-spin-rev 4.5s linear infinite;
}
.a-float {
  animation: ci-float 1.6s ease-in-out infinite;
}
.a-blink {
  animation: ci-blink 1s ease-in-out infinite;
}
.a-tw {
  animation: ci-tw 1.1s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.a-d2 {
  animation-delay: 0.2s;
}
.a-d3 {
  animation-delay: 0.4s;
}
.a-flow {
  animation: ci-flow 0.7s linear infinite;
}
.a-flow2 {
  animation-duration: 0.95s;
  animation-direction: reverse;
}
.a-star {
  animation: ci-star 2s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.a-tassel {
  transform-origin: 50% 0%;
  animation: ci-tassel 1.3s cubic-bezier(0.45, 0, 0.55, 1) infinite;
}
.a-rise {
  animation: ci-rise 1.3s ease-out infinite;
}
.a-liquid {
  animation: ci-liquid 1.4s ease-in-out infinite;
}
.a-wave {
  animation: ci-wave 1.2s ease-in-out infinite alternate;
}
.a-bub {
  animation: ci-bub 1.2s ease-out infinite;
}
.a-shine {
  animation: ci-shine 1.4s ease-in-out infinite;
}
.a-bob {
  animation: ci-bob 1.5s ease-in-out infinite;
}
.a-flame {
  transform-origin: 50% 0%;
  animation: ci-flame 0.4s ease-in-out infinite alternate;
}
.a-speed {
  animation: ci-speed 0.7s ease-out infinite;
}
.a-bounce {
  animation: ci-bounce 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.a-pop {
  animation: ci-pop 1.5s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.a-write {
  stroke-dasharray: 13;
  animation: ci-write 1.3s ease-in-out infinite;
}
.a-pen {
  transform-origin: 0% 100%;
  animation: ci-pen 1.3s ease-in-out infinite;
}
.a-check {
  stroke-dasharray: 27;
  animation: ci-check 1.5s ease-in-out infinite;
}
.a-check2 {
  stroke-dasharray: 26;
  animation: ci-check2 1.6s ease-in-out infinite;
}
.a-scan {
  animation: ci-scan 1.4s ease-in-out infinite;
}
.a-eye {
  animation: ci-eye 1.6s ease-in-out infinite;
}
.a-smile {
  stroke-dasharray: 14;
  animation: ci-smile 1.6s ease-in-out infinite;
}
.a-blk {
  animation: ci-blk 1.35s ease-in-out infinite;
}
.a-link {
  animation: ci-link 1.35s ease-in-out infinite;
}
.a-play {
  animation: ci-play 1s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.a-bar {
  animation: ci-bar 0.55s ease-in-out infinite;
}
.a-node {
  animation: ci-blink 1.2s ease-in-out infinite;
}
.a-ring {
  animation: ci-ring 1.3s ease-out infinite;
}
.a-bolt {
  animation: ci-bolt 1.1s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.a-shield {
  animation: ci-liquid 1.5s ease-in-out infinite;
}
.a-line {
  stroke-dasharray: 18;
  animation: ci-flow 1.3s ease-in-out infinite;
}
.a-dots {
  animation: ci-dots 1.2s ease-in-out infinite;
}
.a-dotc {
  animation: ci-dotc 1.2s ease-in-out infinite;
}

@keyframes ci-pulse {
  0%,
  100% {
    opacity: 0.5;
    transform: scale(0.85);
  }
  50% {
    opacity: 1;
    transform: scale(1.12);
  }
}
@keyframes ci-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
@keyframes ci-spin-rev {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(-360deg);
  }
}
@keyframes ci-float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3.5px);
  }
}
@keyframes ci-blink {
  0%,
  100% {
    opacity: 0.15;
  }
  45% {
    opacity: 1;
  }
}
@keyframes ci-tw {
  0%,
  100% {
    opacity: 0.1;
    transform: scale(0.45) rotate(-25deg);
  }
  50% {
    opacity: 1;
    transform: scale(1.05) rotate(0deg);
  }
}
@keyframes ci-flow {
  0% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: -26;
  }
}
@keyframes ci-star {
  0%,
  100% {
    transform: scale(0.78) rotate(-20deg);
  }
  50% {
    transform: scale(1.18) rotate(20deg);
  }
}
@keyframes ci-tassel {
  0%,
  100% {
    transform: rotate(-16deg);
  }
  50% {
    transform: rotate(16deg);
  }
}
@keyframes ci-rise {
  0% {
    transform: translateY(5px);
    opacity: 0;
  }
  30% {
    opacity: 1;
  }
  100% {
    transform: translateY(-11px);
    opacity: 0;
  }
}
@keyframes ci-liquid {
  0%,
  100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}
@keyframes ci-wave {
  from {
    transform: translateX(-3.5px);
  }
  to {
    transform: translateX(3.5px);
  }
}
@keyframes ci-bub {
  0% {
    transform: translateY(5px) scale(0.7);
    opacity: 0;
  }
  30% {
    opacity: 1;
  }
  100% {
    transform: translateY(-11px) scale(1.15);
    opacity: 0;
  }
}
@keyframes ci-shine {
  0% {
    transform: translateX(-6px);
    opacity: 0;
  }
  30% {
    opacity: 0.85;
  }
  55%,
  100% {
    transform: translateX(14px);
    opacity: 0;
  }
}
@keyframes ci-bob {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  30% {
    transform: translateY(-3.5px) rotate(-4deg);
  }
  70% {
    transform: translateY(-1px) rotate(4deg);
  }
}
@keyframes ci-flame {
  from {
    transform: scale(0.65, 0.6);
    opacity: 0.65;
  }
  to {
    transform: scale(1.12, 1.22);
    opacity: 1;
  }
}
@keyframes ci-speed {
  0% {
    transform: translateX(6px);
    opacity: 0;
  }
  30% {
    opacity: 1;
  }
  100% {
    transform: translateX(-8px);
    opacity: 0;
  }
}
@keyframes ci-bounce {
  0%,
  100% {
    transform: translateY(1.5px);
    opacity: 0.35;
  }
  40% {
    transform: translateY(-5px);
    opacity: 1;
  }
}
@keyframes ci-pop {
  0%,
  50%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  60% {
    transform: scale(1.25);
    opacity: 1;
  }
  72% {
    transform: scale(1);
    opacity: 1;
  }
  90% {
    transform: scale(1);
    opacity: 0.85;
  }
}
@keyframes ci-write {
  0% {
    stroke-dashoffset: 13;
  }
  45%,
  70% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: 13;
  }
}
@keyframes ci-pen {
  0%,
  100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(-10deg);
  }
  60% {
    transform: rotate(7deg);
  }
}
@keyframes ci-check {
  0% {
    stroke-dashoffset: 27;
    opacity: 1;
  }
  45% {
    stroke-dashoffset: 0;
    opacity: 1;
  }
  78% {
    stroke-dashoffset: 0;
    opacity: 1;
  }
  100% {
    stroke-dashoffset: 0;
    opacity: 0;
  }
}
@keyframes ci-check2 {
  0% {
    stroke-dashoffset: 26;
  }
  45%,
  80% {
    stroke-dashoffset: 0;
    opacity: 1;
  }
  100% {
    stroke-dashoffset: 0;
    opacity: 0;
  }
}
@keyframes ci-scan {
  0% {
    transform: translateY(0);
    opacity: 0;
  }
  15% {
    opacity: 0.85;
  }
  85% {
    opacity: 0.85;
  }
  100% {
    transform: translateY(21px);
    opacity: 0;
  }
}
@keyframes ci-eye {
  0%,
  42%,
  50%,
  100% {
    transform: scaleY(1);
  }
  46% {
    transform: scaleY(0.1);
  }
}
@keyframes ci-smile {
  0% {
    stroke-dashoffset: 14;
  }
  40%,
  75% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: 14;
  }
}
@keyframes ci-blk {
  0%,
  100% {
    fill-opacity: 0.05;
    transform: scale(0.95);
  }
  50% {
    fill-opacity: 0.38;
    transform: scale(1.03);
  }
}
@keyframes ci-link {
  0% {
    stroke-dashoffset: 28;
  }
  45%,
  70% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: -28;
  }
}
@keyframes ci-play {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.22);
  }
}
@keyframes ci-bar {
  0%,
  100% {
    transform: scaleY(0.28);
  }
  50% {
    transform: scaleY(1);
  }
}
@keyframes ci-ring {
  0% {
    transform: scale(0.35);
    opacity: 1;
  }
  100% {
    transform: scale(1.7);
    opacity: 0;
  }
}
@keyframes ci-bolt {
  0%,
  100% {
    transform: scale(1);
  }
  45% {
    transform: scale(1.15);
  }
}
@keyframes ci-dots {
  0%,
  100% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(5px);
  }
}
@keyframes ci-dotc {
  0%,
  100% {
    opacity: 0.25;
    transform: scale(0.7);
  }
  50% {
    opacity: 1;
    transform: scale(1.25);
  }
}

@media (prefers-reduced-motion: reduce) {
  .ci *,
  .ci {
    animation: none !important;
  }
}
</style>
