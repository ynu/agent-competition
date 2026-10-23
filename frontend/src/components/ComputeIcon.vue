<script setup lang="ts">
// 算力服务/首页 动态 SVG 图标(扁平贴纸风)
// 48x48 视口,大色块实色填充,图形撑满视口,大幅主运动 + 多组次级动画
const props = withDefaults(
  defineProps<{
    name: string
    size?: number
  }>(),
  { size: 26 }
)

// [主色, 深色, 点缀色] 纯实色,无渐变
const palettes: Record<string, string[]> = {
  rtx4090: ['#ff7a1a', '#d94f04', '#ffd60a'],
  l20: ['#12b8ff', '#0284c7', '#7cffb2'],
  ppu810e: ['#8b5cf6', '#6d28d9', '#22d3ee'],
  more: ['#f43f5e', '#be123c', '#fbbf24'],
  teaching: ['#2563eb', '#1e40af', '#fbbf24'],
  research: ['#10b981', '#047857', '#f472b6'],
  competition: ['#f59e0b', '#b45309', '#ef4444'],
  deploy: ['#6366f1', '#4338ca', '#fb7185'],
  chat: ['#06b6d4', '#0891b2', '#a3e635'],
  apply: ['#8b5cf6', '#6d28d9', '#f59e0b'],
  review: ['#22c55e', '#15803d', '#3b82f6'],
  agent: ['#3b82f6', '#1d4ed8', '#f472b6'],
  build: ['#f97316', '#c2410c', '#22d3ee'],
  experience: ['#ec4899', '#be185d', '#fbbf24'],
  plaza: ['#14b8a6', '#0f766e', '#fbbf24'],
  speed: ['#fbbf24', '#d97706', '#60a5fa'],
  security: ['#10b981', '#047857', '#60a5fa'],
  models: ['#6366f1', '#4338ca', '#22d3ee'],
  multimodal: ['#f43f5e', '#be123c', '#22d3ee']
}

