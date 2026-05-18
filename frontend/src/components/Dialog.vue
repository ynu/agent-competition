<script setup lang="ts">
import { watch, ref, computed } from 'vue'

const props = defineProps<{
  show?: boolean
  modelValue?: boolean
  title?: string
  subtitle?: string
  width?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl' | 'full' | '90vw'
  maxHeight?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '70vh' | '80vh' | '90vh' | '95vh'
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  close: []
}>()

const isOpen = computed(() => props.show ?? props.modelValue ?? false)

const emitClose = () => {
  emit('update:modelValue', false)
  emit('close')
}

const isMaximized = ref(false)

const widthClasses: Record<string, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  '2xl': 'max-w-2xl',
  '3xl': 'max-w-3xl',
  '4xl': 'max-w-4xl',
  '5xl': 'max-w-5xl',
  '6xl': 'max-w-6xl',
  'full': 'max-w-full',
  '90vw': 'max-w-[90vw]'
}

const maxHeightClasses: Record<string, string> = {
  sm: 'max-h-[40vh]',
  md: 'max-h-[50vh]',
  lg: 'max-h-[60vh]',
  xl: 'max-h-[70vh]',
  '2xl': 'max-h-[75vh]',
  '3xl': 'max-h-[80vh]',
  '4xl': 'max-h-[85vh]',
  '70vh': 'max-h-[70vh]',
  '80vh': 'max-h-[80vh]',
  '90vh': 'max-h-[90vh]',
  '95vh': 'max-h-[95vh]'
}

function toggleMaximize() {
  isMaximized.value = !isMaximized.value
}

watch(isOpen, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
    isMaximized.value = false
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="emitClose">
        <!-- Backdrop with shadow effect -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>

        <!-- Dialog container -->
        <div
          class="relative bg-white rounded-2xl shadow-2xl w-full overflow-hidden flex flex-col z-10 transition-all duration-300"
          :class="[widthClasses[width || 'md'], isMaximized ? '!max-w-[95vw] !max-h-[95vh] !h-[95vh]' : maxHeightClasses[maxHeight || '2xl']]"
        >
          <!-- Header -->
          <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 flex justify-between items-center flex-shrink-0">
            <div>
              <h3 class="text-lg font-semibold text-white">{{ title || '' }}</h3>
              <p v-if="subtitle" class="text-blue-100 text-sm">{{ subtitle }}</p>
            </div>
            <div class="flex items-center gap-1">
              <button @click="toggleMaximize" class="text-white/80 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition-colors" :title="isMaximized ? '还原' : '最大化'">
                <svg v-if="isMaximized" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25"/>
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5"/>
                </svg>
              </button>
              <button @click="emitClose" class="text-white/80 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition-colors">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-y-auto" :class="isMaximized ? '!max-h-[calc(95vh-80px)]' : ''">
            <slot></slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-enter-active,
.dialog-leave-active {
  transition: all 0.2s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-enter-from > div,
.dialog-leave-to > div {
  transform: scale(0.95);
}

.dialog-enter-to > div,
.dialog-leave-from > div {
  transform: scale(1);
}
</style>