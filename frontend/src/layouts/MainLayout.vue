<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { RouterView } from 'vue-router'
import Header from './Header.vue'
import Footer from './Footer.vue'

const authStore = useAuthStore()
</script>

<template>
  <div class="min-h-screen flex flex-col bg-[#f5f5f7] text-[#1d1d1f]">
    <!-- 页面级氛围背景 -->
    <div class="pointer-events-none fixed inset-0 z-0" style="background: var(--gradient-mesh)"></div>
    <div class="relative z-10 flex min-h-screen flex-col">
      <Header />
      <main class="flex-1">
        <RouterView />
      </main>
      <Footer />
    </div>
  </div>
</template>