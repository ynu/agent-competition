<script setup lang="ts">
import { ref } from 'vue'
import FileSelector from './FileSelector.vue'
import { mediaApi } from '@/api'

const props = defineProps<{
  modelValue: string
  accept?: string
  placeholder?: string
  label?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const showFileSelector = ref(false)

function openSelector() {
  showFileSelector.value = true
}

function handleFileSelect(result: { path: string; url: string }) {
  // 使用 URL 作为值
  emit('update:modelValue', result.url)
  showFileSelector.value = false
}
</script>

<template>
  <div>
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1.5">{{ label }}</label>
    <div class="relative flex">
      <input
        :value="modelValue"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        :placeholder="placeholder"
        class="flex-1 px-4 py-2.5 border border-gray-200 rounded-l-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
      />
      <button
        type="button"
        @click="openSelector"
        class="px-4 py-2.5 bg-gray-100 border border-l-0 border-gray-200 rounded-r-xl hover:bg-gray-200 transition-colors flex items-center gap-2"
        title="选择文件"
      >
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
        </svg>
        <span class="text-sm text-gray-600">选择</span>
      </button>
    </div>

    <FileSelector
      :show="showFileSelector"
      mode="select"
      :accept="accept"
      @select="handleFileSelect"
      @close="showFileSelector = false"
    />
  </div>
</template>