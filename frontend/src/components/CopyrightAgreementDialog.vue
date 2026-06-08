<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { workApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import SignaturePad from './SignaturePad.vue'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'

const props = defineProps<{
  visible: boolean
  workId?: number
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'agreed'): void
}>()

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true
})

const authStore = useAuthStore()
const agreementContent = ref('')
const renderedAgreement = computed(() => md.render(agreementContent.value || ''))
const loading = ref(false)
const checking = ref(true)
const alreadySigned = ref(false)
const lastSignedAt = ref<string | null>(null)
const signaturePadRef = ref<InstanceType<typeof SignaturePad> | null>(null)
const hasReadAgreement = ref(false)

watch(() => props.visible, async (val) => {
  if (val) {
    await checkAgreementStatus()
  }
})

async function checkAgreementStatus() {
  checking.value = true
  try {
    const res = await workApi.checkCopyrightAgreement()
    agreementContent.value = res.data.agreement_content || ''
    alreadySigned.value = res.data.has_agreed
    lastSignedAt.value = res.data.last_signed_at
  } catch (e: any) {
    console.error('检查版权协议状态失败:', e)
    ElMessage.error('检查版权协议状态失败')
  } finally {
    checking.value = false
  }
}

function handleClose() {
  emit('update:visible', false)
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

async function handleConfirmSign() {
  const signatureData = signaturePadRef.value?.getSignatureData()
  const signatureName = signaturePadRef.value?.getSignatureName()

  if (!signatureData) {
    ElMessage.warning('请先在下方签名区域签名')
    return
  }

  if (!hasReadAgreement.value) {
    ElMessage.warning('请先阅读并同意版权协议')
    return
  }

  loading.value = true
  try {
    await workApi.signCopyrightAgreement({
      work_id: props.workId,
      signature_data: signatureData,
      signature_name: signatureName || authStore.user?.nickname || authStore.user?.username || '未知名'
    })
    ElMessage.success('版权协议签署成功')
    emit('agreed')
    handleClose()
  } catch (e: any) {
    const detail = e.response?.data?.detail || '签署失败'
    if (detail.includes('已经签署过') || detail.includes('已经签约')) {
      alreadySigned.value = true
      ElMessage.info('您已经签署过版权协议')
    } else {
      ElMessage.error(detail)
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    title="版权协议签署"
    width="700px"
    :close-on-click-modal="false"
    @update:model-value="emit('update:visible', $event)"
    @close="handleClose"
  >
    <div v-if="checking" class="flex items-center justify-center py-8">
      <div class="inline-block w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <span class="ml-2 text-gray-500">加载中...</span>
    </div>

    <div v-else>
      <!-- 已签署状态 -->
      <div v-if="alreadySigned" class="text-center py-8">
        <div class="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">您已签署版权协议</h3>
        <p class="text-gray-500 text-sm">
          上次签署时间：{{ formatDate(lastSignedAt) }}
        </p>
        <p class="text-gray-400 text-xs mt-4">
          无需重复签署，可直接提交作品
        </p>
      </div>

      <!-- 签署协议 -->
      <div v-else class="space-y-4">
        <!-- 协议内容 -->
        <div class="agreement-content bg-gray-50 rounded-lg p-4 max-h-[360px] overflow-y-auto">
          <h4 class="text-base font-medium text-gray-800 mb-3 text-center">参赛作品版权声明</h4>
          <div class="text-sm text-gray-600 markdown-body" v-html="renderedAgreement"></div>
        </div>

        <!-- 同意确认 -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <label class="flex items-start gap-3 cursor-pointer">
            <input
              v-model="hasReadAgreement"
              type="checkbox"
              class="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700">
              我已阅读并理解上述版权协议内容，同意遵守相关规定，并对提交的作品负责。
            </span>
          </label>
        </div>

        <!-- 签名区域 -->
        <div class="border border-gray-200 rounded-lg p-4 bg-white">
          <h5 class="text-sm font-medium text-gray-700 mb-3">
            请在下方签名确认 <span class="text-red-500">*</span>
          </h5>
          <div class="flex justify-center">
            <SignaturePad
              ref="signaturePadRef"
              :width="620"
              :height="160"
              line-color="#1f2937"
              background-color="#fafafa"
            />
          </div>
          <p class="text-xs text-gray-400 mt-2 text-center">
            提示：请使用鼠标或触屏在签名区域内签名，然后填写签名人姓名
          </p>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          v-if="!alreadySigned"
          type="primary"
          :loading="loading"
          :disabled="!hasReadAgreement"
          @click="handleConfirmSign"
        >
          确认签署
        </el-button>
        <el-button
          v-else
          type="primary"
          @click="handleClose"
        >
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.agreement-content::-webkit-scrollbar {
  width: 6px;
}

.agreement-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.agreement-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.markdown-body {
  line-height: 1.8;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  font-weight: 600;
  margin-top: 1em;
  margin-bottom: 0.5em;
}

.markdown-body :deep(p) {
  margin: 0.5em 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  list-style: revert !important;
  padding-left: 1.5em;
  margin: 0.5em 0;
}

.markdown-body :deep(li) {
  margin: 0.25em 0;
  list-style: revert !important;
}

.markdown-body :deep(strong) {
  font-weight: 600;
}

.markdown-body :deep(a) {
  color: #3b82f6;
  text-decoration: underline;
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 1em 0;
}
</style>