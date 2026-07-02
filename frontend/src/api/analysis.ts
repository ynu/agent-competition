import api from './index'

// Types for analysis endpoints

export interface AnalysisSummary {
  total_works: number
  total_reviewers: number
  total_votes: number
  avg_score: number
  pending_reviews: number
}

export interface TopWorkItem {
  rank: number
  work_id: number
  work_name: string
  team_name: string
  vote_count: number
  review_score: number | null
  vote_score: number
  final_score: number
}

export interface TopWorksResponse {
  max_votes: number
  works: TopWorkItem[]
}

export interface ReviewerProgressItem {
  user_id: number
  username: string
  reviewed_count: number
  total_count: number
  percentage: number
}

export interface ReviewerProgressResponse {
  total_works: number
  progress: ReviewerProgressItem[]
}

export interface HistogramBin {
  range_start: number
  range_end: number
  count: number
}

export interface HistogramData {
  type: string
  bins: HistogramBin[]
}

export interface LineDataPoint {
  rank: number
  score: number
}

export interface LineData {
  type: string
  data: LineDataPoint[]
}

export interface BoxplotReviewer {
  reviewer: string
  min_val: number
  q1: number
  median: number
  q3: number
  max_val: number
}

export interface BoxplotData {
  type: string
  reviewers: BoxplotReviewer[]
}

// 移除单独的 BoxplotItem，避免混淆
// 使用 BoxplotReviewer 作为箱线图 reviewers 数组的元素类型

export interface ScoreDistributionResponse {
  data: HistogramData | LineData | BoxplotData
}

export type ScoreDistributionData = HistogramData | LineData | BoxplotData

export interface WorkScoreItem {
  id: number
  name: string
}

export interface ReviewerDetailItem {
  user_id: number
  username: string
  scores: Record<string, number | null>
  avg_score: number | null
  progress: string
}

export interface ReviewerDetailsResponse {
  works: WorkScoreItem[]
  reviewers: ReviewerDetailItem[]
}

// Analysis API
export const analysisApi = {
  getSummary: (params?: { theme_id?: number; status?: string }) =>
    api.get<AnalysisSummary>('/admin/analysis/summary', { params }),

  getTopWorks: (params?: { top?: number; theme_id?: number; status?: string }) =>
    api.get<TopWorksResponse>('/admin/analysis/top-works', { params }),

  getReviewerProgress: (params?: { theme_id?: number; status?: string }) =>
    api.get<ReviewerProgressResponse>('/admin/analysis/reviewer-progress', { params }),

  getScoreDistribution: (type: 'histogram' | 'line' | 'boxplot', params?: { theme_id?: number; status?: string }) =>
    api.get<ScoreDistributionResponse>('/admin/analysis/score-distribution', { params: { ...params, type } }),

  getReviewerDetails: (params?: { theme_id?: number; status?: string }) =>
    api.get<ReviewerDetailsResponse>('/admin/analysis/reviewer-details', { params })
}