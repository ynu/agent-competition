<script setup lang="ts">
// 算力服务页动态 SVG 图标
// 每个图标为 48x48 线条风格,带渐变描边与持续微动画
const props = withDefaults(
  defineProps<{
    name: string
    size?: number
  }>(),
  { size: 26 }
)

// 渐变配色(与页面各板块 hue 对应)
const palettes: Record<string, [string, string]> = {
  rtx4090: ['#ff9f0a', '#ff5ca8'],
  l20: ['#30d158', '#0090ff'],
  ppu810e: ['#00c6ff', '#30d158'],
  more: ['#6a5cff', '#a18cd1'],
  teaching: ['#0090ff', '#00c6ff'],
  research: ['#6a5cff', '#a18cd1'],
  competition: ['#ff5ca8', '#ff9f45'],
  deploy: ['#ff9f0a', '#ff5ca8'],
  chat: ['#0090ff', '#00c6ff'],
  apply: ['#6a5cff', '#a18cd1'],
  review: ['#30d158', '#00c6ff'],
  // 首页：智能体广场
  agent: ['#0090ff', '#00c6ff'],
  build: ['#6a5cff', '#a18cd1'],
  experience: ['#ff5ca8', '#ff9f45'],
  plaza: ['#ff9f0a', '#ff5ca8'],
  // 首页：大模型服务
  speed: ['#0090ff', '#00c6ff'],
  security: ['#30d158', '#00c6ff'],
  models: ['#6a5cff', '#a18cd1'],
  multimodal: ['#ff9f0a', '#ff5ca8']
}

const colors = palettes[props.name] ?? ['#0090ff', '#00c6ff']
const c1 = colors[0]
const c2 = colors[1]

