<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import Dialog from './Dialog.vue'

const props = defineProps<{
  show: boolean
  title: string
  message: string
  placeholder?: string
  defaultValue?: string
  confirmText?: string
  cancelText?: string
}>()

const emit = defineEmits<{
  confirm: [value: string]
  cancel: []
  close: []
}>()

const inputValue = ref('')

watch(() => props.show, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
    nextTick(() => {
      inputValue.value = props.defaultValue || ''
    })
  } else {
    document.body.style.overflow = ''
  }
})

function handleConfirm() {
  emit('confirm', inputValue.value)
}
</script>

<template>
  <Dialog
    :show="show"
    :title="title"
    width="sm"
    @close="emit('close')"
  >
    <div class="p-6 space-y-4">
      <p class="text-gray-600 text-sm">{{ message }}</p>
      <input
        v-model="inputValue"
        type="text"
        :placeholder="placeholder"
        class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
        @keyup.enter="handleConfirm"
      />
    </div>
    <div class="px-6 py-4 bg-gray-50 flex justify-end gap-3">
      <button
        @click="emit('cancel')"
        class="px-5 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-100 font-medium text-gray-700 transition-colors"
      >
        {{ cancelText || '取消' }}
      </button>
      <button
        @click="handleConfirm"
        class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-medium transition-all shadow-lg shadow-blue-600/20"
      >
        {{ confirmText || '确定' }}
      </button>
    </div>
  </Dialog>
</template>