<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { RouterView } from 'vue-router'
import Header from './Header.vue'
import Footer from './Footer.vue'

const authStore = useAuthStore()
</script>

<template>
  <div class="min-h-screen flex flex-col bg-white text-[#1f1f1f]">
    <Header />
    <main class="flex-1">
      <RouterView />
    </main>
    <Footer />
  </div>
</template>