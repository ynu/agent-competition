<script setup lang="ts">
import { ref, watch } from 'vue'
import Dialog from './Dialog.vue'

const props = defineProps<{
  modelValue?: boolean
  show?: boolean
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'danger' | 'warning' | 'info'
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
  cancel: []
  close: []
}>()

const isOpen = ref(false)

watch(() => [props.show, props.modelValue], ([show, val]) => {
  isOpen.value = show ?? val ?? false
}, { immediate: true })

watch(isOpen, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

const typeColors = {
  danger: 'from-red-600 to-red-700',
  warning: 'from-amber-500 to-orange-600',
  info: 'from-blue-600 to-blue-700'
}

const handleConfirm = () => {
  emit('update:modelValue', false)
  emit('confirm')
}

const handleCancel = () => {
  emit('update:modelValue', false)
  emit('cancel')
  emit('close')
}
</script>

<template>
  <Dialog
    :modelValue="isOpen"
    :title="title || '确认操作'"
    width="sm"
    @update:modelValue="(v) => { isOpen = v; if (!v) emit('close') }"
  >
    <div class="p-6">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
          :class="type === 'danger' ? 'bg-red-100' : type === 'warning' ? 'bg-amber-100' : 'bg-blue-100'">
          <svg v-if="type === 'danger'" class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
          <svg v-else-if="type === 'warning'" class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <svg v-else class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <p class="text-gray-600 text-sm leading-relaxed">{{ message }}</p>
      </div>
    </div>
    <div class="px-6 py-4 bg-gray-50 flex justify-end gap-3">
      <button
        @click="handleCancel"
        class="px-5 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-100 font-medium text-gray-700 transition-colors"
      >
        {{ cancelText || '取消' }}
      </button>
      <button
        @click="handleConfirm"
        :class="[
          'px-5 py-2.5 text-white rounded-xl font-medium transition-all shadow-lg',
          'bg-gradient-to-r ' + (typeColors[type || 'info'])
        ]"
      >
        {{ confirmText || '确定' }}
      </button>
    </div>
  </Dialog>
</template>