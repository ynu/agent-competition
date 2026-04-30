<template>
  <div class="min-h-screen flex flex-col bg-white text-[#1f1f1f]">
    <Header />
    <main class="flex-1">
      <RouterView />
    </main>
    <Footer />
  </div>
</template>

<script setup>
import Header from './Header.vue';
import Footer from './Footer.vue';
</script>
