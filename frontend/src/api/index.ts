import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // Let axios set the Content-Type for FormData automatically
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      console.log('API 401 error, logging out')
      try {
        const authStore = useAuthStore()
        authStore.logout()
      } catch (e) {
        console.log('Auth store error:', e)
        localStorage.removeItem('token')
      }
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// Auth APIs
export const authApi = {
  login: (data: { username: string; password: string }) => api.post('/auth/login', data),
  unifiedAuth: (data: { code?: string }) => api.post('/auth/unified-auth', data),
  logout: () => api.post<{ message: string; cas_logout_url?: string }>('/auth/logout'),
  me: () => api.get('/auth/me')
}

// User APIs
export const userApi = {
  list: (params?: { page?: number; page_size?: number; role?: string; keyword?: string }) =>
    api.get('/users', { params }),
  get: (id: number) => api.get(`/users/${id}`),
  create: (data: any) => api.post('/users', data),
  update: (id: number, data: any) => api.put(`/users/${id}`, data),
  delete: (id: number) => api.delete(`/users/${id}`),
  resetPassword: (id: number, data: { new_password: string }) => api.post(`/users/${id}/reset-password`, data)
}

// Team APIs
export const teamApi = {
  list: (params?: { page?: number; page_size?: number; status?: string; keyword?: string }) =>
    api.get('/teams', { params }),
  get: (id: number) => api.get(`/teams/${id}`),
  create: (data: any) => api.post('/teams', data),
  update: (id: number, data: any) => api.put(`/teams/${id}`, data),
  delete: (id: number) => api.delete(`/teams/${id}`),
  join: (id: number, data: { student_id: string; name: string }) => api.post(`/teams/${id}/join`, data),
  audit: (id: number, data: { status: string }) => api.put(`/teams/${id}/audit`, data),
  myTeam: () => api.get('/teams/my/team')
}

// Work APIs
export const workApi = {
  list: (params?: { page?: number; page_size?: number; status?: string; team_name?: string; keyword?: string }) =>
    api.get('/works', { params }),
  get: (id: number) => api.get(`/works/${id}`),
  create: (data: any) => api.post('/works', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  update: (id: number, data: any) => api.put(`/works/${id}`, data),
  delete: (id: number) => api.delete(`/works/${id}`),
  vote: (id: number) => api.post(`/works/${id}/vote`, { work_id: id }),
  myWorks: (params?: { page?: number; page_size?: number }) => api.get('/works/my/works', { params }),
  // 版权协议
  checkCopyrightAgreement: () => api.get('/works/copyright-agreement/check'),
  signCopyrightAgreement: (data: { work_id?: number; signature_data: string; signature_name?: string }) =>
    api.post('/works/copyright-agreement', data)
}

// Review APIs
export const reviewApi = {
  list: (params?: { page?: number; page_size?: number; team_name?: string; work_name?: string; is_scored?: boolean }) =>
    api.get('/reviews', { params }),
  create: (data: { work_id: number; score?: number; comment?: string }) => api.post('/reviews', data),
  update: (id: number, data: { score?: number; comment?: string }) => api.put(`/reviews/${id}`, data),
  myReviews: (params?: { page?: number; page_size?: number }) => api.get('/reviews/my-reviews', { params })
}

// Content APIs
export const contentApi = {
  list: (params?: { page?: number; page_size?: number; type?: string; parent_id?: number; is_published?: boolean }) =>
    api.get('/contents', { params }),
  tree: () => api.get('/contents/tree'),
  getBySlug: (slug: string) => api.get(`/contents/slug/${slug}`),
  get: (id: number) => api.get(`/contents/${id}`),
  create: (data: any) => api.post('/contents', data),
  update: (id: number, data: any) => api.put(`/contents/${id}`, data),
  delete: (id: number) => api.delete(`/contents/${id}`),
  generateStatic: (id: number) => api.post(`/contents/${id}/generate-static`),
  // 文章/新闻 API
  articles: (params?: { page?: number; page_size?: number; keyword?: string }) =>
    api.get('/contents/articles', { params }),
  latestArticles: (limit?: number) => api.get('/contents/articles/latest', { params: { limit } })
}

// Settings APIs
export const settingsApi = {
  list: (params?: { page?: number; page_size?: number; keyword?: string }) =>
    api.get('/settings', { params }),
  get: (key: string) => api.get(`/settings/${key}`),
  update: (key: string, data: { value?: string; description?: string }) => api.put(`/settings/${key}`, data),
  init: () => api.post('/settings/init'),
  getThemes: () => api.get('/settings/themes/list')
}

// Log APIs
export const logApi = {
  list: (params?: { page?: number; page_size?: number; action?: string; resource?: string; user_id?: number }) =>
    api.get('/logs', { params }),
  actions: () => api.get('/logs/actions'),
  resources: () => api.get('/logs/resources'),
  statistics: (days?: number) => api.get('/logs/statistics', { params: { days } })
}

// Agent Center APIs
export const agentCenterApi = {
  listCategories: () => api.get('/agent-center/categories'),
  listAgents: (params?: { page?: number; page_size?: number; category?: string; keyword?: string; sort?: string }) =>
    api.get('/agent-center', { params }),
  getImageUrl: (imagePath: string) => {
    const baseUrl = 'https://agent.ynu.edu.cn/api/proxy/down'
    const params = new URLSearchParams({
      Action: 'Download',
      Path: imagePath,
      IsAnonymous: 'true'
    })
    return `${baseUrl}?${params.toString()}`
  }
}

// Materials APIs (课程资料)
export const materialsApi = {
  list: (params?: { page?: number; page_size?: number; keyword?: string }) =>
    api.get('/contents/materials', { params }),
  get: (id: number) => api.get(`/contents/${id}`),
  getBySlug: (slug: string) => api.get(`/contents/slug/${slug}`)
}

// Media APIs (媒体管理)
export const mediaApi = {
  listDirs: () => api.get('/media/dirs'),
  createDir: (data: { name: string; parent?: string }) => api.post('/media/dirs', data),
  deleteDir: (path: string) => api.delete(`/media/dirs?path=${encodeURIComponent(path)}`),
  listFiles: (params?: { path?: string }) => api.get('/media/files', { params }),
  upload: (data: FormData, onProgress?: (progressEvent: any) => void) =>
    api.post('/media/upload', data, { onUploadProgress: onProgress }),
  deleteFile: (path: string) => api.delete(`/media/${encodeURIComponent(path)}`),
  moveFile: (data: { from_path: string; to_path: string }) => api.post('/media/move', data),
  getPreviewUrl: (path: string) => `/media/${path}`
}