// 每个实例独立渐变 id,避免同页多实例 id 冲突
const uid = Math.random().toString(36).slice(2, 9)
const gid = `${uid}-grad`
const gref = `url(#${gid})`
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
      <linearGradient :id="gid" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
        <stop offset="0" :stop-color="c1" />
        <stop offset="1" :stop-color="c2" />
      </linearGradient>
    </defs>

    <!-- RTX 4090:芯片 + 往复扫描线 -->
    <g v-if="name === 'rtx4090'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M17 6.5v4M24 6.5v4M31 6.5v4M17 37.5v4M24 37.5v4M31 37.5v4M6.5 20h4M6.5 28h4M37.5 20h4M37.5 28h4" opacity=".7" />
      <rect x="10.5" y="10.5" width="27" height="27" rx="5.5" />
      <rect class="a-die" x="18.5" y="18.5" width="11" height="11" rx="2.5" :fill="gref" stroke="none" />
      <line x1="20" y1="19.5" x2="20" y2="28.5" stroke="#fff" stroke-width="1.6" opacity=".85">
        <animateTransform
          attributeName="transform"
          type="translate"
          values="0 0;8 0;0 0"
          dur="2.4s"
          calcMode="spline"
          keySplines="0.4 0 0.6 1;0.4 0 0.6 1"
          repeatCount="indefinite"
        />
      </line>
    </g>

    <!-- L20:数据中心卡 + 双向数据流 -->
    <g v-else-if="name === 'l20'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <rect x="7" y="14" width="34" height="20" rx="4.5" />
      <path d="M12 21h24M12 27h24" opacity=".35" stroke-width="2" />
      <path d="M18 34v4.5M24 34v4.5M30 34v4.5" opacity=".7" />
      <circle cy="21" r="2.1" :fill="c1" stroke="none">
        <animate attributeName="cx" values="12;36" dur="1.9s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.12;0.85;1" dur="1.9s" repeatCount="indefinite" />
      </circle>
      <circle cy="27" r="2.1" :fill="c2" stroke="none">
        <animate attributeName="cx" values="36;12" dur="1.9s" begin="0.95s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.12;0.85;1" dur="1.9s" begin="0.95s" repeatCount="indefinite" />
      </circle>
    </g>

    <!-- PPU-810E:核心 + 轨道环绕粒子 -->
    <g v-else-if="name === 'ppu810e'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="24" cy="24" r="17" opacity=".3" />
      <g>
        <animateTransform attributeName="transform" type="rotate" from="0 24 24" to="360 24 24" dur="7s" repeatCount="indefinite" />
        <circle cx="24" cy="7" r="2.6" :fill="c1" stroke="none" />
        <circle cx="41" cy="24" r="1.7" :fill="c2" stroke="none" opacity=".8" />
      </g>
      <rect x="17" y="17" width="14" height="14" rx="4" :fill="gref" stroke="none" />
      <rect x="21.2" y="21.2" width="5.6" height="5.6" rx="1.6" fill="#fff" opacity=".92" stroke="none" />
    </g>

    <!-- 更多算力卡:呼吸星芒 + 闪烁 -->
    <g v-else-if="name === 'more'" stroke-linecap="round" stroke-linejoin="round">
      <path
        class="a-star"
        d="M24 8.5C25.5 19.5 28.5 22.5 39.5 24 28.5 25.5 25.5 28.5 24 39.5 22.5 28.5 19.5 25.5 8.5 24 19.5 22.5 22.5 19.5 24 8.5Z"
        :fill="gref"
      />
      <path class="a-tw" d="M38.5 5v7M35 8.5h7" :stroke="c1" stroke-width="2.2" />
      <path class="a-tw a-tw2" d="M9 34.5v5.5M6.2 37.2h5.6" :stroke="c2" stroke-width="2" />
    </g>

    <!-- 教学实验:学士帽 + 摆动流苏 -->
    <g v-else-if="name === 'teaching'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M24 11 43 19 24 27 5 19Z" />
      <path d="M14 23.5V31c0 2.9 4.5 5.2 10 5.2s10-2.3 10-5.2v-7.5" />
      <g>
        <animateTransform
          attributeName="transform"
          type="rotate"
          values="-8 42.5 19;8 42.5 19;-8 42.5 19"
          dur="2.8s"
          calcMode="spline"
          keySplines="0.45 0 0.55 1;0.45 0 0.55 1"
          repeatCount="indefinite"
        />
        <path d="M42.5 19v9.5" stroke-width="2.2" />
        <circle cx="42.5" cy="31.5" r="2.1" :fill="c1" stroke="none" />
      </g>
    </g>

    <!-- 科研训练:锥形瓶 + 沸腾气泡 -->
    <g v-else-if="name === 'research'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M19 6.5h10" />
      <path d="M21 6.5v11.5L10.6 36.6A3.1 3.1 0 0 0 13.4 41h21.2a3.1 3.1 0 0 0 2.8-4.4L27 18V6.5" />
      <path class="a-wave" d="M15.5 31.5c2-1.7 4-1.7 6 0s4 1.7 6 0 4-1.7 6 0" :stroke="c1" stroke-width="2.2" />
      <circle class="a-bub" cx="20" cy="27" r="1.7" :fill="c2" stroke="none" />
      <circle class="a-bub a-bub2" cx="26.5" cy="25.5" r="1.3" :fill="c1" stroke="none" />
    </g>

    <!-- 竞赛支撑:奖杯 + 闪耀 -->
    <g v-else-if="name === 'competition'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M17 8h14v8.5a7 7 0 0 1-14 0Z" />
      <path d="M17 10.5h-3.5a3.5 3.5 0 0 0-3.5 3.5c0 3.4 2.9 6 6.6 6.3" />
      <path d="M31 10.5h3.5a3.5 3.5 0 0 1 3.5 3.5c0 3.4-2.9 6-6.6 6.3" />
      <path d="M24 23.5v6M18 33.5h12M15 37.5h18" />
      <path class="a-tw a-tw3" d="M36.5 5.5v6M33.5 8.5h6" :stroke="c1" stroke-width="2" />
    </g>

    <!-- 应用部署:火箭 + 跳动尾焰 -->
    <g v-else-if="name === 'deploy'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M24 5c4.8 4.6 7 10.3 7 16.4V29H17v-7.6C17 15.3 19.2 9.6 24 5Z" />
      <circle cx="24" cy="18" r="3.1" />
      <path d="M17 24.5 11 32.5h6M31 24.5l6 8h-6" />
      <path class="a-flame" d="M21.2 31.5c0 4.5 2.8 8.5 2.8 8.5s2.8-4 2.8-8.5c0-1.5-1.2-2.5-2.8-2.5s-2.8 1-2.8 2.5Z" :fill="c1" stroke="none" opacity=".9" />
      <path class="a-speed" d="M7 15.5h4.5M5.5 21.5H10" :stroke="c2" stroke-width="2.2" />
    </g>

    <!-- 沟通咨询:对话气泡 + 打字点 -->
    <g v-else-if="name === 'chat'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M13 9h22a6 6 0 0 1 6 6v10a6 6 0 0 1-6 6H23l-8 8v-8h-2a6 6 0 0 1-6-6V15a6 6 0 0 1 6-6Z" />
      <circle class="a-blink" cx="17.5" cy="20" r="2.3" :fill="c1" stroke="none" />
      <circle class="a-blink a-blink2" cx="24" cy="20" r="2.3" :fill="c1" stroke="none" />
      <circle class="a-blink a-blink3" cx="30.5" cy="20" r="2.3" :fill="c1" stroke="none" />
    </g>

    <!-- 提交申请:文档 + 书写中笔迹 -->
    <g v-else-if="name === 'apply'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M13 6.5h13.5L35 15v21.5a4 4 0 0 1-4 4H13a4 4 0 0 1-4-4v-26a4 4 0 0 1 4-4Z" />
      <path d="M26.5 6.5V15H35" opacity=".7" />
      <path d="M15 21h11" />
      <path class="a-write" d="M15 27h13" :stroke="c1" />
      <g class="a-pen">
        <path d="M28.5 27.5 37.5 18.5l3 3-9 9-3-3Z" :fill="gref" stroke="none" opacity=".95" />
      </g>
    </g>

    <!-- 审核评估:旋转刻度环 + 描绘对勾 -->
    <g v-else-if="name === 'review'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="24" cy="24" r="20.5" stroke-dasharray="2.5 5.5" opacity=".5">
        <animateTransform attributeName="transform" type="rotate" from="0 24 24" to="360 24 24" dur="12s" repeatCount="indefinite" />
      </circle>
      <circle cx="24" cy="24" r="16.5" opacity=".9" />
      <path class="a-check" d="M15.5 24.5l6.5 6.5L33 17.5" stroke-width="3" />
    </g>

    <!-- 什么是智能体:机器人头像 + 眨眼扫描 -->
    <g v-else-if="name === 'agent'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M24 5.5v4" />
      <circle cx="24" cy="7" r="1.8" :fill="c1" stroke="none" class="a-ant" />
      <rect x="9" y="12.5" width="30" height="24" rx="7" />
      <circle class="a-eye" cx="17.5" cy="22.5" r="2.6" :fill="c1" stroke="none" />
      <circle class="a-eye a-eye2" cx="30.5" cy="22.5" r="2.6" :fill="c2" stroke="none" />
      <path class="a-smile" d="M18.5 30c3.5 3 7.5 3 11 0" />
      <path d="M9 20.5h-3M38 20.5h3" opacity=".6" />
    </g>

    <!-- 快速搭建:积木块逐块点亮 -->
    <g v-else-if="name === 'build'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <rect class="a-blk" x="5" y="26" width="15" height="15" rx="3" :fill="c1" fill-opacity=".14" />
      <rect class="a-blk a-blk2" x="28" y="26" width="15" height="15" rx="3" :fill="c1" fill-opacity=".14" />
      <rect class="a-blk a-blk3" x="16.5" y="7" width="15" height="15" rx="3" :fill="c1" fill-opacity=".14" />
      <path class="a-link" d="M12.5 26v-4.5a3 3 0 0 1 3-3h1M24 22v4M31.5 26v-4.5a3 3 0 0 0-3-3h-1" opacity=".8" />
    </g>

    <!-- 体验智能体:播放气泡 + 音波脉动 -->
    <g v-else-if="name === 'experience'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M8.5 7.5h31a3.5 3.5 0 0 1 3.5 3.5v17a3.5 3.5 0 0 1-3.5 3.5H20l-8 7.5v-7.5h-3.5A3.5 3.5 0 0 1 5 28V11a3.5 3.5 0 0 1 3.5-3.5Z" />
      <path class="a-play" d="M18.5 13.5v11.5l9.5-5.75-9.5-5.75Z" :fill="gref" stroke="none" />
      <path class="a-bar a-bar1" d="M33 16v8" :stroke="c1" stroke-width="2.6" />
      <path class="a-bar a-bar2" d="M38 14v12" :stroke="c2" stroke-width="2.6" />
    </g>

    <!-- 智能体广场:网格节点 + 流转脉冲 -->
    <g v-else-if="name === 'plaza'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="10" cy="10" r="4.5" />
      <circle cx="38" cy="10" r="4.5" />
      <circle cx="10" cy="38" r="4.5" />
      <circle cx="38" cy="38" r="4.5" />
      <path d="M14.5 10h19M10 14.5v19M38 14.5v19M14.5 38h19" opacity=".55" />
      <circle class="a-pulse" cx="24" cy="24" r="3" :fill="c1" stroke="none" />
      <circle class="a-pulse2" cx="24" cy="24" r="2" :fill="c2" stroke="none" />
    </g>

    <!-- 极速响应:闪电 + 能量环 -->
    <g v-else-if="name === 'speed'" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="24" cy="24" r="19" :stroke="gref" stroke-width="2.4" opacity=".35" />
      <circle cx="24" cy="24" r="19" :stroke="c1" stroke-width="2.4" stroke-linecap="round" fill="none"
        stroke-dasharray="30 89" class="a-orbit" />
      <path class="a-bolt" d="M26.5 10 15 26.5h7.5L21.5 38 33 21.5h-7.5L26.5 10Z" :fill="gref" stroke="none" />
    </g>

    <!-- 安全合规:盾牌 + 描绘对勾 -->
    <g v-else-if="name === 'security'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M24 5.5 40 11v12.5c0 9.8-6.6 15.9-16 19-9.4-3.1-16-9.2-16-19V11L24 5.5Z" />
      <path class="a-check a-check2" d="M16.5 23.5l5.5 5.5 10-11" :stroke="c1" stroke-width="2.8" />
    </g>

    <!-- 多模型接入:层叠面板 + 轮播指示 -->
    <g v-else-if="name === 'models'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <rect x="6" y="9" width="28" height="20" rx="4" />
      <path d="M38 11.5a4 4 0 0 1 4 4V31a4 4 0 0 1-4 4H17" opacity=".45" />
      <path class="a-line" d="M11.5 16h17" />
      <path class="a-line a-line2" d="M11.5 22h11" :stroke="c1" />
      <g class="a-dots">
        <circle cx="14" cy="35.5" r="1.7" :fill="c1" stroke="none" />
        <circle cx="20" cy="35.5" r="1.7" :fill="c1" stroke="none" opacity=".55" />
        <circle cx="26" cy="35.5" r="1.7" :fill="c1" stroke="none" opacity=".3" />
      </g>
    </g>

    <!-- 多模态生成:调色盘 + 旋转色点 -->
    <g v-else-if="name === 'multimodal'" :stroke="gref" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M24 6.5c9.7 0 17.5 7 17.5 16 0 5-4 7.5-8.5 7.5h-3.5c-2.8 0-4.5 2-4.5 4.2 0 1.2.5 2.1 1.2 3.1.6.9 1.3 1.8 1.3 3 0 2-1.6 3.2-3.5 3.2-9.7 0-17.5-8.2-17.5-18.5S14.3 6.5 24 6.5Z" />
      <circle class="a-dot a-dot1" cx="16.5" cy="19" r="2.4" :fill="c1" stroke="none" />
      <circle class="a-dot a-dot2" cx="24" cy="15" r="2.4" :fill="c2" stroke="none" />
      <circle class="a-dot a-dot3" cx="31.5" cy="19" r="2.4" :fill="c1" stroke="none" />
    </g>
  </svg>
