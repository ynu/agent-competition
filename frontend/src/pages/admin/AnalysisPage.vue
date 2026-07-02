<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { analysisApi } from '@/api/analysis'
import type {
  AnalysisSummary,
  TopWorksResponse,
  ReviewerProgressResponse,
  ScoreDistributionResponse,
  ReviewerDetailsResponse,
  HistogramData,
  LineData,
  BoxplotData
} from '@/api/analysis'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart, LineChart, BoxplotChart, ScatterChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([BarChart, LineChart, BoxplotChart, ScatterChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent, CanvasRenderer])

const summary = ref<AnalysisSummary | null>(null)
const topWorks = ref<TopWorksResponse | null>(null)
const reviewerProgress = ref<ReviewerProgressResponse | null>(null)
const chartData = ref<ScoreDistributionResponse | null>(null)
const reviewerDetails = ref<ReviewerDetailsResponse | null>(null)
const loading = ref(false)
const topN = ref(10)
const sortBy = ref<'final_score' | 'review_score' | 'vote_count'>('final_score')
const chartType = ref<'histogram' | 'line' | 'boxplot'>('histogram')
const selectedReviewerId = ref<number | null>(null)
const expandedWorkId = ref<number | null>(null)

async function loadData() {
  loading.value = true
  try {
    const [s, tw, rp, cd, rd] = await Promise.all([
      analysisApi.getSummary(),
      analysisApi.getTopWorks({ top: topN.value }),
      analysisApi.getReviewerProgress(),
      analysisApi.getScoreDistribution(chartType.value),
      analysisApi.getReviewerDetails()
    ])
    summary.value = s.data
    topWorks.value = tw.data
    reviewerProgress.value = rp.data
    chartData.value = cd.data
    reviewerDetails.value = rd.data

    // Debug: 检查数据
    console.log('reviewerDetails:', reviewerDetails.value)
    if (reviewerDetails.value?.reviewers.length) {
      console.log('First reviewer scores:', reviewerDetails.value.reviewers[0].scores)
    }
  } finally {
    loading.value = false
  }
}

async function switchChart(type: 'histogram' | 'line' | 'boxplot') {
  chartType.value = type
  try {
    const cd = await analysisApi.getScoreDistribution(type)
    chartData.value = cd.data
  } catch (e) {
    console.error('Failed to load chart data:', e)
  }
}

// 评分项接口
interface ReviewerScoreItem {
  workId: number
  workName: string
  score: number
}

// 获取选中评审的评分列表
const selectedReviewerScores = computed<ReviewerScoreItem[]>(() => {
  if (!selectedReviewerId.value) return []

  const reviewer = reviewerDetails.value?.reviewers.find(r => r.user_id === selectedReviewerId.value)
  if (!reviewer) return []

  console.log('Looking for reviewer:', selectedReviewerId.value)
  console.log('Reviewer found:', reviewer)
  console.log('Reviewer scores keys:', Object.keys(reviewer.scores))

  const result: ReviewerScoreItem[] = []
  const works = reviewerDetails.value?.works || []

  works.forEach(work => {
    // 尝试多种方式获取分数
    let score = reviewer.scores[work.id]
    if (score === undefined || score === null) {
      score = reviewer.scores[String(work.id)]
    }
    if (score === undefined || score === null) {
      score = reviewer.scores[work.name]
    }

    console.log(`Work ${work.id} (${work.name}): score = ${score}`)

    if (score !== undefined && score !== null) {
      result.push({
        workId: work.id,
        workName: work.name,
        score: score as number
      })
    }
  })

  console.log('Final result:', result)
  return result.sort((a, b) => b.score - a.score)
})

