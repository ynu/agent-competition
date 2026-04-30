<template>
  <footer class="bg-[#383838] text-white">
    <div class="mx-auto min-h-[120px] max-w-[1200px] flex flex-col items-center justify-between gap-[24px] px-[16px] py-[28px] md:flex-row">
      <div class="flex items-center">
        <img :src="logoFoot" alt="云南大学" class="h-[58px] w-auto" />
      </div>

      <div class="text-center text-[14px] leading-[28px] md:text-right">
        <p>技术支持：云南大学信息技术中心</p>
        <p>
          <a href="https://beian.miit.gov.cn/" target="_blank" rel="noreferrer" class="hover:text-[#8bbcff]">
            滇公网安备 53011202000850号
          </a>
        </p>
        <p>Copyright © 2004-2026 云南大学 Yunnan University</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import logoFoot from '@/assets/images/logo_foot.png';
</script>
