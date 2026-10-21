<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { contentApi } from '@/api'
import markdownIt from 'markdown-it'
import { mediaPlugin } from '@/plugins/markdown'

const route = useRoute()
const router = useRouter()
const article = ref<any>(null)
const loading = ref(true)
const error = ref('')

const md = markdownIt({
  html: true,
  linkify: true,
  typographer: true
}).use(mediaPlugin)

const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  return md.render(article.value.content)
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

onMounted(async () => {
  await fetchArticle()
})

async function fetchArticle() {
  loading.value = true
  try {
    const id = Number(route.params.id || route.query.id)
    const res = await contentApi.get(id)
    article.value = res.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || '加载失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="min-h-[calc(100vh-200px)] pb-[80px] pt-[28px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px]">
      <div class="flex items-center gap-[6px] text-[14px] text-[#86868b]">
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#0071e3] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <RouterLink to="/news" class="text-[#0071e3] hover:underline">新闻资讯</RouterLink>
        <span class="mx-1">/</span>
        <span>{{ article?.title || '新闻详情' }}</span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="mt-[48px] text-center py-16">
        <div class="inline-block h-10 w-10 animate-spin rounded-full border-4 border-[#0071e3]/20 border-t-[#0071e3]"></div>
        <p class="mt-3 text-[#86868b]">加载中...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="mt-[48px] text-center py-16">
        <p class="text-[#ff3b30]">{{ error }}</p>
        <el-button type="primary" round class="mt-4" @click="router.push('/news')">返回列表</el-button>
      </div>

      <!-- Content -->
      <article v-else-if="article" class="anim-fade-up mt-[20px] overflow-hidden rounded-[24px] border border-white/70 bg-white/85 shadow-[var(--shadow-card)] backdrop-blur-xl">
        <!-- 绚丽渐变 Header -->
        <div class="relative h-[200px] overflow-hidden bg-gradient-to-br from-[#0090ff] via-[#6a5cff] to-[#ff5ca8]">
          <img
            v-if="article.cover_image"
            :src="article.cover_image"
            alt=""
            class="absolute inset-0 h-full w-full object-cover opacity-30 mix-blend-overlay"
          />
          <div class="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-white/15 blur-3xl"></div>
          <div class="absolute inset-0 flex flex-col justify-center px-[36px] lg:px-[44px]">
            <h1 class="text-[26px] font-[800] leading-[36px] text-white drop-shadow-lg lg:text-[30px]">
              {{ article.title }}
            </h1>
            <div class="mt-[14px] flex flex-wrap items-center gap-[24px] text-[14px] text-white/85">
              <span v-if="article.author" class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-zongzhiduiwu text-[19px]"></i>
                {{ article.author }}
              </span>
              <span class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-shijian text-[19px]"></i>
                {{ formatDate(article.created_at) }}
              </span>
              <span class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-icon- text-[19px]"></i>
                {{ article.view_count || 0 }} 浏览
              </span>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="px-[32px] pb-[36px] pt-[24px] lg:px-[44px]">
          <div class="article-content" v-html="renderedContent"></div>
        </div>
      </article>

      <!-- Back Button -->
      <div class="anim-fade-up mt-[32px] text-center">
        <el-button type="primary" round size="large" class="!px-[36px]" @click="router.push('/news')">返回列表</el-button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.article-content {
  font-size: 16px;
  line-height: 1.9;
  color: #3a3a3c;
}

.article-content :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  color: #1d1d1f;
  margin: 24px 0 16px;
  line-height: 1.4;
}

.article-content :deep(h2) {
  font-size: 20px;
  font-weight: 700;
  color: #1d1d1f;
  margin: 20px 0 14px;
  line-height: 1.4;
  padding-left: 12px;
  border-left: 4px solid;
  border-image: linear-gradient(to bottom, #0090ff, #6a5cff) 1;
}

.article-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 18px 0 12px;
}

.article-content :deep(p) {
  margin: 12px 0;
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
  background: rgba(120, 120, 128, 0.12);
  padding: 2px 8px;
  border-radius: 6px;
  font-family: ui-monospace, "SF Mono", monospace;
  font-size: 0.9em;
}

.article-content :deep(pre) {
  background: #1d1d1f;
  color: #e8e8ed;
  padding: 18px;
  border-radius: 14px;
  overflow-x: auto;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #0090ff;
  padding: 12px 18px;
  margin: 16px 0;
  color: #515154;
  background: rgba(0, 113, 227, 0.05);
  border-radius: 0 14px 14px 0;
}

.article-content :deep(a) {
  color: #0071e3;
  text-decoration: none;
}

.article-content :deep(a:hover) {
  text-decoration: underline;
}

.article-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 16px;
  margin: 16px 0;
  box-shadow: var(--shadow-card);
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin: 16px 0;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(120, 120, 128, 0.18);
}

.article-content :deep(th),
.article-content :deep(td) {
  border-bottom: 1px solid rgba(120, 120, 128, 0.14);
  padding: 10px 14px;
  text-align: left;
}

.article-content :deep(th) {
  background: rgba(120, 120, 128, 0.08);
  font-weight: 600;
}

@media (max-width: 767px) {
  .article-content :deep(h1) {
    font-size: 20px;
  }

  .article-content :deep(h2) {
    font-size: 18px;
  }
}
</style>
