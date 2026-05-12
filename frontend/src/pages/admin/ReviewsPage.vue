<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import Dialog from '@/components/Dialog.vue'
import { useNotification } from '@/composables/useNotification'

const authStore = useAuthStore()
const { success, error } = useNotification()
const works = ref<any[]>([])
const loading = ref(true)
const page = ref(1)
const total = ref(0)
const pageSize = 20
const teamName = ref('')
const workName = ref('')
const isScored: any = ref('')

const showDialog = ref(false)
const dialogType = ref<'review'>('review')
const showPdfModal = ref(false)
const showVideoModal = ref(false)
const selectedWork = ref<any>(null)
const reviewForm = ref({
  score: 0,
  comment: ''
})
const workReviews = ref<any[]>([])

const canAudit = computed(() => authStore.isAdmin || authStore.isReviewer)
const isAdmin = computed(() => authStore.isAdmin)

onMounted(() => {
  fetchReviews()
})

async function fetchReviews() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_width: pageSize }
    if (teamName.value) params.team_name = teamName.value
    if (workName.value) params.work_name = workName.value

    let res
    if (authStore.isAdmin) {
      // Admin sees all reviews grouped by work
      if (isScored.value !== '') params.is_scored = isScored.value === 'true'
      res = await api.get('/reviews/all-by-work', { params })
    } else {
      // Reviewer sees their own reviews
      if (isScored.value !== '') params.is_scored = isScored.value === 'true'
      res = await api.get('/reviews', { params })
    }
    works.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openReviewModal(work: any) {
  selectedWork.value = work
  reviewForm.value = {
    score: work.my_review?.score || 0,
    comment: work.my_review?.comment || ''
  }
  dialogType.value = 'review'
  showDialog.value = true
}

function openPdfViewer(work: any) {
  selectedWork.value = work
  showPdfModal.value = true
}

function openVideoPlayer(work: any) {
  selectedWork.value = work
  showVideoModal.value = true
}

async function handleSubmitReview() {
  if (!selectedWork.value) return
  try {
    if (selectedWork.value.my_review?.id) {
      await api.put(`/reviews/${selectedWork.value.my_review.id}`, {
        score: reviewForm.value.score,
        comment: reviewForm.value.comment
      })
    } else {
      await api.post('/reviews', {
        work_id: selectedWork.value.id,
        score: reviewForm.value.score,
        comment: reviewForm.value.comment
      })
    }
    showDialog.value = false
    success('提交成功')
    await fetchReviews()
  } catch (e: any) {
    error('操作失败', e.response?.data?.detail)
  }
}

function openUrl(url: string) {
  if (url) window.open(url, '_blank')
}

