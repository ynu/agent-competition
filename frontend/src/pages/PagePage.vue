<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { contentApi } from '@/api'
import markdownIt from 'markdown-it'
import { mediaPlugin } from '@/plugins/markdown'

const route = useRoute()

const content = ref<any>(null)
const loading = ref(true)
const error = ref('')

const md = markdownIt({ html: true, linkify: true, typographer: true }).use(mediaPlugin)

const renderedContent = computed(() => {
  if (!content.value?.content) return ''
  if (content.value.content_format === 'markdown') {
    const markdown = md.render(content.value.content)
    console.info(`Rendered markdown content for slug "${route.params.slug}":`, markdown)
    return markdown
  }
  return content.value.content
})

onMounted(async () => {
  await fetchContent()
})

async function fetchContent() {
  loading.value = true
  try {
    const response = await contentApi.getBySlug(route.params.slug as string)
    content.value = response.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || '页面不存在'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[60vh]">
    <div v-if="loading" class="text-center py-16">
      <div class="inline-flex items-center gap-2 text-gray-500">
        <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        加载中...
      </div>
    </div>
    <div v-else-if="error" class="text-center py-16">
      <div class="inline-flex items-center gap-2 text-red-500">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        {{ error }}
      </div>
    </div>
    <div v-else-if="content" class="max-w-4xl mx-auto px-4 py-8">
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 md:p-10">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">{{ content.title }}</h1>
        <div class="prose max-w-none" v-html="renderedContent"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.prose :deep(h1) { font-size: 1.8rem; font-weight: 700; margin: 1.5rem 0 1rem; color: #111; }
.prose :deep(h2) { font-size: 1.5rem; font-weight: 600; margin: 1.25rem 0 0.75rem; color: #1f2937; }
.prose :deep(h3) { font-size: 1.25rem; font-weight: 600; margin: 1rem 0 0.5rem; color: #374151; }
.prose :deep(p) { margin: 0.75rem 0; line-height: 1.8; }
.prose :deep(ul), .prose :deep(ol) { padding-left: 1.5rem; margin: 0.75rem 0; }
.prose :deep(li) { margin: 0.375rem 0; }
.prose :deep(code) { background: #f3f4f6; padding: 0.125rem 0.375rem; border-radius: 0.25rem; font-family: monospace; font-size: 0.875em; }
.prose :deep(pre) { background: #f3f4f6; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; }
.prose :deep(pre code) { background: none; padding: 0; }
.prose :deep(blockquote) { border-left: 4px solid #3b82f6; padding-left: 1rem; margin: 1rem 0; color: #6b7280; }
.prose :deep(img) { max-width: 100%; height: auto; border-radius: 0.5rem; margin: 1rem 0; }
.prose :deep(a) { color: #3b82f6; text-decoration: none; }
.prose :deep(a:hover) { text-decoration: underline; }
.prose :deep(hr) { border: none; border-top: 1px solid #e5e7eb; margin: 2rem 0; }
.prose :deep(table) { width: 100%; border-collapse: collapse; margin: 1rem 0; }
.prose :deep(th), .prose :deep(td) { border: 1px solid #e5e7eb; padding: 0.5rem 0.75rem; text-align: left; }
.prose :deep(th) { background: #f9fafb; font-weight: 600; }

/* Media styles */
.prose :deep(.md-media) { margin: 1rem 0; border-radius: 8px; overflow: hidden; background: #f8f9fa; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); }
.prose :deep(.md-media-header) { display: flex; align-items: center; gap: 0.5rem; padding: 0.625rem 0.875rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 0.875rem; font-weight: 500; }
.prose :deep(.md-image) { max-width: 100%; border-radius: 8px; margin: 1rem auto; display: block; }
.prose :deep(.md-pdf-frame) { width: 100%; height: 500px; border: none; display: block; background: #f0f0f0; }
.prose :deep(.md-audio-player), .prose :deep(.md-video-player) { width: 100%; display: block; background: #1a1a1a; }
.prose :deep(.md-audio-player) { height: 48px; }
.prose :deep(.md-video-player) { max-height: 600px; }
.prose :deep(.md-office iframe) { width: 100%; height: 500px; border: 1px solid #e5e7eb; border-radius: 8px; background: #f9fafb; }
</style>