const colors = palettes[props.name] ?? ['#3b82f6', '#1d4ed8', '#fbbf24']
const c1 = colors[0] // 主色
const c2 = colors[1] // 深色
const c3 = colors[2] // 点缀色
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
    <!-- RTX 4090:胖芯片整体摇摆,内核闪爆,扫描条狂奔 -->
    <g v-if="name === 'rtx4090'" class="wob">
      <g :stroke="c2" stroke-width="4" stroke-linecap="round">
        <path d="M17 7v4M24 7v4M31 7v4M17 37v4M24 37v4M31 37v4M7 17h4M7 24h4M7 31h4M37 17h4M37 24h4M37 31h4" />
      </g>
      <rect x="9" y="9" width="30" height="30" rx="8" :fill="c1" />
      <rect x="9" y="9" width="30" height="12" rx="8" fill="#fff" opacity=".18" />
      <rect class="pump" x="17" y="17" width="14" height="14" rx="4" :fill="c3" />
      <rect x="18.6" y="19" width="3.2" height="10" rx="1.6" fill="#fff">
        <animateTransform attributeName="transform" type="translate" values="0 0;7.5 0;0 0" dur="0.9s" repeatCount="indefinite" />
      </rect>
      <circle class="blik" cx="14.5" cy="14.5" r="1.8" fill="#fff" />
      <circle class="blik d2" cx="33.5" cy="33.5" r="1.8" fill="#fff" />
    </g>

    <!-- L20:整卡弹跳,双进度条快速充能,LED 爆闪 -->
    <g v-else-if="name === 'l20'" class="bob">
      <path d="M14 35v6M24 35v6M34 35v6" :stroke="c2" stroke-width="4" stroke-linecap="round" />
      <rect x="4" y="13" width="40" height="23" rx="6" :fill="c1" />
      <rect x="4" y="13" width="40" height="9" rx="6" fill="#fff" opacity=".18" />
      <rect x="9" y="20" width="24" height="3.4" rx="1.7" fill="#fff" opacity=".3" />
      <rect class="load" x="9" y="20" width="12" height="3.4" rx="1.7" :fill="c3" />
      <rect x="9" y="27" width="24" height="3.4" rx="1.7" fill="#fff" opacity=".3" />
      <rect class="load ld2" x="9" y="27" width="8" height="3.4" rx="1.7" :fill="c3" />
      <circle class="blik" cx="39" cy="30" r="2.4" :fill="c3" />
    </g>

    <!-- PPU-810E:核心心跳,双卫星绕飞,虚线环旋转 -->
    <g v-else-if="name === 'ppu810e'">
      <circle class="spin" cx="24" cy="24" r="19" fill="none" :stroke="c2" stroke-width="2" stroke-dasharray="7 8" opacity=".55" />
      <ellipse class="spin-rev" cx="24" cy="24" rx="20" ry="9" fill="none" :stroke="c3" stroke-width="1.8" opacity=".5" />
      <g class="spin">
        <circle cx="24" cy="5" r="3.6" :fill="c3" />
      </g>
      <g class="spin-rev">
        <circle cx="44" cy="24" r="2.6" :fill="c2" />
      </g>
      <circle class="pump" cx="24" cy="24" r="10" :fill="c1" />
      <rect x="20.4" y="20.4" width="7.2" height="7.2" rx="2.4" fill="#fff" />
    </g>

    <!-- 更多算力卡:大星魔性旋转缩放,小星抽风闪 -->
    <g v-else-if="name === 'more'">
      <circle class="spin" cx="24" cy="24" r="20" fill="none" :stroke="c2" stroke-width="1.8" stroke-dasharray="4 8" opacity=".5" />
      <path
        class="star"
        d="M24 4C26 18.5 29.5 22 44 24 29.5 26 26 29.5 24 44 22 29.5 18.5 26 4 24 18.5 22 22 18.5 24 4Z"
        :fill="c1"
      />
      <path class="tw" d="M40 4v9M35.5 8.5h9" :stroke="c3" stroke-width="3" stroke-linecap="round" />
      <path class="tw d2" d="M8 34v7M4.5 37.5h7" :stroke="c2" stroke-width="2.6" stroke-linecap="round" />
    </g>

    <!-- 教学实验:帽子弹跳,流苏大摆,彩屑喷射 -->
    <g v-else-if="name === 'teaching'" class="bob">
      <path d="M13.5 23v9c0 3.4 4.7 6 10.5 6s10.5-2.6 10.5-6v-9" :fill="c2" />
      <path d="M23 8.5 45 17 23 25.5 1 17Z" :fill="c1" />
      <path d="M23 8.5 45 17 23 25.5 1 17Z" fill="#fff" opacity=".14" />
      <g class="tassel">
        <path d="M41.5 17.5v9" :stroke="c3" stroke-width="2.6" stroke-linecap="round" />
        <circle class="pump" cx="41.5" cy="30" r="3" :fill="c3" />
      </g>
      <circle class="rise" cx="9" cy="38" r="2" :fill="c3" />
      <circle class="rise d2" cx="16" cy="42" r="1.6" fill="#fff" />
      <circle class="rise d3" cx="38" cy="40" r="1.8" :fill="c3" />
    </g>

    <!-- 科研训练:整瓶摇晃,液体翻涌,气泡连蹦 -->
    <g v-else-if="name === 'research'" class="wob">
      <path d="M19 4h10" :stroke="c2" stroke-width="3.6" stroke-linecap="round" />
      <path d="M21 4.5v11L9.5 36.5A4 4 0 0 0 13.1 42h21.8a4 4 0 0 0 3.6-5.5L27 15.5v-11Z" :fill="c1" opacity=".25" />
      <path class="liq" d="M14.4 29.5h19.2l4.2 7.4a2.2 2.2 0 0 1-2 3.1H12.2a2.2 2.2 0 0 1-2-3.1l4.2-7.4Z" :fill="c1" />
      <path class="wave" d="M12.5 30c2.4-2.2 4.6-2.2 7 0s4.6 2.2 7 0 4.6-2.2 7 0" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".8" />
      <circle class="bub" cx="19" cy="26" r="2" fill="#fff" />
      <circle class="bub d2" cx="26" cy="24.5" r="1.6" :fill="c3" />
      <circle class="bub d3" cx="22.5" cy="22" r="1.3" :fill="c3" />
      <path class="tw" d="M38.5 6v6M35.5 9h6" :stroke="c3" stroke-width="2.6" stroke-linecap="round" />
    </g>

    <!-- 竞赛支撑:奖杯狂欢摇摆,杯身高光扫,彩屑飞 -->
    <g v-else-if="name === 'competition'" class="rock">
      <path d="M16 6h16v9.5a8 8 0 0 1-16 0Z" :fill="c1" />
      <path d="M16 8.5h-4a4.5 4.5 0 0 0-4.5 4.5c0 4 3.4 7 7.9 7.3" fill="none" :stroke="c2" stroke-width="3.4" stroke-linecap="round" />
      <path d="M32 8.5h4a4.5 4.5 0 0 1 4.5 4.5c0 4-3.4 7-7.9 7.3" fill="none" :stroke="c2" stroke-width="3.4" stroke-linecap="round" />
      <path d="M24 23.5v6M17.5 33h13M14 38h20" :stroke="c2" stroke-width="4" stroke-linecap="round" />
      <rect class="shine" x="17.5" y="6.5" width="4" height="16" rx="2" fill="#fff" opacity=".55" />
      <path class="tw" d="M40.5 3.5v7M37 7h7" :stroke="c3" stroke-width="2.8" stroke-linecap="round" />
      <circle class="rise" cx="8" cy="26" r="2" :fill="c3" />
      <circle class="rise d2" cx="40" cy="28" r="1.8" :fill="c1" />
      <circle class="rise d3" cx="35" cy="20" r="1.5" :fill="c3" />
    </g>

    <!-- 应用部署:火箭猛烈抖动,双层尾焰狂喷,气浪线 -->
    <g v-else-if="name === 'deploy'" class="shake">
      <path d="M16.5 21 9 31h7.5M31.5 21 39 31h-7.5" fill="none" :stroke="c2" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
      <path d="M24 3c5.5 5.2 8 11.7 8 18.5V28H16v-6.5C16 14.7 18.5 8.2 24 3Z" :fill="c1" />
      <circle cx="24" cy="17" r="3.8" fill="#fff" />
      <circle cx="24" cy="17" r="3.8" fill="none" :stroke="c2" stroke-width="2" />
      <path class="flame" d="M20.4 30c0 5.6 3.6 10.5 3.6 10.5s3.6-4.9 3.6-10.5c0-1.9-1.6-3.2-3.6-3.2s-3.6 1.3-3.6 3.2Z" :fill="c3" />
      <path class="flame fl2" d="M22.2 30c0 3.4 1.8 6.5 1.8 6.5s1.8-3.1 1.8-6.5c0-1.2-.8-2-1.8-2s-1.8.8-1.8 2Z" fill="#fff" />
      <path class="gust" d="M3 15h6M2 22h7" :stroke="c2" stroke-width="3" stroke-linecap="round" />
      <path class="gust g2" d="M45 12h-4M46 19h-5" :stroke="c3" stroke-width="2.6" stroke-linecap="round" />
    </g>

    <!-- 沟通咨询:气泡翻滚,三点弹跳打字,小气泡探头的 -->
    <g v-else-if="name === 'chat'" class="rock">
      <path d="M13 6.5h22a7 7 0 0 1 7 7v9a7 7 0 0 1-7 7H23.5L14.5 38v-8.5H13a7 7 0 0 1-7-7v-9a7 7 0 0 1 7-7Z" :fill="c1" />
      <circle class="dot-b" cx="17" cy="18" r="3" fill="#fff" />
      <circle class="dot-b d2" cx="24" cy="18" r="3" fill="#fff" />
      <circle class="dot-b d3" cx="31" cy="18" r="3" fill="#fff" />
      <g class="peek">
        <circle cx="41" cy="36" r="5.5" :fill="c3" />
        <circle cx="38.8" cy="36" r="1.1" fill="#0f172a" opacity=".75" />
        <circle cx="41" cy="36" r="1.1" fill="#0f172a" opacity=".75" />
        <circle cx="43.2" cy="36" r="1.1" fill="#0f172a" opacity=".75" />
      </g>
    </g>

    <!-- 提交申请:纸张弹跳,笔尖来回疾书,折角闪光 -->
    <g v-else-if="name === 'apply'" class="bob">
      <path d="M12 4h14l10 10v24a4 4 0 0 1-4 4H12a4 4 0 0 1-4-4V8a4 4 0 0 1 4-4Z" fill="#fff" />
      <path d="M12 4h14l10 10v24a4 4 0 0 1-4 4H12a4 4 0 0 1-4-4V8a4 4 0 0 1 4-4Z" fill="none" :stroke="c1" stroke-width="3" />
      <path d="M26 4v10h10" fill="none" :stroke="c1" stroke-width="3" stroke-linejoin="round" />
      <path d="M14 20h10" :stroke="c2" stroke-width="3.4" stroke-linecap="round" />
      <path class="writeline" d="M14 27h13" :stroke="c3" stroke-width="3.4" stroke-linecap="round" />
      <g class="pen">
        <path d="M26.5 27 36 17.5l4 4-9.5 9.5-5.2 1.2 1.2-5.2Z" :fill="c1" />
        <path d="M35 16.5l5 5" :stroke="c2" stroke-width="2.4" stroke-linecap="round" />
      </g>
      <path class="tw" d="M41 8v6M38 11h6" :stroke="c3" stroke-width="2.6" stroke-linecap="round" />
    </g>

    <!-- 审核评估:对勾重锤盖章,双环反向飞转 -->
    <g v-else-if="name === 'review'">
      <circle class="spin" cx="24" cy="24" r="21" fill="none" :stroke="c2" stroke-width="2.4" stroke-dasharray="5 7" opacity=".6" />
      <circle class="spin-rev" cx="24" cy="24" r="16" fill="none" :stroke="c3" stroke-width="2.4" stroke-dasharray="12 7" opacity=".8" />
      <circle class="pump" cx="24" cy="24" r="12" :fill="c1" />
      <path class="stamp" d="M17.5 24.5l4.8 4.8L31 18.5" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
    </g>

    <!-- 什么是智能体:机器人活泼歪头,眨眼,嘴巴说话,天线电波 -->
    <g v-else-if="name === 'agent'" class="tilt">
      <path d="M24 6v5" :stroke="c2" stroke-width="3" stroke-linecap="round" />
      <circle class="pump" cx="24" cy="5" r="3" :fill="c3" />
      <path d="M6 20.5H2M42 20.5h4" :stroke="c2" stroke-width="3.4" stroke-linecap="round" />
      <rect x="7" y="11" width="34" height="27" rx="9" :fill="c1" />
      <rect x="7" y="11" width="34" height="11" rx="9" fill="#fff" opacity=".16" />
      <g class="blink-eye">
        <circle cx="17.5" cy="22" r="3.4" fill="#fff" />
        <circle cx="18.5" cy="22.8" r="1.6" fill="#0f172a" opacity=".8" />
      </g>
      <g class="blink-eye d2">
        <circle cx="30.5" cy="22" r="3.4" fill="#fff" />
        <circle cx="31.5" cy="22.8" r="1.6" fill="#0f172a" opacity=".8" />
      </g>
      <rect class="talk" x="19" y="29.5" width="10" height="3" rx="1.5" fill="#fff" />
      <circle class="blik" cx="11.5" cy="29" r="1.5" :fill="c3" />
      <circle class="blik d3" cx="36.5" cy="29" r="1.5" :fill="c3" />
    </g>

    <!-- 快速搭建:顶块反复砸落合体,连线抽动,底块呼吸 -->
    <g v-else-if="name === 'build'">
      <rect class="blk" x="4" y="27" width="17" height="17" rx="4.5" :fill="c1" />
      <rect class="blk d2" x="27" y="27" width="17" height="17" rx="4.5" :fill="c2" />
      <rect class="drop" x="15.5" y="4" width="17" height="17" rx="4.5" :fill="c3" />
      <path class="dash" d="M12.5 27v-6a3 3 0 0 1 3-3h.5M24 21.5V27M31.5 27v-6a3 3 0 0 0-3-3H28" fill="none" :stroke="c1" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="5 5" />
      <circle class="blik" cx="12.5" cy="35.5" r="2" fill="#fff" />
      <circle class="blik d2" cx="35.5" cy="35.5" r="2" fill="#fff" />
    </g>

    <!-- 体验智能体:气泡鼓动,播放键心跳,音条狂舞 -->
    <g v-else-if="name === 'experience'" class="bob">
      <path d="M9 6h30a5 5 0 0 1 5 5v15a5 5 0 0 1-5 5H20l-9 8.5V31H9a5 5 0 0 1-5-5V11a5 5 0 0 1 5-5Z" :fill="c1" />
      <path class="play" d="M14.5 13.5v11l9.5-5.5-9.5-5.5Z" fill="#fff" />
      <rect class="bar" x="29.5" y="16" width="3.2" height="6.5" rx="1.6" :fill="c3" />
      <rect class="bar b2" x="35.5" y="13" width="3.2" height="12.5" rx="1.6" fill="#fff" />
    </g>

    <!-- 智能体广场:中心脉冲雷达,四节点轮流点亮,连线流动 -->
    <g v-else-if="name === 'plaza'">
      <path class="dash" d="M15 10h18M10 15v18M38 15v18M15 38h18" fill="none" :stroke="c2" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="5 5" opacity=".7" />
      <circle class="node" cx="9.5" cy="9.5" r="5.5" :fill="c1" />
      <circle class="node d2" cx="38.5" cy="9.5" r="5.5" :fill="c2" />
      <circle class="node d3" cx="9.5" cy="38.5" r="5.5" :fill="c2" />
      <circle class="node d2" cx="38.5" cy="38.5" r="5.5" :fill="c1" />
      <circle class="ring" cx="24" cy="24" r="7" fill="none" :stroke="c3" stroke-width="2" />
      <circle class="ring r2" cx="24" cy="24" r="7" fill="none" :stroke="c3" stroke-width="2" />
      <circle class="pump" cx="24" cy="24" r="4.5" :fill="c3" />
    </g>

    <!-- 极速响应:闪电高频震动,残影拖尾,光圈爆发 -->
    <g v-else-if="name === 'speed'">
      <circle class="burst" cx="24" cy="24" r="20" fill="none" :stroke="c3" stroke-width="2.4" opacity=".6" />
      <path class="ghost" d="M27 6 14 26h7.5L20 42 34 22h-8l1-16Z" :fill="c3" opacity=".45" />
      <path class="jolt" d="M27 4 13.5 25h8L20 44 34.5 23h-8.5L27 4Z" :fill="c1" />
      <path class="gust" d="M2 18h7M1 26h8" :stroke="c3" stroke-width="3.4" stroke-linecap="round" />
    </g>

    <!-- 安全合规:盾牌稳固摇晃,对勾盖章,星光守卫 -->
    <g v-else-if="name === 'security'" class="rock">
      <path d="M24 3 42 9.5v13.5C42 34 34.5 40.8 24 44.5 13.5 40.8 6 34 6 23V9.5L24 3Z" :fill="c1" />
      <path d="M24 8.5 37 13.2v9.8c0 7.8-5.3 13-13 15.8-7.7-2.8-13-8-13-15.8v-9.8L24 8.5Z" fill="#fff" opacity=".14" />
      <path class="stamp" d="M16.5 23.5l5.5 5.5 10.5-11.5" fill="none" stroke="#fff" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round" />
      <path class="tw" d="M41 29.5v6M38 32.5h6" :stroke="c3" stroke-width="2.8" stroke-linecap="round" />
    </g>

    <!-- 多模型接入:三卡洗牌轮转,文字行快扫,指示点追跑 -->
    <g v-else-if="name === 'models'">
      <rect class="card-b" x="14" y="6" width="30" height="22" rx="5" :fill="c2" opacity=".55" />
      <rect x="4" y="10" width="30" height="22" rx="5" :fill="c1" />
      <path class="scanline" d="M9 17h20" :stroke="c3" stroke-width="3.4" stroke-linecap="round" />
      <path d="M9 24h12" stroke="#fff" stroke-width="3.4" stroke-linecap="round" opacity=".55" />
      <circle class="chase" cx="12" cy="40" r="2.6" :fill="c1" />
      <circle class="chase d2" cx="20" cy="40" r="2.6" :fill="c3" />
      <circle class="chase d3" cx="28" cy="40" r="2.6" :fill="c2" />
    </g>

    <!-- 多模态生成:调色盘摇摆,三彩点炸闪,声波荡漾 -->
    <g v-else-if="name === 'multimodal'" class="rock">
      <path d="M24 4c11 0 20 7.9 20 18 0 5.6-4.6 8.5-9.6 8.5h-4c-3.2 0-5.1 2.2-5.1 4.8 0 1.3.6 2.4 1.3 3.5.7 1 1.4 2 1.4 3.3 0 2.3-1.8 3.9-3.9 3.9C13 46 4 37.2 4 25.5S13 4 24 4Z" :fill="c1" />
      <circle class="pump" cx="15" cy="18" r="3.4" :fill="c3" />
      <circle class="pump d2" cx="24" cy="13" r="3.4" fill="#fff" />
      <circle class="pump d3" cx="33" cy="18" r="3.4" :fill="c2" />
      <path class="wave" d="M12 28.5c2-1.8 4-1.8 6 0s4 1.8 6 0" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" opacity=".75" />
    </g>
  </svg>
