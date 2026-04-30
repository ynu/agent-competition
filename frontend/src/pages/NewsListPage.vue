<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { contentApi } from '@/api'

const router = useRouter()
const articles = ref<any[]>([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = 8
const total = ref(0)

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return {
    day: date.getDate().toString().padStart(2, '0'),
    month: `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`
  }
}

const openArticle = (article: any) => {
  router.push(`/page/${article.id}`)
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const summary =
  '您好，我是云小智，现在正式与全校师生见面！从今天起，我将以7×24小时在线陪伴的方式，为老师和同学们提供便捷、贴心的校园服务。'

onMounted(async () => {
  try {
    const res = await contentApi.articles({ page: currentPage.value, page_size: pageSize })
    articles.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (e: any) {
    console.error('Articles error:', e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="min-h-[calc(100vh-200px)] bg-white pb-[69px] pt-[27px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px]">
      <el-breadcrumb separator=">" class="article-list-breadcrumb">
        <el-breadcrumb-item>
          <span class="text-[#999999]">首页</span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>新闻列表</el-breadcrumb-item>
      </el-breadcrumb>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-16">
        <div class="inline-block w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-3 text-gray-500">加载中...</p>
      </div>

      <!-- Article List -->
      <div v-else class="mt-[36px]">
        <button
          v-for="article in articles"
          :key="article.id"
          type="button"
          class="article-item group grid w-full grid-cols-[80px_1fr] gap-[22px] border-0 border-b border-dashed border-[#e1e1e1] bg-transparent pb-[16px] pt-[16px] text-left first:pt-0 cursor-pointer"
          @click="openArticle(article)"
        >
          <time
            class="flex h-[74px] w-[80px] flex-col items-center justify-center text-white transition-colors duration-200 bg-[#b4b4b4] group-hover:bg-[#087fff]"
            :datetime="article.created_at"
          >
            <span class="text-[28px] font-[700] leading-[32px]">{{ formatDate(article.created_at).day }}</span>
            <span class="mt-[8px] text-[16px] leading-[18px]">{{ formatDate(article.created_at).month }}</span>
          </time>

          <div class="min-w-0 pt-[4px]">
            <h2 class="line-clamp-1 text-[16px] font-[500] leading-[24px] transition-colors duration-200 text-[#202020] group-hover:text-[#007dff]">
              {{ article.title }}
            </h2>
            <p class="mt-[8px] line-clamp-2 text-[12px] leading-[20px] text-[#999]">
              {{ article.summary || article.content?.substring(0, 150) || summary }}
            </p>
          </div>
        </button>

        <!-- Empty State -->
        <div v-if="articles.length === 0" class="text-center py-16">
          <p class="text-gray-500">暂无新闻资讯</p>
          <p class="text-gray-400 text-sm mt-1">请在后台添加新闻资讯</p>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="total > pageSize" class="mt-[54px] flex justify-center">
        <el-pagination
          v-model:current-page="currentPage"
          background
          layout="prev, pager, next"
          :page-size="pageSize"
          :total="total"
          class="article-pagination"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.article-list-breadcrumb {
  --el-text-color-regular: #777777;
  --el-color-primary: #047eff;
  font-size: 14px;
  line-height: 20px;
}

.article-list-breadcrumb :deep(.el-breadcrumb__inner),
.article-list-breadcrumb :deep(.el-breadcrumb__separator) {
  color: #777777;
  font-weight: 400;
}

.article-item {
  cursor: pointer;
}

.article-pagination :deep(.el-pager li),
.article-pagination :deep(.btn-prev),
.article-pagination :deep(.btn-next) {
  width: 30px;
  min-width: 30px;
  height: 30px;
  border-radius: 3px;
  background-color: #eeeeee;
  color: #9c9c9c;
  font-size: 14px;
  font-weight: 400;
}

.article-pagination :deep(.el-pager li.is-active) {
  background-color: #087fff;
  color: #ffffff;
}

.article-pagination :deep(.btn-prev),
.article-pagination :deep(.btn-next) {
  color: #b0b0b0;
}

@media (max-width: 767px) {
  .article-list-page {
    padding-top: 20px;
  }

  .article-item {
    grid-template-columns: 68px 1fr;
    gap: 16px;
    padding-bottom: 18px;
    padding-top: 18px;
  }

  .article-item time {
    width: 68px;
  }
}
</style>