<script setup lang="ts">
import BrandLogo from './BrandLogo.vue'
</script>

<template>
  <footer class="relative overflow-hidden bg-white">
    <!-- 顶部柔和渐变光带 -->
    <div class="h-[3px] w-full anim-gradient bg-gradient-to-r from-[#9bd8ff] via-[#c9b8ff] via-[#ffc9e2] to-[#ffe3b8]"></div>
    <!-- 清新风氛围光斑 -->
    <div class="pointer-events-none absolute -top-20 left-[12%] h-40 w-80 rounded-full bg-[#c5e8ff]/50 blur-3xl"></div>
    <div class="pointer-events-none absolute -bottom-20 right-[12%] h-40 w-80 rounded-full bg-[#e6dcff]/50 blur-3xl"></div>
    <div class="pointer-events-none absolute top-1/2 left-1/2 h-32 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[#ffe0ee]/40 blur-3xl"></div>

    <div class="relative mx-auto min-h-[130px] max-w-[1200px] flex flex-col items-center justify-between gap-[24px] px-[16px] py-[32px] md:flex-row">
      <BrandLogo />

      <div class="text-center text-[13px] leading-[28px] text-[#86868b] md:text-right">
        <p>技术支持：云南大学信息技术中心</p>
        <p>
          <a
            href="https://beian.miit.gov.cn/"
            target="_blank"
            rel="noreferrer"
            class="text-[#86868b] transition-colors duration-300 hover:text-[#0071e3]"
          >
            滇公网安备 53011202000850号
          </a>
        </p>
        <p>Copyright © 2004-2026 云南大学 Yunnan University</p>
      </div>
    </div>
  </footer>
</template>