// 选中评审的评分分布图表配置
const reviewerChartOption = computed(() => {
  const scores = selectedReviewerScores.value
  if (!scores.length) return {}

  if (chartType.value === 'histogram') {
    // 按10分区间分组
    const bins: { range: string; count: number; scores: number[] }[] = []
    for (let i = 0; i < 10; i++) {
      bins.push({ range: `${i * 10}-${(i + 1) * 10}`, count: 0, scores: [] })
    }

    scores.forEach(item => {
      const binIndex = Math.min(Math.floor(item.score / 10), 9)
      bins[binIndex].count++
      bins[binIndex].scores.push(item.score)
    })

    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: bins.map(b => b.range),
        name: '分数区间',
        axisLabel: { rotate: 45 }
      },
      yAxis: { type: 'value', name: '作品数' },
      series: [{
        type: 'bar',
        data: bins.map(b => b.count),
        itemStyle: { color: '#10b981' }
      }]
    }
  }

  if (chartType.value === 'line') {
    return {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const item = scores[params.dataIndex]
          return `${item.workName}<br/>分数: ${item.score}`
        }
      },
      grid: { left: '3%', right: '4%', bottom: '10%', top: '10%', containLabel: true },
      xAxis: { type: 'value', name: '排名', min: 1 },
      yAxis: { type: 'value', name: '分数', min: 0, max: 100 },
      series: [{
        type: 'line',
        data: scores.map((s, i) => [i + 1, s.score]),
        smooth: true,
        itemStyle: { color: '#10b981' },
        areaStyle: { color: 'rgba(16, 185, 129, 0.1)' },
        symbol: 'circle',
        symbolSize: 8
      }]
    }
  }

  if (chartType.value === 'boxplot') {
    // 计算箱线图统计数据
    const scoreValues = scores.map(s => s.score).sort((a, b) => a - b)
    const len = scoreValues.length

    if (len === 0) return {}

    const min = scoreValues[0]
    const max = scoreValues[len - 1]
    const median = len % 2 === 0
      ? (scoreValues[len / 2 - 1] + scoreValues[len / 2]) / 2
      : scoreValues[Math.floor(len / 2)]
    const q1Index = Math.floor(len * 0.25)
    const q3Index = Math.floor(len * 0.75)
    const q1 = scoreValues[q1Index]
    const q3 = scoreValues[q3Index]

    return {
      tooltip: {
        trigger: 'item',
        formatter: () => {
          return `评审评分分布<br/>最小值: ${min.toFixed(1)}<br/>Q1: ${q1.toFixed(1)}<br/>中位数: ${median.toFixed(1)}<br/>Q3: ${q3.toFixed(1)}<br/>最大值: ${max.toFixed(1)}`
        }
      },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: ['评分分布'], name: '' },
      yAxis: { type: 'value', name: '分数', min: 0, max: 100 },
      series: [{
        type: 'boxplot',
        data: [[min, q1, median, q3, max]],
        itemStyle: { color: '#10b981', borderColor: '#059669', borderWidth: 2 }
      }]
    }
  }

  return {}
})

// 全局评分分布图表配置
const globalChartOption = computed(() => {
  if (!chartData.value?.data) return {}

  if (chartType.value === 'histogram') {
    const data = chartData.value.data as HistogramData
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: data.bins.map(b => `${b.range_start}-${b.range_end}`),
        name: '分数区间',
        axisLabel: { rotate: 45 }
      },
      yAxis: { type: 'value', name: '作品数' },
      series: [{
        type: 'bar',
        data: data.bins.map(b => b.count),
        itemStyle: { color: '#3b82f6' }
      }]
    }
  }

  if (chartType.value === 'line') {
    const data = chartData.value.data as LineData
    return {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => `排名: ${params.data[0]}<br/>分数: ${params.data[1]}`
      },
      grid: { left: '3%', right: '4%', bottom: '10%', top: '10%', containLabel: true },
      xAxis: { type: 'value', name: '排名', min: 1 },
      yAxis: { type: 'value', name: '分数', min: 0, max: 100 },
      series: [{
        type: 'line',
        data: data.data.map(d => [d.rank, d.score]),
        smooth: true,
        itemStyle: { color: '#3b82f6' },
        areaStyle: { color: 'rgba(59, 130, 246, 0.1)' },
        symbol: 'circle',
        symbolSize: 6
      }]
    }
  }

  if (chartType.value === 'boxplot') {
    const data = chartData.value.data as BoxplotData
    return {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const d = data.reviewers[params.dataIndex]
          return `${d.reviewer}<br/>最小值: ${d.min_val}<br/>Q1: ${d.q1}<br/>中位数: ${d.median}<br/>Q3: ${d.q3}<br/>最大值: ${d.max_val}`
        }
      },
      grid: { left: '3%', right: '4%', bottom: '10%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: data.reviewers.map(r => r.reviewer), name: '评审' },
      yAxis: { type: 'value', name: '分数', min: 0, max: 100 },
      series: [{
        type: 'boxplot',
        data: data.reviewers.map(r => [r.min_val, r.q1, r.median, r.q3, r.max_val]),
        itemStyle: { color: '#3b82f6', borderColor: '#1d4ed8' }
      }]
    }
  }

  return {}
})