function getPdfUrl(path: string) {
  if (!path) return ''
  const cleanPath = path.replace(/^\.\//, '').replace(/^\//, '')
  return '/' + cleanPath
}

function getVideoUrl(path: string) {
  if (!path) return ''
  const cleanPath = path.replace(/^\.\//, '').replace(/^\//, '')
  return '/' + cleanPath
}

function handlePageChange(newPage: number) {
  page.value = newPage
  fetchReviews()
}

function handleSearch() {
  page.value = 1
  fetchReviews()
}

function getScoreColor(score: number | undefined): string {
  if (!score) return 'text-gray-400'
  if (score >= 90) return 'text-green-600'
  if (score >= 70) return 'text-blue-600'
  if (score >= 60) return 'text-amber-600'
  return 'text-red-600'
}

function calculateAverage(reviews: any[]): number {
  const scored = reviews.filter((r: any) => r.score != null)
  if (scored.length === 0) return 0
  return scored.reduce((sum: number, r: any) => sum + r.score, 0) / scored.length
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">评审管理</h1>
          <p class="text-sm text-gray-500 mt-1">专家评分与作品审核</p>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="flex-1 relative">
          <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <input
            v-model="teamName"
            type="text"
            placeholder="队伍名称"
            class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            @keyup.enter="handleSearch"
          />
        </div>
        <div class="flex-1 relative">
          <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
          </svg>
          <input
            v-model="workName"
            type="text"
            placeholder="作品名称"
            class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            @keyup.enter="handleSearch"
          />
        </div>
        <select
          v-model="isScored"
          class="px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white min-w-[140px]"
          @change="handleSearch"
        >
          <option value="">全部</option>
          <option value="true">已打分</option>
          <option value="false">未打分</option>
        </select>
        <button
          @click="handleSearch"
          class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium"
        >
          搜索
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">作品名</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">队伍</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">主题</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">我的评分</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">平均分</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="work in works"
            :key="work.id"
            class="hover:bg-blue-50/50 transition-colors"
          >
            <td class="px-6 py-4 text-sm">
              <button @click="openReviewModal(work)" class="text-blue-600 hover:text-blue-700 font-medium transition-colors">
                {{ work.name }}
              </button>
            </td>
            <td class="px-6 py-4 text-sm text-gray-600">{{ work.team_name || '-' }}</td>
            <td class="px-6 py-4 text-sm text-gray-600">{{ work.theme_name || '-' }}</td>
            <td class="px-6 py-4 text-sm">
              <span v-if="work.my_review?.score" class="font-bold" :class="getScoreColor(work.my_review.score)">
                {{ work.my_review.score }}
              </span>
              <span v-else class="text-gray-400 text-sm">未评分</span>
            </td>
            <td class="px-6 py-4 text-sm">
              <span v-if="work.score" class="text-gray-700 font-medium">{{ work.score.toFixed(1) }}</span>
              <span v-else class="text-gray-400">-</span>
            </td>
            <td class="px-6 py-4 text-sm">
              <div class="flex flex-wrap items-center gap-2">
                <button
                  v-if="!isScored || work.my_review?.score"
                  @click="openReviewModal(work)"
                  class="inline-flex items-center gap-1 px-2.5 py-1.5 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 text-xs font-medium transition-colors"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                  {{ work.my_review?.id ? '编辑' : '评分' }}
                </button>
                <template v-if="work.agent_url">
                  <button
                    @click="openUrl(work.agent_url)"
                    class="inline-flex items-center gap-1 px-2.5 py-1.5 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 text-xs font-medium transition-colors"
                    title="打开智能体链接"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                    </svg>
                    智能体
                  </button>
                </template>
                <template v-if="work.agent_editor_url">
                  <button
                    @click="openUrl(work.agent_editor_url)"
                    class="inline-flex items-center gap-1 px-2.5 py-1.5 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 text-xs font-medium transition-colors"
                    title="打开编排链接"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                    </svg>
                    编排
                  </button>
                </template>
                <template v-if="work.pdf_file">
                  <button
                    @click="openPdfViewer(work)"
                    class="inline-flex items-center gap-1 px-2.5 py-1.5 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 text-xs font-medium transition-colors"
                    title="查看PDF文档"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                    </svg>
                    PDF
                  </button>
                </template>
                <template v-if="work.video_file">
                  <button
                    @click="openVideoPlayer(work)"
                    class="inline-flex items-center gap-1 px-2.5 py-1.5 bg-pink-100 text-pink-700 rounded-lg hover:bg-pink-200 text-xs font-medium transition-colors"
                    title="播放演示视频"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    视频
                  </button>
                </template>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-flex items-center gap-2 text-gray-500">
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          加载中...
        </div>
      </div>
      <div v-else-if="works.length === 0" class="text-center py-12 text-gray-500">
        <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        暂无数据
      </div>

      <div v-if="total > pageSize" class="px-6 py-4 border-t border-gray-100 flex justify-center">
        <div class="flex items-center gap-1">
          <button
            @click="handlePageChange(page - 1)"
            :disabled="page === 1"
            class="px-3 py-1.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            上一页
          </button>
          <div class="px-4 py-1.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg text-sm font-medium shadow-md">
            {{ page }} / {{ Math.ceil(total / pageSize) }}
          </div>
          <button
            @click="handlePageChange(page + 1)"
            :disabled="page * pageSize >= total"
            class="px-3 py-1.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- Review Dialog -->
    <Dialog
      :show="showDialog && dialogType === 'review'"
      :title="`评审 - ${selectedWork?.name}`"
      subtitle="专家评分与评价"
      width="md"
      @close="showDialog = false"
    >
      <div class="p-6 space-y-5">
        <div class="bg-gray-50 rounded-xl p-4">
          <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">作品描述</label>
          <p class="text-gray-800 mt-1">{{ selectedWork?.description || '暂无描述' }}</p>
        </div>

        <div class="flex flex-wrap gap-2">
          <button v-if="selectedWork?.agent_url" @click="openUrl(selectedWork.agent_url)" class="px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 text-sm font-medium transition-colors">
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
            </svg>
            智能体URL
          </button>
          <button v-if="selectedWork?.agent_editor_url" @click="openUrl(selectedWork.agent_editor_url)" class="px-3 py-1.5 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 text-sm font-medium transition-colors">
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
            </svg>
            编排URL
          </button>
          <button v-if="selectedWork?.pdf_file" @click="openPdfViewer(selectedWork)" class="px-3 py-1.5 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 text-sm font-medium transition-colors">
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
            </svg>
            PDF文档
          </button>
          <button v-if="selectedWork?.video_file" @click="openVideoPlayer(selectedWork)" class="px-3 py-1.5 bg-pink-100 text-pink-700 rounded-lg hover:bg-pink-200 text-sm font-medium transition-colors">
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            演示视频
          </button>
        </div>

        <form @submit.prevent="handleSubmitReview" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">评分 (0-100)</label>
            <div class="relative">
              <input
                v-model.number="reviewForm.score"
                type="number"
                min="0"
                max="100"
                class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              />
              <div class="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-500">分</div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">评价</label>
            <textarea
              v-model="reviewForm.comment"
              rows="4"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              placeholder="请输入评价..."
            ></textarea>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              @click="showDialog = false"
              class="px-5 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 font-medium text-gray-700 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium"
            >
              保存
            </button>
          </div>
        </form>
      </div>
    </Dialog>

    <!-- PDF Viewer Dialog -->
    <Dialog
      :show="showPdfModal"
      title="PDF文档预览"
      :subtitle="selectedWork?.name"
      width="6xl"
      @close="showPdfModal = false"
    >
      <div class="h-[70vh]">
        <iframe :src="getPdfUrl(selectedWork?.pdf_file)" class="w-full h-full" frameborder="0"></iframe>
      </div>
    </Dialog>

    <!-- Video Player Dialog -->
    <Dialog
      :show="showVideoModal"
      title="演示视频播放"
      :subtitle="selectedWork?.name"
      width="lg"
      @close="showVideoModal = false"
    >
      <div class="p-4 bg-black">
        <video :src="getVideoUrl(selectedWork?.video_file)" controls class="w-full rounded-lg" preload="metadata">
          您的浏览器不支持视频播放
        </video>
      </div>
    </Dialog>
  </div>
</template>