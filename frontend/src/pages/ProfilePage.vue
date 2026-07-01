<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { passkeyApi, type PasskeyCredential, type PasskeyConfig } from '@/api/passkey'

const authStore = useAuthStore()

const passkeyConfig = ref<PasskeyConfig>({ enabled: false, require_for_roles: [] })
const credentials = ref<PasskeyCredential[]>([])
const registering = ref(false)
const error = ref('')
const success = ref('')

// WebAuthn 支持检测
const webAuthnSupported = !!(navigator.credentials && typeof navigator.credentials.create === 'function' && typeof navigator.credentials.get === 'function')

// 将 base64url 字符串转换为 ArrayBuffer
function base64urlToBuffer(base64url: string): ArrayBuffer {
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/')
  const binary = atob(base64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return bytes.buffer
}

// 将 ArrayBuffer 转换为 base64url 字符串
function bufferToBase64url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}

// 将 PublicKeyCredential 转换为 JSON 格式
function publicKeyCredentialToJson(credential: PublicKeyCredential): any {
  const response = credential.response as AuthenticatorAttestationResponse

  return {
    id: credential.id,
    rawId: bufferToBase64url(credential.rawId),
    type: credential.type,
    response: {
      attestationObject: bufferToBase64url(response.attestationObject),
      clientDataJSON: bufferToBase64url(response.clientDataJSON),
      transports: response.transports || []
    }
  }
}

onMounted(async () => {
  await loadConfig()
  await loadCredentials()
})

async function loadConfig() {
  try {
    const res = await passkeyApi.getConfig()
    passkeyConfig.value = res.data
  } catch (e) {
    console.error('Failed to load passkey config:', e)
  }
}

async function loadCredentials() {
  try {
    const res = await passkeyApi.getMyCredentials()
    credentials.value = res.data
  } catch (e) {
    console.error('Failed to load credentials:', e)
  }
}

async function handleRegisterPasskey() {
  if (!webAuthnSupported) {
    error.value = '您的浏览器不支持通行密钥'
    return
  }

  error.value = ''
  success.value = ''
  registering.value = true

  try {
    // 获取注册选项
    const optionsRes = await passkeyApi.getRegisterOptions()
    const optionsJson = JSON.parse(optionsRes.data.options)

    // 将 base64url 字符串转换回 ArrayBuffer
    const publicKeyOptions = {
      rp: optionsJson.rp,
      user: {
        id: base64urlToBuffer(optionsJson.user.id),
        name: optionsJson.user.name,
        displayName: optionsJson.user.displayName
      },
      challenge: base64urlToBuffer(optionsJson.challenge),
      pubKeyCredParams: optionsJson.pubKeyCredParams,
      timeout: optionsJson.timeout,
      attestation: optionsJson.attestation,
      excludeCredentials: (optionsJson.excludeCredentials || []).map((cred: any) => ({
        type: cred.type,
        id: base64urlToBuffer(cred.id),
        transports: cred.transports
      }))
    }

    // 调用 WebAuthn 创建凭证
    const credential = await navigator.credentials.create({
      publicKey: publicKeyOptions
    })

    if (!credential) {
      error.value = '注册已取消'
      registering.value = false
      return
    }

    // 将凭证转换为 JSON 格式
    const credentialJson = publicKeyCredentialToJson(credential)

    // 验证注册
    await passkeyApi.verifyRegistration({
      options: JSON.stringify(credentialJson),
      device_name: getDeviceName()
    })

    success.value = '通行密钥注册成功'
    await loadCredentials()
  } catch (e: any) {
    console.error('Passkey registration error:', e)
    error.value = e.response?.data?.detail || e.message || '注册失败，请重试'
  } finally {
    registering.value = false
  }
}

async function handleDeleteCredential(id: number) {
  if (!confirm('确定要删除这个通行密钥吗？')) return

  try {
    await passkeyApi.deleteCredential(id)
    success.value = '通行密钥已删除'
    await loadCredentials()
  } catch (e: any) {
    error.value = e.response?.data?.detail || '删除失败'
  }
}

async function handleRenameCredential(id: number, currentName: string) {
  const newName = prompt('请输入新的设备名称：', currentName)
  if (!newName || newName === currentName) return

  try {
    await passkeyApi.renameCredential(id, newName)
    success.value = '设备名称已更新'
    await loadCredentials()
  } catch (e: any) {
    error.value = e.response?.data?.detail || '重命名失败'
  }
}

function getDeviceName(): string {
  const ua = navigator.userAgent
  if (ua.includes('iPhone')) return `iPhone ${ua.match(/iPhone\s+(\d+)/)?.[1] || ''}`
  if (ua.includes('iPad')) return `iPad ${ua.match(/iPad\s+(\d+)/)?.[1] || ''}`
  if (ua.includes('Android')) return 'Android Device'
  if (ua.includes('Mac OS')) return 'Mac'
  if (ua.includes('Windows')) return 'Windows PC'
  if (ua.includes('Linux')) return 'Linux PC'
  return 'Unknown Device'
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '从未使用'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<template>
  <div class="max-w-2xl mx-auto p-6">
    <h1 class="text-2xl font-bold mb-6">个人设置</h1>

    <!-- Alerts -->
    <div v-if="error" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
      {{ error }}
    </div>
    <div v-if="success" class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
      {{ success }}
    </div>

    <!-- Passkey Section -->
    <div v-if="passkeyConfig.enabled" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">通行密钥</h2>
        <span class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">已启用</span>
      </div>

      <p class="text-sm text-gray-500 mb-4">
        通行密钥允许您使用指纹、面容或硬件密钥安全登录，无需输入密码。
      </p>

      <!-- Credentials List -->
      <div v-if="credentials.length > 0" class="space-y-3 mb-4">
        <div
          v-for="cred in credentials"
          :key="cred.id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-900">{{ cred.device_name || '未命名设备' }}</p>
              <p class="text-xs text-gray-500">
                注册于 {{ formatDate(cred.created_at) }}
                <span v-if="cred.last_used_at"> · 最后使用 {{ formatDate(cred.last_used_at) }}</span>
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="handleRenameCredential(cred.id, cred.device_name || '')"
              class="p-2 text-gray-400 hover:text-gray-600 transition"
              title="重命名"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </button>
            <button
              @click="handleDeleteCredential(cred.id)"
              class="p-2 text-gray-400 hover:text-red-600 transition"
              title="删除"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-4 text-gray-500 text-sm mb-4">
        您还没有注册任何通行密钥
      </div>

      <!-- Register Button -->
      <button
        v-if="webAuthnSupported"
        @click="handleRegisterPasskey"
        :disabled="registering"
        class="w-full py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg font-medium hover:shadow-lg transition disabled:opacity-50 flex items-center justify-center gap-2"
      >
        <svg v-if="registering" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
        </svg>
        {{ registering ? '注册中...' : '添加通行密钥' }}
      </button>

      <p v-if="!webAuthnSupported" class="text-xs text-amber-600 text-center mt-2">
        您的浏览器不支持通行密钥
      </p>
    </div>

    <!-- User Info -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 class="text-lg font-semibold mb-4">账户信息</h2>
      <div class="space-y-3 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-500">用户名</span>
          <span class="font-medium">{{ authStore.user?.username }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">昵称</span>
          <span class="font-medium">{{ authStore.user?.nickname || '-' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">邮箱</span>
          <span class="font-medium">{{ authStore.user?.email || '-' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">角色</span>
          <span class="font-medium capitalize">{{ authStore.user?.role }}</span>
        </div>
      </div>
    </div>
  </div>
</template>