// 当前显示的图表配置
const currentChartOption = computed(() => {
  return selectedReviewerId.value ? reviewerChartOption.value : globalChartOption.value
})

// 排序后的作品列表
const sortedWorks = computed(() => {
  if (!topWorks.value?.works) return []
  const works = [...topWorks.value.works]
  if (sortBy.value === 'review_score') {
    return works.sort((a, b) => (b.review_score ?? 0) - (a.review_score ?? 0))
  } else if (sortBy.value === 'vote_count') {
    return works.sort((a, b) => b.vote_count - a.vote_count)
  } else {
    return works.sort((a, b) => b.final_score - a.final_score)
  }
})

// 获取选中评审的信息
const selectedReviewer = computed(() => {
  if (!selectedReviewerId.value || !reviewerDetails.value) return null
  return reviewerDetails.value.reviewers.find(r => r.user_id === selectedReviewerId.value) ?? null
})

function selectReviewer(userId: number | null) {
  selectedReviewerId.value = userId
}

// 计算某个作品的箱线图数据
function getWorkBoxplotOption(workId: number) {
  if (!reviewerDetails.value) return {}

  const work = reviewerDetails.value.works.find(w => w.id === workId)
  if (!work) return {}

  // 收集所有评审对该作品的评分
  const scores: number[] = []
  reviewerDetails.value.reviewers.forEach(reviewer => {
    const score = reviewer.scores[String(workId)]
    if (score !== undefined && score !== null) {
      scores.push(score)
    }
  })

  if (scores.length === 0) {
    return { tooltip: { trigger: 'item', formatter: () => '暂无评分数据' } }
  }

  // 计算箱线图统计
  const sorted = [...scores].sort((a, b) => a - b)
  const len = sorted.length
  const min = sorted[0]
  const max = sorted[len - 1]
  const median = len % 2 === 0
    ? (sorted[len / 2 - 1] + sorted[len / 2]) / 2
    : sorted[Math.floor(len / 2)]
  const q1 = sorted[Math.floor(len * 0.25)]
  const q3 = sorted[Math.floor(len * 0.75)]

  return {
    tooltip: {
      trigger: 'item',
      formatter: () => {
        return `评分分布<br/>最小值: ${min.toFixed(1)}<br/>Q1: ${q1.toFixed(1)}<br/>中位数: ${median.toFixed(1)}<br/>Q3: ${q3.toFixed(1)}<br/>最大值: ${max.toFixed(1)}`
      }
    },
    grid: { left: '3%', right: '3%', bottom: '10%', top: '5%', containLabel: true },
    xAxis: { type: 'category', data: ['评分分布'] },
    yAxis: { type: 'value', name: '分数', min: 0, max: 100 },
    series: [{
      type: 'boxplot',
      data: [[min, q1, median, q3, max]],
      itemStyle: {
        color: '#8b5cf6',
        borderColor: '#7c3aed',
        borderWidth: 2
      }
    }]
  }
}

function toggleWorkExpand(workId: number) {
  expandedWorkId.value = expandedWorkId.value === workId ? null : workId
}

// 辅助函数：获取评审对某个作品的分数
function getWorkScore(reviewer: { scores: Record<string, number | null> }, workId: number): number | null {
  const score = reviewer.scores[String(workId)]
  return score ?? null
}

