<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Dialog from './Dialog.vue'
import { mediaApi } from '@/api'
import { useNotification } from '@/composables/useNotification'

interface DirItem {
  name: string
  path: string
  children?: DirItem[]
}

interface FileItem {
  name: string
  path: string
  size: number
  is_dir: boolean
  modified: string
  extension?: string
}

const props = defineProps<{
  show: boolean
  mode?: 'insert' | 'select'
  accept?: string
  initialPath?: string
}>()

const emit = defineEmits<{
  select: [{ path: string; url: string }]
  close: []
}>()

const { success, error } = useNotification()

const dirs = ref<DirItem[]>([])
const files = ref<FileItem[]>([])
const currentPath = ref('')
const loading = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const viewMode = ref<'list' | 'grid'>('list')
const expandedDirs = ref<Set<string>>(new Set())
const selectedFile = ref<FileItem | null>(null)
const previewFile = ref<FileItem | null>(null)
const showPreview = ref(false)
const showCreateDir = ref(false)
const newDirName = ref('')
const dragOver = ref(false)
const contextMenu = ref<{ x: number; y: number; file: FileItem } | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const currentDirPath = computed(() => currentPath.value || '/')

const fileIconMap: Record<string, string> = {
  pdf: 'pdf',
  jpg: 'image',
  jpeg: 'image',
  png: 'image',
  gif: 'image',
  svg: 'image',
  webp: 'image',
  mp4: 'video',
  webm: 'video',
  mp3: 'audio',
  wav: 'audio',
  m4a: 'audio',
  doc: 'document',
  docx: 'document',
  zip: 'archive'
}

function getFileIcon(ext?: string): string {
  if (!ext) return 'folder'
  return fileIconMap[ext.toLowerCase()] || 'file'
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function getAcceptTypes(): string {
  if (props.accept) return props.accept
  return '*'
}

watch(() => props.show, async (val) => {
  if (val) {
    currentPath.value = props.initialPath || ''
    await loadDirs()
    await loadFiles()
    selectedFile.value = null
    showCreateDir.value = false
    contextMenu.value = null
  }
})

async function loadDirs() {
  try {
    const res = await mediaApi.listDirs()
    dirs.value = res.data.items || []
  } catch (e: any) {
    error('加载目录失败', e.response?.data?.detail || '未知错误')
  }
}

async function loadFiles() {
  loading.value = true
  try {
    const res = await mediaApi.listFiles({ path: currentPath.value || undefined })
    files.value = res.data.items || []
  } catch (e: any) {
    error('加载文件失败', e.response?.data?.detail || '未知错误')
  } finally {
    loading.value = false
  }
}

function navigateToDir(path: string) {
  currentPath.value = path
  selectedFile.value = null
  loadFiles()
}

function navigateUp() {
  const parts = currentPath.value.split('/').filter(Boolean)
  parts.pop()
  currentPath.value = parts.join('/')
  selectedFile.value = null
  loadFiles()
}

function selectFile(file: FileItem) {
  if (file.is_dir) {
    navigateToDir(file.path)
  } else {
    selectedFile.value = file
  }
}

function confirmSelection() {
  if (!selectedFile.value) return
  const url = mediaApi.getPreviewUrl(selectedFile.value.path)
  emit('select', { path: selectedFile.value.path, url })
  emit('close')
}

function handleDoubleClick(file: FileItem) {
  if (file.is_dir) {
    navigateToDir(file.path)
  } else {
    openPreview(file)
  }
}

function openPreview(file: FileItem) {
  previewFile.value = file
  showPreview.value = true
}

function closePreview() {
  showPreview.value = false
  previewFile.value = null
}

function handleContextMenu(e: MouseEvent, file: FileItem) {
  e.preventDefault()
  contextMenu.value = { x: e.clientX, y: e.clientY, file }
}

function closeContextMenu() {
  contextMenu.value = null
}

async function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  await uploadFiles(Array.from(input.files))
  input.value = ''
}