</template>

<style scoped>
.ci {
  display: block;
}

.ci [class],
.ci g {
  transform-box: fill-box;
  transform-origin: center;
}

/* ============ 复用动作 ============ */
.wob {
  animation: ci-wob 1.6s ease-in-out infinite;
}
.rock {
  animation: ci-rock 1.8s ease-in-out infinite;
}
.tilt {
  animation: ci-tilt 2s ease-in-out infinite;
}
.bob {
  animation: ci-bob 1.4s ease-in-out infinite;
}
.shake {
  animation: ci-shake 0.5s linear infinite;
}
.jolt {
  animation: ci-jolt 0.6s ease-in-out infinite;
}
.spin {
  animation: ci-spin 4s linear infinite;
}
.spin-rev {
  animation: ci-spin-rev 6s linear infinite;
}
.pump {
  animation: ci-pump 1.1s ease-in-out infinite;
}
.blik {
  animation: ci-blik 1.1s ease-in-out infinite;
}
.tw {
  animation: ci-tw 1.1s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.d2 {
  animation-delay: 0.25s;
}
.d3 {
  animation-delay: 0.5s;
}
.load {
  animation: ci-load 1.1s ease-in-out infinite;
}
.ld2 {
  animation-delay: 0.35s;
}
.star {
  animation: ci-star 2.4s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.tassel {
  transform-origin: 50% 0%;
  animation: ci-tassel 1.4s cubic-bezier(0.45, 0, 0.55, 1) infinite;
}
.rise {
  animation: ci-rise 1.2s ease-out infinite;
}
.liq {
  animation: ci-liq 1.6s ease-in-out infinite;
}
.wave {
  animation: ci-wave 1.3s ease-in-out infinite alternate;
}
.bub {
  animation: ci-bub 1.1s ease-out infinite;
}
.shine {
  animation: ci-shine 1.5s ease-in-out infinite;
}
.flame {
  transform-origin: 50% 0%;
  animation: ci-flame 0.35s ease-in-out infinite alternate;
}
.fl2 {
  animation-duration: 0.28s;
}
.gust {
  animation: ci-gust 0.8s ease-out infinite;
}
.g2 {
  animation-delay: 0.4s;
}
.dot-b {
  animation: ci-dotb 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.peek {
  animation: ci-peek 1.8s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.writeline {
  stroke-dasharray: 13;
  animation: ci-write 1.2s ease-in-out infinite;
}
.pen {
  transform-origin: 0% 100%;
  animation: ci-pen 1.2s ease-in-out infinite;
}
.stamp {
  animation: ci-stamp 1.4s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.blink-eye {
  animation: ci-eye 1.7s ease-in-out infinite;
}
.talk {
  animation: ci-talk 0.55s ease-in-out infinite alternate;
}
.blk {
  animation: ci-blk 1.3s ease-in-out infinite;
}
.drop {
  animation: ci-drop 1.3s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.dash {
  animation: ci-flow 1s linear infinite;
}
.play {
  animation: ci-play 0.9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}
.bar {
  animation: ci-bar 0.5s ease-in-out infinite;
}
.b2 {
  animation-delay: 0.15s;
}
.node {
  animation: ci-node 1.4s ease-in-out infinite;
}
.ring {
  animation: ci-ring 1.4s ease-out infinite;
}
.r2 {
  animation-delay: 0.7s;
}
.burst {
  transform-origin: center;
  animation: ci-burst 1.3s ease-out infinite;
}
.ghost {
  animation: ci-ghost 0.6s ease-in-out infinite;
}
.chase {
  animation: ci-chase 1.2s ease-in-out infinite;
}
.scanline {
  stroke-dasharray: 20 20;
  animation: ci-scan 1.4s linear infinite;
}

/* ============ 关键帧 ============ */
@keyframes ci-wob {
  0%, 100% { transform: rotate(-4deg) scale(1); }
  50% { transform: rotate(4deg) scale(1.03); }
}
@keyframes ci-rock {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(5deg); }
}
@keyframes ci-tilt {
  0%, 100% { transform: rotate(-6deg); }
  50% { transform: rotate(6deg); }
}
@keyframes ci-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3.5px); }
}
@keyframes ci-shake {
  0% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(-1px, -1.5px) rotate(-2deg); }
  50% { transform: translate(1px, 0.5px) rotate(1.5deg); }
  75% { transform: translate(-0.5px, 1px) rotate(-1deg); }
  100% { transform: translate(0, 0) rotate(0deg); }
}
@keyframes ci-jolt {
  0%, 100% { transform: translateX(0) scale(1); }
  30% { transform: translateX(-2.5px) scale(1.05); }
  60% { transform: translateX(2px) scale(0.97); }
}
@keyframes ci-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes ci-spin-rev {
  from { transform: rotate(0deg); }
  to { transform: rotate(-360deg); }
}
@keyframes ci-pump {
  0%, 100% { transform: scale(0.86); opacity: 0.75; }
  50% { transform: scale(1.1); opacity: 1; }
}
@keyframes ci-blik {
  0%, 100% { opacity: 0.15; transform: scale(0.6); }
  45% { opacity: 1; transform: scale(1.15); }
}
@keyframes ci-tw {
  0%, 100% { opacity: 0.1; transform: scale(0.4) rotate(-30deg); }
  50% { opacity: 1; transform: scale(1.1) rotate(0deg); }
}
@keyframes ci-load {
  0% { transform: translateX(-6px); opacity: 0; }
  25% { opacity: 1; }
  100% { transform: translateX(14px); opacity: 0; }
}
@keyframes ci-star {
  0%, 100% { transform: scale(0.75) rotate(-25deg); }
  50% { transform: scale(1.15) rotate(25deg); }
}
@keyframes ci-tassel {
  0%, 100% { transform: rotate(-18deg); }
  50% { transform: rotate(18deg); }
}
@keyframes ci-rise {
  0% { transform: translateY(4px) scale(0.7); opacity: 0; }
  30% { opacity: 1; }
  100% { transform: translateY(-10px) scale(1.1); opacity: 0; }
}
@keyframes ci-liq {
  0%, 100% { opacity: 0.75; transform: scaleY(0.96); }
  50% { opacity: 1; transform: scaleY(1.03); }
}
@keyframes ci-wave {
  from { transform: translateX(-3px); }
  to { transform: translateX(3px); }
}
@keyframes ci-bub {
  0% { transform: translateY(4px) scale(0.6); opacity: 0; }
  30% { opacity: 1; }
  100% { transform: translateY(-10px) scale(1.2); opacity: 0; }
}
@keyframes ci-shine {
  0% { transform: translateX(-6px); opacity: 0; }
  30% { opacity: 0.8; }
  60%, 100% { transform: translateX(16px); opacity: 0; }
}
@keyframes ci-flame {
  from { transform: scale(0.6, 0.55); opacity: 0.6; }
  to { transform: scale(1.15, 1.3); opacity: 1; }
}
@keyframes ci-gust {
  0% { transform: translateX(8px); opacity: 0; }
  30% { opacity: 1; }
  100% { transform: translateX(-10px); opacity: 0; }
}
@keyframes ci-dotb {
  0%, 100% { transform: translateY(2.5px); opacity: 0.4; }
  40% { transform: translateY(-5px); opacity: 1; }
}
@keyframes ci-peek {
  0%, 45%, 100% { transform: translateY(9px) scale(0.4); opacity: 0; }
  58% { transform: translateY(0) scale(1.15); opacity: 1; }
  70% { transform: translateY(0) scale(1); opacity: 1; }
  92% { transform: translateY(0) scale(1); opacity: 0.9; }
}
@keyframes ci-write {
  0% { stroke-dashoffset: 13; }
  45%, 70% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: 13; }
}
@keyframes ci-pen {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  30% { transform: translate(-2.5px, 1px) rotate(-9deg); }
  60% { transform: translate(1.5px, -0.5px) rotate(6deg); }
}
@keyframes ci-stamp {
  0% { transform: scale(1.6); opacity: 0; }
  35% { transform: scale(1); opacity: 1; }
  80% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1); opacity: 0.15; }
}
@keyframes ci-eye {
  0%, 40%, 48%, 100% { transform: scaleY(1); }
  44% { transform: scaleY(0.08); }
}
@keyframes ci-talk {
  from { transform: scaleX(0.55); }
  to { transform: scaleX(1.1); }
}
@keyframes ci-blk {
  0%, 100% { transform: scale(0.94); filter: brightness(0.92); }
  50% { transform: scale(1.02); filter: brightness(1.1); }
}
@keyframes ci-drop {
  0%, 100% { transform: translateY(-7px); }
  45% { transform: translateY(3.5px) scaleY(0.92); }
  60% { transform: translateY(0) scaleY(1); }
}
@keyframes ci-flow {
  0% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -20; }
}
@keyframes ci-play {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.25); }
}
@keyframes ci-bar {
  0%, 100% { transform: scaleY(0.3); }
  50% { transform: scaleY(1); }
}
@keyframes ci-node {
  0%, 100% { transform: scale(0.82); opacity: 0.55; }
  50% { transform: scale(1.12); opacity: 1; }
}
@keyframes ci-ring {
  0% { transform: scale(0.4); opacity: 1; }
  100% { transform: scale(1.8); opacity: 0; }
}
@keyframes ci-burst {
  0% { transform: scale(0.55); opacity: 0.9; }
  100% { transform: scale(1.25); opacity: 0; }
}
@keyframes ci-ghost {
  0%, 100% { transform: translateX(0); opacity: 0.5; }
  50% { transform: translateX(-4px); opacity: 0.2; }
}
@keyframes ci-chase {
  0%, 100% { transform: scale(0.7); opacity: 0.35; }
  50% { transform: scale(1.25); opacity: 1; }
}
@keyframes ci-scan {
  0% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -40; }
}

@media (prefers-reduced-motion: reduce) {
  .ci *,
  .ci {
    animation: none !important;
  }
}
</style>