onMounted(loadData)
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">评分分析</h1>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12 text-gray-500">加载中...</div>

    <template v-else>
      <!-- Filters -->
      <div class="flex gap-4 mb-6 items-center flex-wrap">
        <select v-model="sortBy" @change="loadData" class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="final_score">按总分排序</option>
          <option value="review_score">按评审分排序</option>
          <option value="vote_count">按投票数排序</option>
        </select>
        <select v-model="topN" @change="loadData" class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option :value="10">Top 10</option>
          <option :value="20">Top 20</option>
          <option :value="50">Top 50</option>
        </select>
      </div>

      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-gray-500 text-sm">作品总数</div>
          <div class="text-2xl font-bold text-blue-600">{{ summary?.total_works ?? 0 }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-gray-500 text-sm">评审人数</div>
          <div class="text-2xl font-bold text-purple-600">{{ summary?.total_reviewers ?? 0 }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-gray-500 text-sm">平均分</div>
          <div class="text-2xl font-bold text-green-600">{{ summary?.avg_score?.toFixed(1) ?? '-' }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-gray-500 text-sm">待评审数</div>
          <div class="text-2xl font-bold text-orange-600">{{ summary?.pending_reviews ?? 0 }}</div>
        </div>
      </div>

      <!-- Top N Works -->
      <div class="bg-white rounded-lg shadow p-4 mb-6">
        <h2 class="text-lg font-semibold mb-4">Top {{ topN }} 作品排行</h2>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="bg-gray-50">
                <th class="px-4 py-2 text-left text-sm font-medium text-gray-600 w-12">排名</th>
                <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">作品名称</th>
                <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">团队</th>
                <th class="px-4 py-2 text-left text-sm font-medium text-gray-600 w-24">投票数</th>
                <th class="px-4 py-2 text-left text-sm font-medium text-gray-600 w-24">评审分</th>
                <th class="px-4 py-2 text-left text-sm font-medium text-gray-600 w-24">总分</th>
                <th class="px-4 py-2 text-left text-sm font-medium text-gray-600 w-12"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <template v-for="(work, index) in sortedWorks" :key="work.work_id">
                <tr class="hover:bg-gray-50">
                  <td class="px-4 py-2">
                    <span v-if="index < 3" class="inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold"
                      :class="{
                        'bg-yellow-100 text-yellow-700': index === 0,
                        'bg-gray-200 text-gray-700': index === 1,
                        'bg-orange-100 text-orange-700': index === 2
                      }">
                      {{ index + 1 }}
                    </span>
                    <span v-else class="text-gray-600">{{ index + 1 }}</span>
                  </td>
                  <td class="px-4 py-2 font-medium">{{ work.work_name }}</td>
                  <td class="px-4 py-2 text-gray-600">{{ work.team_name }}</td>
                  <td class="px-4 py-2 text-center">{{ work.vote_count }}</td>
                  <td class="px-4 py-2 text-center">{{ work.review_score?.toFixed(1) || '-' }}</td>
                  <td class="px-4 py-2 text-center font-semibold text-blue-600">{{ work.final_score.toFixed(1) }}</td>
                  <td class="px-4 py-2 text-center">
                    <button
                      @click="toggleWorkExpand(work.work_id)"
                      class="p-1 rounded hover:bg-gray-200 transition"
                      :title="expandedWorkId === work.work_id ? '收起' : '查看各评审评分'"
                    >
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': expandedWorkId === work.work_id }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </td>
                </tr>
                <!-- Expanded Row: Boxplot Chart -->
                <tr v-if="expandedWorkId === work.work_id">
                  <td colspan="7" class="px-4 py-4 bg-gray-50">
                    <div class="flex items-center gap-4">
                      <div class="flex-shrink-0">
                        <div class="text-sm font-medium text-gray-600 mb-2">各评审评分分布</div>
                        <div class="w-64 h-48">
                          <v-chart :option="getWorkBoxplotOption(work.work_id)" autoresize class="w-full h-full" />
                        </div>
                      </div>
                      <div class="flex-1">
                        <div class="text-sm font-medium text-gray-600 mb-2">各评审打分</div>
                        <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
                          <div
                            v-for="reviewer in reviewerDetails?.reviewers"
                            :key="reviewer.user_id"
                            class="flex items-center gap-2 p-2 bg-white rounded border"
                          >
                            <span class="text-sm text-gray-600 truncate max-w-[80px]">{{ reviewer.username }}</span>
                            <span
                              v-if="getWorkScore(reviewer, work.work_id) !== null"
                              class="font-semibold"
                              :class="{
                                'text-yellow-600': getWorkScore(reviewer, work.work_id)! >= 90,
                                'text-green-600': getWorkScore(reviewer, work.work_id)! >= 70 && getWorkScore(reviewer, work.work_id)! < 90,
                                'text-blue-600': getWorkScore(reviewer, work.work_id)! >= 50 && getWorkScore(reviewer, work.work_id)! < 70,
                                'text-gray-600': getWorkScore(reviewer, work.work_id)! < 50
                              }"
                            >
                              {{ getWorkScore(reviewer, work.work_id)?.toFixed(1) }}
                            </span>
                            <span v-else class="text-gray-400 text-sm">-</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
              <tr v-if="!sortedWorks.length">
                <td colspan="7" class="px-4 py-8 text-center text-gray-500">暂无数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Reviewer Progress -->
      <div class="bg-white rounded-lg shadow p-4 mb-6">
        <h2 class="text-lg font-semibold mb-4">各评审评分进度</h2>
        <div v-if="reviewerProgress?.progress?.length" class="space-y-3">
          <div
            v-for="p in reviewerProgress?.progress"
            :key="p.user_id"
            class="flex items-center gap-4"
          >
            <div class="w-32">
              <button
                @click="selectReviewer(selectedReviewerId === p.user_id ? null : p.user_id)"
                class="text-sm font-medium hover:text-blue-600 transition text-left"
                :class="{ 'text-blue-600': selectedReviewerId === p.user_id }"
              >
                {{ p.username }}
              </button>
            </div>
            <div class="flex-1">
              <div class="flex justify-between mb-1">
                <span class="text-sm text-gray-500">{{ p.reviewed_count }}/{{ p.total_count }} ({{ p.percentage }}%)</span>
              </div>
              <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  class="h-full transition-all duration-300"
                  :class="selectedReviewerId === p.user_id ? 'bg-green-500' : 'bg-blue-500'"
                  :style="{ width: p.percentage + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">暂无数据</div>
      </div>

      <!-- Charts Section -->
      <div class="bg-white rounded-lg shadow p-4 mb-6">
        <!-- Chart Controls -->
        <div class="flex flex-wrap gap-4 mb-4 items-center">
          <!-- Reviewer Selector Dropdown -->
          <select
            v-model="selectedReviewerId"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option :value="null">全局视图（所有作品）</option>
            <option
              v-for="reviewer in reviewerDetails?.reviewers"
              :key="reviewer.user_id"
              :value="reviewer.user_id"
            >
              {{ reviewer.username }} ({{ reviewer.avg_score?.toFixed(1) ?? '-' }})
            </option>
          </select>

          <!-- Chart Type Selector -->
          <div class="flex gap-2">
            <button
              @click="switchChart('histogram')"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-medium transition',
                chartType === 'histogram' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]">
              直方图
            </button>
            <button
              @click="switchChart('line')"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-medium transition',
                chartType === 'line' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]">
              折线图
            </button>
            <button
              @click="switchChart('boxplot')"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-medium transition',
                chartType === 'boxplot' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]">
              箱线图
            </button>
          </div>

          <!-- Selected Reviewer Badge -->
          <div v-if="selectedReviewer" class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
            {{ selectedReviewer.username }} - {{ selectedReviewerScores.length }} 个评分
          </div>
        </div>

        <!-- Chart -->
        <div class="h-80 w-full">
          <v-chart :option="currentChartOption" autoresize class="w-full h-full" />
        </div>
      </div>

      <!-- Reviewer Score Details (Only shown when a reviewer is selected) -->
      <div v-if="selectedReviewer" class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">{{ selectedReviewer.username }} - 评分详情</h2>
          <div class="text-sm text-gray-500">
            共 {{ selectedReviewerScores.length }} 个作品，平均分 {{ selectedReviewer.avg_score?.toFixed(1) }}
          </div>
        </div>

        <!-- Score Cards Grid -->
        <div v-if="selectedReviewerScores.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          <div
            v-for="(item, index) in selectedReviewerScores"
            :key="item.workId"
            class="border border-gray-200 rounded-lg p-3 hover:shadow-md transition"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0 mr-2">
                <div class="text-xs text-gray-500 mb-1">#{{ index + 1 }}</div>
                <div class="font-medium text-sm truncate" :title="item.workName">
                  {{ item.workName }}
                </div>
              </div>
              <div
                class="text-xl font-bold"
                :class="{
                  'text-yellow-600': item.score >= 90,
                  'text-green-600': item.score >= 70 && item.score < 90,
                  'text-blue-600': item.score >= 50 && item.score < 70,
                  'text-gray-600': item.score < 50
                }"
              >
                {{ item.score.toFixed(0) }}
              </div>
            </div>

            <!-- Score Bar -->
            <div class="mt-2 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full"
                :class="{
                  'bg-yellow-500': item.score >= 90,
                  'bg-green-500': item.score >= 70 && item.score < 90,
                  'bg-blue-500': item.score >= 50 && item.score < 70,
                  'bg-gray-400': item.score < 50
                }"
                :style="{ width: item.score + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <!-- No scores message -->
        <div v-else class="text-center py-8 text-gray-500">
          <p>该评审暂无评分记录</p>
          <p class="text-sm mt-2">已评分 {{ selectedReviewer.progress }} 个作品</p>
        </div>
      </div>
    </template>
  </div>
</template>