async function handleDrop(e: DragEvent) {
  dragOver.value = false
  e.preventDefault()
  if (!e.dataTransfer?.files.length) return
  await uploadFiles(Array.from(e.dataTransfer.files))
}

function handleDragOver(e: DragEvent) {
  e.preventDefault()
  dragOver.value = true
}

function handleDragLeave() {
  dragOver.value = false
}

async function uploadFiles(filesToUpload: File[]) {
  uploading.value = true
  uploadProgress.value = 0

  for (let i = 0; i < filesToUpload.length; i++) {
    const file = filesToUpload[i]
    const formData = new FormData()
    formData.append('file', file)
    if (currentPath.value) {
      formData.append('path', currentPath.value)
    }

    try {
      await mediaApi.upload(formData, (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      })
    } catch (e: any) {
      error('上传失败', `${file.name}: ${e.response?.data?.detail || '未知错误'}`)
    }
  }

  uploading.value = false
  uploadProgress.value = 0
  await loadFiles()
  success('上传成功')
}

async function createDirectory() {
  if (!newDirName.value.trim()) return

  try {
    await mediaApi.createDir({
      name: newDirName.value.trim(),
      parent: currentPath.value || undefined
    })
    showCreateDir.value = false
    newDirName.value = ''
    await loadDirs()
    await loadFiles()
    success('目录创建成功')
  } catch (e: any) {
    error('创建失败', e.response?.data?.detail || '未知错误')
  }
}

async function deleteFile(file: FileItem) {
  closeContextMenu()
  if (!confirm(`确定删除 ${file.name} 吗？`)) return

  try {
    await mediaApi.deleteFile(file.path)
    await loadFiles()
    if (selectedFile.value?.path === file.path) {
      selectedFile.value = null
    }
    success('删除成功')
  } catch (e: any) {
    error('删除失败', e.response?.data?.detail || '未知错误')
  }
}

function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.context-menu')) {
    closeContextMenu()
  }
}

function isPreviewable(file: FileItem): boolean {
  if (!file.extension) return false
  const previewable = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'pdf', 'mp4', 'webm', 'mp3', 'wav']
  return previewable.includes(file.extension.toLowerCase())
}
</script>