</template>

<style scoped>
.ci {
  display: block;
}

/* 统一设置 transform 基准,保证缩放/旋转围绕元素自身中心 */
.a-die,
.a-star,
.a-tw,
.a-blink,
.a-bub,
.a-wave,
.a-flame,
.a-speed,
.a-pen {
  transform-box: fill-box;
  transform-origin: center;
}

.a-die {
  animation: ci-die 2s ease-in-out infinite;
}
.a-star {
  animation: ci-star 3s ease-in-out infinite;
}
.a-tw {
  animation: ci-tw 2.4s ease-in-out infinite;
}
.a-tw2 {
  animation-delay: 1.2s;
}
.a-tw3 {
  animation-delay: 0.6s;
}
.a-blink {
  animation: ci-blink 1.8s ease-in-out infinite;
}
.a-blink2 {
  animation-delay: 0.3s;
}
.a-blink3 {
  animation-delay: 0.6s;
}
.a-bub {
  animation: ci-bub 2.2s ease-in infinite;
}
.a-bub2 {
  animation-delay: 1.1s;
}
.a-wave {
  animation: ci-wave 3s ease-in-out infinite alternate;
}
.a-flame {
  transform-origin: 50% 0%;
  animation: ci-flame 0.9s ease-in-out infinite alternate;
}
.a-speed {
  animation: ci-speed 1.4s ease-in-out infinite;
}
.a-write {
  stroke-dasharray: 13;
  animation: ci-write 2.6s ease-in-out infinite;
}
.a-pen {
  transform-origin: 12% 88%;
  animation: ci-pen 2.6s ease-in-out infinite;
}
.a-check {
  stroke-dasharray: 27;
  animation: ci-check 3s ease-in-out infinite;
}
.a-ant {
  transform-box: fill-box;
  transform-origin: center;
  animation: ci-ant 2s ease-in-out infinite;
}
.a-eye {
  animation: ci-eye 3.2s ease-in-out infinite;
}
.a-eye2 {
  animation-delay: 0.15s;
}
.a-smile {
  stroke-dasharray: 14;
  animation: ci-smile 3.2s ease-in-out infinite;
}
.a-blk {
  animation: ci-blk 2.7s ease-in-out infinite;
}
.a-blk2 {
  animation-delay: 0.3s;
}
.a-blk3 {
  animation-delay: 0.6s;
}
.a-link {
  stroke-dasharray: 30;
  animation: ci-link 2.7s ease-in-out infinite;
}
.a-play {
  transform-box: fill-box;
  transform-origin: center;
  animation: ci-play 2.2s ease-in-out infinite;
}
.a-bar {
  animation: ci-bar 1.1s ease-in-out infinite;
}
.a-bar2 {
  animation-delay: 0.25s;
}
.a-pulse {
  transform-box: fill-box;
  transform-origin: center;
  animation: ci-pulse 2.6s ease-out infinite;
}
.a-pulse2 {
  transform-box: fill-box;
  transform-origin: center;
  animation: ci-pulse2 2.6s ease-out infinite;
}
.a-orbit {
  transform-box: fill-box;
  transform-origin: center;
  animation: ci-orbit 2.2s linear infinite;
}
.a-bolt {
  transform-box: fill-box;
  transform-origin: center;
  animation: ci-bolt 2.2s ease-in-out infinite;
}
.a-check2 {
  stroke-dasharray: 26;
  animation: ci-check2 3.2s ease-in-out infinite;
}
.a-line {
  stroke-dasharray: 17;
  animation: ci-line 3s ease-in-out infinite;
}
.a-line2 {
  animation-delay: 0.4s;
}
.a-dots {
  transform-box: fill-box;
  transform-origin: center;
  animation: ci-dots 2.4s ease-in-out infinite;
}
.a-dot {
  animation: ci-dot 2.6s ease-in-out infinite;
}
.a-dot2 {
  animation-delay: 0.5s;
}
.a-dot3 {
  animation-delay: 1s;
}

