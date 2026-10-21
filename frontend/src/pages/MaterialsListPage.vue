<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { materialsApi } from '@/api'

const router = useRouter()
const materials = ref<any[]>([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = 10
const total = ref(0)

const formatDate = (dateStr: string) => {
  if (!dateStr) return { day: '01', month: '2026-01' }
  const date = new Date(dateStr)
  return {
    day: date.getDate().toString().padStart(2, '0'),
    month: `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`
  }
}

const openMaterial = (material: any) => {
  router.push(`/materials/${material.id}`)
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchMaterials()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(async () => {
  await fetchMaterials()
})

async function fetchMaterials() {
  loading.value = true
  try {
    const res = await materialsApi.list({ page: currentPage.value, page_size: pageSize })
    materials.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (e: any) {
    console.error('Materials error:', e)
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
        <span>课程资料</span>
      </div>

      <!-- 页头 -->
      <div class="anim-fade-up mt-[28px] text-center">
        <h1 class="text-[34px] font-[700] lg:text-[44px]"><span class="text-gradient">课程资料</span></h1>
        <p class="mt-[10px] text-[15px] text-[#86868b]">学习资源，助你备战</p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="mt-[48px] text-center py-16">
        <div class="inline-block h-10 w-10 animate-spin rounded-full border-4 border-[#0071e3]/20 border-t-[#0071e3]"></div>
        <p class="mt-3 text-[#86868b]">加载中...</p>
      </div>

      <!-- Materials List -->
      <div v-else class="anim-stagger mt-[44px] grid content-start gap-[16px]">
        <button
          v-for="material in materials"
          :key="material.id"
          type="button"
          class="apple-card apple-card-hover group grid w-full grid-cols-[74px_1fr] items-center gap-[20px] border-0 p-[18px] text-left cursor-pointer"
          @click="openMaterial(material)"
        >
          <time
            class="news-date flex h-[72px] w-[74px] flex-col items-center justify-center rounded-[18px] text-white transition-all duration-300"
            :datetime="material.created_at"
          >
            <span class="text-[26px] font-[800] leading-[32px]">{{ formatDate(material.created_at).day }}</span>
            <span class="mt-[4px] text-[13px] opacity-85">{{ formatDate(material.created_at).month }}</span>
          </time>

          <div class="min-w-0">
            <h2 class="line-clamp-1 text-[17px] font-[600] text-[#1d1d1f] transition-colors duration-300 group-hover:text-[#0071e3]">
              {{ material.title }}
            </h2>
            <p class="mt-[8px] line-clamp-2 text-[13px] leading-[21px] text-[#86868b]">
              {{ material.summary || material.content?.substring(0, 150) || '暂无简介' }}
            </p>
          </div>

          <span class="hidden h-[32px] w-[32px] shrink-0 items-center justify-center rounded-full bg-[#0071e3]/8 text-[#0071e3] transition-transform duration-300 group-hover:translate-x-1 sm:flex">
            →
          </span>
        </button>

        <!-- Empty State -->
        <div v-if="materials.length === 0" class="apple-card text-center py-16">
          <p class="text-[#86868b]">暂无课程资料</p>
          <p class="mt-1 text-sm text-[#a1a1a6]">请在后台添加课程资料</p>
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
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.news-date {
  background: linear-gradient(135deg, #c7c7cc 0%, #a1a1a6 100%);
}

.group:hover .news-date {
  background: linear-gradient(135deg, #6a5cff 0%, #0090ff 100%);
  box-shadow: 0 8px 20px rgba(106, 92, 255, 0.32);
}

@media (max-width: 767px) {
  .apple-card.group {
    grid-template-columns: 64px 1fr;
    gap: 14px;
  }

  .apple-card.group time {
    width: 64px;
  }
}
</style>