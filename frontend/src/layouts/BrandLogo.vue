<script setup lang="ts">
// Footer 品牌 Logo：动态 SVG —— 云南大学AI门户
</script>

<template>
  <div class="footer-logo flex items-center gap-[14px] select-none">
    <!-- 动态 SVG Logo -->
    <svg
      class="footer-logo-mark"
      width="52"
      height="52"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="云南大学AI门户"
      role="img"
    >
      <defs>
        <!-- 流动渐变（与页面主渐变呼应） -->
        <linearGradient id="footerLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#4d9df0">
            <animate attributeName="stop-color" values="#4d9df0;#8a7cf6;#f386c0;#4d9df0" dur="6s" repeatCount="indefinite" />
          </stop>
          <stop offset="100%" stop-color="#8a7cf6">
            <animate attributeName="stop-color" values="#8a7cf6;#f386c0;#ffd08a;#8a7cf6" dur="6s" repeatCount="indefinite" />
          </stop>
        </linearGradient>
        <!-- 光晕 -->
        <radialGradient id="footerLogoGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#4d9df0" stop-opacity="0.25" />
          <stop offset="100%" stop-color="#4d9df0" stop-opacity="0" />
        </radialGradient>
      </defs>

      <!-- 背景光晕（呼吸） -->
      <circle cx="32" cy="32" r="30" fill="url(#footerLogoGlow)">
        <animate attributeName="opacity" values="0.5;1;0.5" dur="4s" repeatCount="indefinite" />
      </circle>

      <!-- 外环：门/门户意象（旋转虚线圆环） -->
      <circle
        cx="32" cy="32" r="26"
        stroke="url(#footerLogoGrad)"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-dasharray="10 7"
        fill="none"
        opacity="0.85"
      >
        <animateTransform
          attributeName="transform"
          type="rotate"
          from="0 32 32"
          to="360 32 32"
          dur="16s"
          repeatCount="indefinite"
        />
      </circle>

      <!-- 拱门轮廓：云南大学会泽院大门的抽象 -->
      <path
        d="M22 42 V30 a10 10 0 0 1 20 0 V42"
        stroke="url(#footerLogoGrad)"
        stroke-width="3"
        stroke-linecap="round"
        fill="none"
      >
        <animate
          attributeName="stroke-width"
          values="3;3.6;3"
          dur="4s"
          repeatCount="indefinite"
        />
      </path>

      <!-- AI 神经节点：门内三颗星点（连线呼吸） -->
      <g stroke="url(#footerLogoGrad)" stroke-width="1.6" stroke-linecap="round" opacity="0.9">
        <path d="M32 24 V32" />
        <path d="M32 32 L26 38" />
        <path d="M32 32 L38 38" />
      </g>

      <g fill="url(#footerLogoGrad)">
        <!-- 顶点 -->
        <circle cx="32" cy="23" r="2.6">
          <animate attributeName="r" values="2.6;3.4;2.6" dur="2.6s" repeatCount="indefinite" />
        </circle>
        <!-- 中心枢纽 -->
        <circle cx="32" cy="32" r="3">
          <animate attributeName="r" values="3;3.8;3" dur="2.6s" begin="0.4s" repeatCount="indefinite" />
        </circle>
        <!-- 左节点 -->
        <circle cx="25.5" cy="38.5" r="2.2">
          <animate attributeName="r" values="2.2;3;2.2" dur="2.6s" begin="0.8s" repeatCount="indefinite" />
        </circle>
        <!-- 右节点 -->
        <circle cx="38.5" cy="38.5" r="2.2">
          <animate attributeName="r" values="2.2;3;2.2" dur="2.6s" begin="1.2s" repeatCount="indefinite" />
        </circle>
      </g>
    </svg>

    <!-- 文字标识 -->
    <div class="flex flex-col">
      <span class="footer-logo-title text-[19px] font-[700] leading-[26px] tracking-[1px]">
        云南大学AI门户
      </span>
      <span class="text-[11px] font-[500] uppercase leading-[16px] tracking-[3px] text-[#a1a1b5]">
        Yunnan University · AI Portal
      </span>
    </div>
  </div>
</template>

<style scoped>
.footer-logo-mark {
  flex-shrink: 0;
  filter: drop-shadow(0 4px 14px rgba(77, 157, 240, 0.28));
  transition: transform 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}

.footer-logo:hover .footer-logo-mark {
  transform: scale(1.08) rotate(-3deg);
}

.footer-logo-title {
  background: linear-gradient(96deg, #3a7bd5 0%, #6a5cff 55%, #d16ab0 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

@media (prefers-reduced-motion: reduce) {
  .footer-logo-mark * {
    animation: none !important;
  }
}
</style>
