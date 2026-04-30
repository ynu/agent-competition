<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { contentApi } from '@/api'
import markdownIt from 'markdown-it'

const route = useRoute()
const router = useRouter()
const article = ref<any>(null)
const loading = ref(true)
const error = ref('')

const md = markdownIt()

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

const renderMarkdown = (content: string) => {
  if (!content) return ''
  return md.render(content)
}

onMounted(async () => {
  const id = route.params.id || route.query.id
  if (!id) {
    error.value = '缺少文章ID'
    loading.value = false
    return
  }

  try {
    const res = await contentApi.get(Number(id))
    article.value = res.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || '加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="min-h-[calc(100vh-200px)] bg-white pb-[69px] pt-[27px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px]">

      <!-- Loading -->
      <div v-if="loading" class="text-center py-16">
        <div class="inline-block w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-3 text-gray-500">加载中...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-16">
        <p class="text-red-500 mb-2">{{ error }}</p>
        <el-button type="primary" @click="router.push('/news')">返回列表</el-button>
      </div>

      <!-- Article Content -->
      <article v-else class="mt-[36px]">
        <header class="text-center mb-[40px]">
          <h1 class="text-[28px] font-[700] text-[#202734] leading-[1.4] mb-[20px]">
            {{ article.title }}
          </h1>
          <div class="flex justify-center items-center gap-[20px] text-[14px] text-[#999]">
            <span v-if="article.author">作者：{{ article.author }}</span>
            <span>发布时间：{{ formatDate(article.created_at) }}</span>
            <span>浏览量：{{ article.view_count || 0 }}</span>
          </div>
        </header>

        <div
          v-if="article.content"
          class="article-content prose prose-lg max-w-none"
          v-html="renderMarkdown(article.content)"
        ></div>
        <div v-else class="text-center text-gray-400 py-12">
          暂无内容
        </div>
      </article>

      <!-- Back Button -->
      <div class="mt-[50px] text-center">
        <el-button type="primary" round @click="router.push('/news')">返回列表</el-button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.article-breadcrumb {
  font-size: 14px;
  line-height: 20px;
}

.article-breadcrumb :deep(.el-breadcrumb__inner),
.article-breadcrumb :deep(.el-breadcrumb__separator) {
  color: #777777;
  font-weight: 400;
}

.article-content :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  margin: 24px 0 16px;
  color: #202734;
}

.article-content :deep(h2) {
  font-size: 20px;
  font-weight: 700;
  margin: 20px 0 14px;
  color: #202734;
}

.article-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  margin: 18px 0 12px;
  color: #333;
}

.article-content :deep(p) {
  line-height: 1.8;
  margin: 14px 0;
  color: #5d6472;
}

.article-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 16px 0;
}

.article-content :deep(a) {
  color: #1189ff;
  text-decoration: none;
}

.article-content :deep(a:hover) {
  text-decoration: underline;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  padding-left: 24px;
  margin: 14px 0;
}

.article-content :deep(li) {
  line-height: 1.8;
  margin: 6px 0;
  color: #5d6472;
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

.article-content :deep(pre code) {
  background: none;
  padding: 0;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #1189ff;
  padding-left: 16px;
  margin: 16px 0;
  color: #666;
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 4px;
}
</style>