@keyframes ci-die {
  0%,
  100% {
    opacity: 0.45;
  }
  50% {
    opacity: 1;
  }
}
@keyframes ci-star {
  0%,
  100% {
    transform: scale(0.92);
  }
  50% {
    transform: scale(1.07);
  }
}
@keyframes ci-tw {
  0%,
  100% {
    opacity: 0.2;
    transform: scale(0.7);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}
@keyframes ci-blink {
  0%,
  100% {
    opacity: 0.25;
  }
  40% {
    opacity: 1;
  }
}
@keyframes ci-bub {
  0% {
    transform: translateY(2px);
    opacity: 0;
  }
  30% {
    opacity: 0.9;
  }
  100% {
    transform: translateY(-5px);
    opacity: 0;
  }
}
@keyframes ci-wave {
  from {
    transform: translateX(-1.6px);
  }
  to {
    transform: translateX(1.6px);
  }
}
@keyframes ci-flame {
  from {
    transform: scale(0.82, 0.8);
  }
  to {
    transform: scale(1.04, 1.08);
  }
}
@keyframes ci-speed {
  0% {
    transform: translateX(3px);
    opacity: 0;
  }
  30% {
    opacity: 0.8;
  }
  100% {
    transform: translateX(-3px);
    opacity: 0;
  }
}
@keyframes ci-write {
  0% {
    stroke-dashoffset: 13;
  }
  45% {
    stroke-dashoffset: 0;
  }
  75% {
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
    transform: rotate(-5deg);
  }
  60% {
    transform: rotate(3deg);
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
  80% {
    stroke-dashoffset: 0;
    opacity: 1;
  }
  100% {
    stroke-dashoffset: 0;
    opacity: 0;
  }
}
@keyframes ci-ant {
  0%,
  100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1.15);
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
    fill-opacity: 0.06;
  }
  50% {
    fill-opacity: 0.3;
  }
}
@keyframes ci-link {
  0% {
    stroke-dashoffset: 30;
  }
  45%,
  70% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: -30;
  }
}
@keyframes ci-play {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.12);
  }
}
@keyframes ci-bar {
  0%,
  100% {
    transform: scaleY(0.45);
  }
  50% {
    transform: scaleY(1);
  }
}
@keyframes ci-pulse {
  0% {
    transform: scale(0.4);
    opacity: 0.9;
  }
  70%,
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}
@keyframes ci-pulse2 {
  0%,
  30% {
    transform: scale(0.4);
    opacity: 0.9;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}
@keyframes ci-orbit {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
@keyframes ci-bolt {
  0%,
  100% {
    transform: scale(1);
    filter: drop-shadow(0 0 0 rgba(0, 144, 255, 0));
  }
  50% {
    transform: scale(1.06);
    filter: drop-shadow(0 0 4px rgba(0, 144, 255, 0.45));
  }
}
@keyframes ci-check2 {
  0% {
    stroke-dashoffset: 26;
  }
  45%,
  80% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: 0;
    opacity: 0;
  }
}
@keyframes ci-line {
  0% {
    stroke-dashoffset: 17;
  }
  50%,
  75% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: -17;
  }
}
@keyframes ci-dots {
  0%,
  100% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(3px);
  }
}
@keyframes ci-dot {
  0%,
  100% {
    opacity: 0.35;
  }
  50% {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .ci *,
  .ci {
    animation: none !important;
  }
}
</style>
