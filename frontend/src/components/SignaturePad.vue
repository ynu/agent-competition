<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'

const props = defineProps<{
  width?: number
  height?: number
  lineWidth?: number
  lineColor?: string
  backgroundColor?: string
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const isDrawing = ref(false)
const hasSignature = ref(false)
const signatureName = ref('')

// 存储签名的路径点
const signaturePaths = ref<{ x: number; y: number }[][]>([])
const currentPath = ref<{ x: number; y: number }[]>([])

const canvasWidth = computed(() => props.width || 400)
const canvasHeight = computed(() => props.height || 150)
const lineWidthValue = computed(() => props.lineWidth || 2)
const lineColorValue = computed(() => props.lineColor || '#000000')
const backgroundColorValue = computed(() => props.backgroundColor || '#fafafa')

let ctx: CanvasRenderingContext2D | null = null

onMounted(() => {
  initCanvas()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

function initCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return

  canvas.width = canvasWidth.value
  canvas.height = canvasHeight.value

  ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.fillStyle = backgroundColorValue.value
    ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
    ctx.strokeStyle = lineColorValue.value
    ctx.lineWidth = lineWidthValue.value
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'

    // Draw placeholder text
    ctx.fillStyle = '#ccc'
    ctx.font = '16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('请在此处签名', canvasWidth.value / 2, canvasHeight.value / 2 + 6)
  }

  canvas.addEventListener('touchstart', handleTouchStart, { passive: false })
  canvas.addEventListener('touchmove', handleTouchMove, { passive: false })
  canvas.addEventListener('touchend', handleTouchEnd)
}

function handleResize() {}

function getEventPos(e: MouseEvent | TouchEvent) {
  const canvas = canvasRef.value
  if (!canvas) return { x: 0, y: 0 }

  const rect = canvas.getBoundingClientRect()
  const scaleX = canvas.width / rect.width
  const scaleY = canvas.height / rect.height

  if ('touches' in e) {
    const touch = e.touches[0]
    return {
      x: (touch.clientX - rect.left) * scaleX,
      y: (touch.clientY - rect.top) * scaleY
    }
  } else {
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY
    }
  }
}

function handleMouseDown(e: MouseEvent) {
  startDrawing(e)
}

function handleMouseMove(e: MouseEvent) {
  draw(e)
}

function handleMouseUp() {
  stopDrawing()
}

function handleTouchStart(e: TouchEvent) {
  e.preventDefault()
  startDrawing(e)
}

function handleTouchMove(e: TouchEvent) {
  e.preventDefault()
  draw(e)
}

function handleTouchEnd() {
  stopDrawing()
}

function startDrawing(e: MouseEvent | TouchEvent) {
  if (!ctx) return

  // 开始新路径时，隐藏水印
  if (!hasSignature.value) {
    hidePlaceholder()
  }

  isDrawing.value = true
  currentPath.value = []
  const pos = getEventPos(e)
  currentPath.value.push(pos)
  ctx.beginPath()
  ctx.moveTo(pos.x, pos.y)
}

function draw(e: MouseEvent | TouchEvent) {
  if (!isDrawing.value || !ctx) return

  const pos = getEventPos(e)
  currentPath.value.push(pos)
  ctx.lineTo(pos.x, pos.y)
  ctx.stroke()
  hasSignature.value = true
}

function stopDrawing() {
  if (!isDrawing.value) return
  isDrawing.value = false
  if (currentPath.value.length > 0) {
    signaturePaths.value.push([...currentPath.value])
    currentPath.value = []
  }
}

function hidePlaceholder() {
  if (!ctx || !canvasRef.value) return
  // 重绘整个画布，用背景色覆盖水印
  ctx.fillStyle = backgroundColorValue.value
  ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
  ctx.strokeStyle = lineColorValue.value
  ctx.lineWidth = lineWidthValue.value
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  // 重绘之前的签名
  redrawSignature()
}

function redrawSignature() {
  if (!ctx) return
  for (const path of signaturePaths.value) {
    if (path.length < 2) continue
    ctx.beginPath()
    ctx.moveTo(path[0].x, path[0].y)
    for (let i = 1; i < path.length; i++) {
      ctx.lineTo(path[i].x, path[i].y)
    }
    ctx.stroke()
  }
}

function clearSignature() {
  if (!ctx || !canvasRef.value) return

  ctx.fillStyle = backgroundColorValue.value
  ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
  ctx.strokeStyle = lineColorValue.value
  ctx.lineWidth = lineWidthValue.value
  ctx.fillStyle = '#ccc'
  ctx.font = '16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('请在此处签名', canvasWidth.value / 2, canvasHeight.value / 2 + 6)

  hasSignature.value = false
  signatureName.value = ''
  signaturePaths.value = []
  currentPath.value = []
}

function getSignatureData() {
  if (!canvasRef.value || !hasSignature.value) return null

  // 创建新 canvas
  const tempCanvas = document.createElement('canvas')
  tempCanvas.width = canvasWidth.value
  tempCanvas.height = canvasHeight.value
  const tempCtx = tempCanvas.getContext('2d')

  if (tempCtx) {
    // 绘制背景
    tempCtx.fillStyle = backgroundColorValue.value
    tempCtx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
    tempCtx.strokeStyle = lineColorValue.value
    tempCtx.lineWidth = lineWidthValue.value
    tempCtx.lineCap = 'round'
    tempCtx.lineJoin = 'round'
    // 重绘所有签名路径（不包含水印）
    for (const path of signaturePaths.value) {
      if (path.length < 2) continue
      tempCtx.beginPath()
      tempCtx.moveTo(path[0].x, path[0].y)
      for (let i = 1; i < path.length; i++) {
        tempCtx.lineTo(path[i].x, path[i].y)
      }
      tempCtx.stroke()
    }
  }

  return tempCanvas.toDataURL('image/png')
}

// Expose for parent component
defineExpose({
  clearSignature,
  getSignatureData,
  getSignatureName: () => signatureName.value,
  hasSignature
})
</script>

<template>
  <div class="signature-pad">
    <!--
    <div class="signature-name-input">
      <label class="text-sm font-medium text-gray-700">签名人姓名</label>
      <input
        v-model="signatureName"
        type="text"
        class="w-full mt-1 px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm"
        placeholder="请输入签名人姓名"
      />
    </div>
    -->
    <div class="canvas-container">
      <canvas
        ref="canvasRef"
        class="signature-canvas"
        :style="{
          width: canvasWidth + 'px',
          height: canvasHeight + 'px'
        }"
        @mousedown="handleMouseDown"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
        @mouseleave="handleMouseUp"
      />
    </div>
    <div class="signature-actions">
      <button
        type="button"
        @click="clearSignature"
        class="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
      >
        清除
      </button>
    </div>
  </div>
</template>

<style scoped>
.signature-pad {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.signature-name-input {
  max-width: 300px;
}

.canvas-container {
  display: inline-block;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  overflow: hidden;
  background-color: v-bind(backgroundColorValue);
}

.signature-canvas {
  cursor: crosshair;
  touch-action: none;
}

.signature-actions {
  display: flex;
  justify-content: flex-end;
}
</style>