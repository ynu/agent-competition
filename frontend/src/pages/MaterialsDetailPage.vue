<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { materialsApi } from '@/api'
import markdownIt from 'markdown-it'
import { mediaPlugin } from '@/plugins/markdown'

const route = useRoute()
const material = ref<any>(null)
const loading = ref(true)
const error = ref('')

const md = markdownIt({
  html: true,
  linkify: true,
  typographer: true
}).use(mediaPlugin)

const renderedContent = computed(() => {
  if (!material.value?.content) return ''
  return md.render(material.value.content)
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

onMounted(async () => {
  await fetchMaterial()
})

async function fetchMaterial() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const res = await materialsApi.get(id)
    material.value = res.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="work-detail-page min-h-[calc(100vh-200px)] bg-white pb-[82px] pt-[27px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px] xl:px-0">
      <div class="detail-breadcrumb flex items-center gap-[7px] text-[#777]">
        <i class="iconfont icon-shouye text-[#999999]"></i>
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#047eff] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <RouterLink to="/materials" class="text-[#047eff] hover:underline">课程资料</RouterLink>
        <span class="mx-1">/</span>
        <span>{{ material?.title || '资料详情' }}</span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="mt-[36px] text-center py-16">
        <div class="inline-block w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-3 text-gray-500">加载中...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="mt-[36px] text-center py-16">
        <p class="text-red-500">{{ error }}</p>
      </div>

      <!-- Content -->
      <article v-else-if="material" class="mt-[19px] overflow-hidden rounded-[12px] bg-white shadow-[0_4px_18px_rgba(24,42,78,0.12)]">
        <!-- Header -->
        <div class="relative h-[180px] overflow-hidden bg-[#e7f8ff]">
          <img
            v-if="material.cover_image"
            :src="material.cover_image"
            alt=""
            class="absolute inset-0 h-full w-full object-cover"
          />
          <div class="absolute inset-0 bg-gradient-to-r from-[#0066cc]/80 to-[#004385]/80"></div>
          <div class="absolute inset-0 flex flex-col justify-center px-[39px]">
            <h1 class="text-[28px] font-[800] leading-[34px] text-white">{{ material.title }}</h1>
            <div class="mt-[15px] flex items-center gap-[31px] text-[16px] leading-[20px] text-white/80">
              <span v-if="material.author" class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-zongzhiduiwu text-[22px]"></i>
                {{ material.author }}
              </span>
              <span class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-shijian text-[22px]"></i>
                {{ formatDate(material.created_at) }}
              </span>
              <span class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-icon- text-[22px]"></i>
                {{ material.view_count || 0 }} 浏览
              </span>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="px-[39px] pr-[12px] pb-[31px] pt-[17px]">
          <div class="article-content detail-scroll" v-html="renderedContent"></div>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.detail-breadcrumb {
  font-size: 14px;
  line-height: 20px;
}

.detail-scroll::-webkit-scrollbar,
.detail-scroll::-webkit-scrollbar-thumb,
.detail-scroll::-webkit-scrollbar-thumb:hover,
.detail-scroll::-webkit-scrollbar-thumb:active {
  background: #0a7fff;
  height: 4px;
  width: 5px;
  border-radius: 3px;
}

.detail-scroll::-webkit-scrollbar-track {
  background: #f0f0f0;
  width: 5px;
  border-radius: 3px;
}

.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: #5f5f5f;
}

.article-content :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  color: #007dff;
  margin: 24px 0 16px;
  line-height: 1.4;
}

.article-content :deep(h2) {
  font-size: 20px;
  font-weight: 700;
  color: #007dff;
  margin: 20px 0 14px;
  line-height: 1.4;
}

.article-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 18px 0 12px;
}

.article-content :deep(p) {
  margin: 12px 0;
  text-indent: 2em;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 12px 0;
  padding-left: 2em;
}

.article-content :deep(li) {
  margin: 8px 0;
}

.article-content :deep(code) {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.article-content :deep(pre) {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #007dff;
  padding-left: 16px;
  margin: 16px 0;
  color: #666;
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
}

.article-content :deep(a) {
  color: #007dff;
  text-decoration: none;
}

.article-content :deep(a:hover) {
  text-decoration: underline;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.article-content :deep(th),
.article-content :deep(td) {
  border: 1px solid #ddd;
  padding: 10px 14px;
  text-align: left;
}

.article-content :deep(th) {
  background: #f5f5f5;
  font-weight: 600;
}

@media (max-width: 767px) {
  .work-detail-page {
    padding-top: 20px;
  }

  .article-content :deep(h1) {
    font-size: 20px;
  }

  .article-content :deep(h2) {
    font-size: 18px;
  }
}
</style>