<template>
  <Dialog
    :show="show"
    :title="mode === 'insert' ? '选择文件' : '选择文件'"
    width="90vw"
    maxHeight="90vh"
    @close="emit('close')"
  >
    <div class="flex h-[70vh]" @click="handleClickOutside">
      <!-- Left: Directory Tree -->
      <div class="w-56 border-r border-gray-200 bg-gray-50 overflow-y-auto flex-shrink-0">
        <div class="p-3 border-b border-gray-200 bg-white sticky top-0 z-10">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">目录</span>
            <button
              @click="showCreateDir = true"
              class="p-1 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
              title="创建目录"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
              </svg>
            </button>
          </div>
          <div v-if="showCreateDir" class="flex gap-1">
            <input
              v-model="newDirName"
              @keyup.enter="createDirectory"
              placeholder="目录名"
              class="flex-1 px-2 py-1 text-sm border border-gray-200 rounded focus:outline-none focus:border-blue-500"
            />
            <button @click="createDirectory" class="px-2 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">创建</button>
          </div>
        </div>
        <div class="p-2">
          <button
            @click="navigateToDir('')"
            class="w-full text-left px-2 py-1.5 text-sm rounded hover:bg-blue-50 flex items-center gap-2"
            :class="currentPath === '' ? 'bg-blue-100 text-blue-700' : 'text-gray-700'"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
            全部文件
          </button>
          <template v-for="dir in dirs" :key="dir.path">
            <button
              @click="navigateToDir(dir.path)"
              class="w-full text-left px-2 py-1.5 text-sm rounded hover:bg-blue-50 flex items-center gap-2"
              :class="currentPath === dir.path ? 'bg-blue-100 text-blue-700' : 'text-gray-700'"
            >
              <svg class="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/>
              </svg>
              {{ dir.name }}
            </button>
          </template>
        </div>
      </div>

      <!-- Right: File List -->
      <div class="flex-1 flex flex-col min-w-0">
        <!-- Toolbar -->
        <div class="flex items-center justify-between p-3 border-b border-gray-200 bg-white">
          <div class="flex items-center gap-2">
            <button
              v-if="currentPath"
              @click="navigateUp"
              class="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
              title="返回上级"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
              </svg>
            </button>
            <span class="text-sm text-gray-600">
              {{ currentPath || '根目录' }}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="viewMode = 'list'"
              class="p-1.5 rounded"
              :class="viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-100'"
              title="列表视图"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"/>
              </svg>
            </button>
            <button
              @click="viewMode = 'grid'"
              class="p-1.5 rounded"
              :class="viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-100'"
              title="缩略图视图"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
              </svg>
            </button>
            <input
              ref="fileInputRef"
              type="file"
              :accept="getAcceptTypes()"
              multiple
              class="hidden"
              @change="handleFileSelect"
            />
            <button
              @click="fileInputRef?.click()"
              class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
              </svg>
              上传
            </button>
          </div>
        </div>

        <!-- Upload Progress -->
        <div v-if="uploading" class="px-4 py-2 bg-blue-50 border-b border-blue-100 flex items-center gap-3">
          <div class="relative w-8 h-8">
            <svg class="w-8 h-8 transform -rotate-90">
              <circle cx="16" cy="16" r="14" stroke="#e5e7eb" stroke-width="3" fill="none"/>
              <circle cx="16" cy="16" r="14" stroke="#3b82f6" stroke-width="3" fill="none"
                :stroke-dasharray="`${uploadProgress * 0.88} 88`"/>
            </svg>
            <span class="absolute inset-0 flex items-center justify-center text-xs font-medium text-blue-600">{{ uploadProgress }}%</span>
          </div>
          <span class="text-sm text-blue-700">正在上传...</span>
        </div>

        <!-- Drop Zone -->
        <div
          class="flex-1 overflow-y-auto p-4"
          :class="{ 'bg-blue-50 border-2 border-dashed border-blue-300': dragOver }"
          @drop="handleDrop"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
        >
          <!-- Loading -->
          <div v-if="loading" class="flex items-center justify-center h-full">
            <div class="flex items-center gap-2 text-gray-500">
              <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              加载中...
            </div>
          </div>

          <!-- Empty -->
          <div v-else-if="files.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400">
            <svg class="w-16 h-16 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
            </svg>
            <p>文件夹为空或拖拽文件到此处上传</p>
          </div>

          <!-- List View -->
          <table v-else-if="viewMode === 'list'" class="w-full">
            <thead>
              <tr class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b">
                <th class="pb-2 pl-2">名称</th>
                <th class="pb-2">大小</th>
                <th class="pb-2">修改时间</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="file in files"
                :key="file.path"
                class="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
                :class="{ 'bg-blue-50': selectedFile?.path === file.path }"
                @click="selectFile(file)"
                @dblclick="handleDoubleClick(file)"
                @contextmenu="handleContextMenu($event, file)"
              >
                <td class="py-2 pl-2 flex items-center gap-2">
                  <svg v-if="file.is_dir" class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/>
                  </svg>
                  <svg v-else class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                  </svg>
                  <span class="text-sm text-gray-700">{{ file.name }}</span>
                </td>
                <td class="py-2 text-sm text-gray-500">
                  {{ file.is_dir ? '-' : formatSize(file.size) }}
                </td>
                <td class="py-2 text-sm text-gray-500">
                  {{ formatDate(file.modified) }}
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Grid View -->
          <div v-else class="grid grid-cols-4 gap-4">
            <div
              v-for="file in files"
              :key="file.path"
              class="p-3 border border-gray-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 cursor-pointer transition-all"
              :class="{ 'border-blue-500 bg-blue-50': selectedFile?.path === file.path }"
              @click="selectFile(file)"
              @dblclick="handleDoubleClick(file)"
              @contextmenu="handleContextMenu($event, file)"
            >
              <div class="aspect-square flex items-center justify-center mb-2">
                <svg v-if="file.is_dir" class="w-16 h-16 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/>
                </svg>
                <svg v-else class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
              </div>
              <p class="text-sm text-gray-700 text-center truncate">{{ file.name }}</p>
              <p class="text-xs text-gray-400 text-center">{{ file.is_dir ? '文件夹' : formatSize(file.size) }}</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between p-3 border-t border-gray-200 bg-gray-50">
          <div class="text-sm text-gray-500">
            {{ files.filter(f => !f.is_dir).length }} 个文件
          </div>
          <div class="flex gap-2">
            <button
              @click="emit('close')"
              class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
            >
              取消
            </button>
            <button
              @click="confirmSelection"
              :disabled="!selectedFile"
              class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ mode === 'insert' ? '插入' : '选择' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <Teleport to="body">
      <div v-if="showPreview && previewFile" class="fixed inset-0 z-[100] bg-black/80 flex items-center justify-center p-4" @click.self="closePreview">
        <div class="relative max-w-5xl max-h-[90vh] w-full bg-white rounded-xl overflow-hidden">
          <button @click="closePreview" class="absolute top-3 right-3 z-10 p-2 bg-black/50 text-white rounded-full hover:bg-black/70">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
          <div class="p-4 bg-gray-100 border-b">
            <p class="font-medium">{{ previewFile.name }}</p>
          </div>
          <div class="max-h-[70vh] overflow-auto flex items-center justify-center bg-gray-50">
            <img
              v-if="['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(previewFile.extension || '')"
              :src="mediaApi.getPreviewUrl(previewFile.path)"
              :alt="previewFile.name"
              class="max-w-full max-h-[65vh] object-contain"
            />
            <video
              v-else-if="['mp4', 'webm'].includes(previewFile.extension || '')"
              :src="mediaApi.getPreviewUrl(previewFile.path)"
              controls
              class="max-w-full max-h-[65vh]"
            />
            <audio
              v-else-if="['mp3', 'wav', 'm4a'].includes(previewFile.extension || '')"
              :src="mediaApi.getPreviewUrl(previewFile.path)"
              controls
              class="w-full max-w-lg"
            />
            <iframe
              v-else-if="previewFile.extension === 'pdf'"
              :src="`/pdfjs/web/viewer.html?file=${encodeURIComponent(mediaApi.getPreviewUrl(previewFile.path))}`"
              class="w-full h-[65vh]"
            />
            <div v-else class="text-gray-500 p-8 text-center">
              <p>该文件类型不支持预览</p>
              <a :href="mediaApi.getPreviewUrl(previewFile.path)" class="text-blue-600 hover:underline mt-2 inline-block">下载查看</a>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Context Menu -->
    <Teleport to="body">
      <div
        v-if="contextMenu"
        class="context-menu fixed z-[100] bg-white rounded-lg shadow-xl border border-gray-200 py-1 min-w-[150px]"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      >
        <button
          v-if="isPreviewable(contextMenu.file)"
          @click="openPreview(contextMenu.file); closeContextMenu()"
          class="w-full px-4 py-2 text-sm text-left hover:bg-gray-100 flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
          </svg>
          预览
        </button>
        <button
          @click="selectedFile = contextMenu.file; confirmSelection(); closeContextMenu()"
          class="w-full px-4 py-2 text-sm text-left hover:bg-gray-100 flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          选择
        </button>
        <hr class="my-1 border-gray-200" />
        <button
          @click="deleteFile(contextMenu.file)"
          class="w-full px-4 py-2 text-sm text-left hover:bg-red-50 text-red-600 flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
          删除
        </button>
      </div>
    </Teleport>
  </Dialog>
</template>