<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import { passkeyApi, type PasskeyCredential, type PasskeyConfig } from '@/api/passkey'
import { otpApi, type OTPSetupResponse } from '@/api/otp'
import Notification from '@/components/Notification.vue'

const notify = ref<InstanceType<typeof Notification> | null>(null)

function showNotification(type: 'success' | 'error' | 'warning' | 'info', title: string, message?: string) {
  if (notify.value) {
    notify.value[type](title, message)
  }
}

// User info
const userInfo = ref<any>(null)
const editingProfile = ref(false)
const profileForm = ref({
  nickname: '',
  email: ''
})

// Passkey
const passkeyConfig = ref<PasskeyConfig>({ enabled: false, require_for_roles: [] })
const credentials = ref<PasskeyCredential[]>([])
const registering = ref(false)
const passkeyError = ref('')
const passkeySuccess = ref('')

// 2FA
const otpConfig = ref<{ enabled: boolean; required_for_roles: string[] }>({ enabled: false, required_for_roles: [] })
const otpStatus = ref<{ enabled: boolean; verified: boolean }>({ enabled: false, verified: false })
const showOtpSetupModal = ref(false)
const otpSetupData = ref<OTPSetupResponse | null>(null)
const otpVerifyCode = ref('')
const otpLoading = ref(false)
const otpError = ref('')

// WebAuthn support
const webAuthnSupported = !!(navigator.credentials && typeof navigator.credentials.create === 'function' && typeof navigator.credentials.get === 'function')

// Base64url conversion
function base64urlToBuffer(base64url: string): ArrayBuffer {
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/')
  const binary = atob(base64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return bytes.buffer
}

function bufferToBase64url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}

function publicKeyCredentialToJson(credential: PublicKeyCredential): any {
  const response = credential.response as AuthenticatorAttestationResponse
  const transports = 'getTransports' in response ? response.getTransports() : []

  return {
    id: credential.id,
    rawId: bufferToBase64url(credential.rawId),
    type: credential.type,
    response: {
      attestationObject: bufferToBase64url(response.attestationObject),
      clientDataJSON: bufferToBase64url(response.clientDataJSON),
      transports: transports
    }
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

onMounted(async () => {
  await loadUserInfo()
  await loadPasskeyConfig()
  await loadCredentials()
  await loadOtpConfig()
  await loadOtpStatus()
})

async function loadUserInfo() {
  try {
    const res = await api.get('/auth/me')
    userInfo.value = res.data
    profileForm.value = {
      nickname: res.data.nickname || '',
      email: res.data.email || ''
    }
  } catch (e) {
    console.error('Failed to load user info:', e)
  }
}

async function updateProfile() {
  try {
    await api.put('/users/me', profileForm.value)
    userInfo.value = { ...userInfo.value, ...profileForm.value }
    editingProfile.value = false
    showNotification('success', '个人资料已更新')
  } catch (e: any) {
    showNotification('error', '更新失败', e.response?.data?.detail || '更新失败')
  }
}

async function loadPasskeyConfig() {
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
    passkeyError.value = '您的浏览器不支持通行密钥'
    return
  }

  passkeyError.value = ''
  passkeySuccess.value = ''
  registering.value = true

  try {
    const optionsRes = await passkeyApi.getRegisterOptions()
    const optionsJson = JSON.parse(optionsRes.data.options)

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

    const credential = await navigator.credentials.create({
      publicKey: publicKeyOptions
    })

    if (!credential) {
      passkeyError.value = '注册已取消'
      registering.value = false
      return
    }

    const credentialJson = publicKeyCredentialToJson(credential as PublicKeyCredential)
    await passkeyApi.verifyRegistration({
      options: JSON.stringify(credentialJson),
      device_name: getDeviceName()
    })

    passkeySuccess.value = '通行密钥注册成功'
    await loadCredentials()
  } catch (e: any) {
    console.error('Passkey registration error:', e)
    passkeyError.value = e.response?.data?.detail || e.message || '注册失败，请重试'
  } finally {
    registering.value = false
  }
}

async function handleDeleteCredential(id: number) {
  if (!confirm('确定要删除这个通行密钥吗？')) return

  try {
    await passkeyApi.deleteCredential(id)
    passkeySuccess.value = '通行密钥已删除'
    await loadCredentials()
  } catch (e: any) {
    passkeyError.value = e.response?.data?.detail || '删除失败'
  }
}

async function handleRenameCredential(id: number, currentName: string) {
  const newName = prompt('请输入新的设备名称：', currentName)
  if (!newName || newName === currentName) return

  try {
    await passkeyApi.renameCredential(id, newName)
    passkeySuccess.value = '设备名称已更新'
    await loadCredentials()
  } catch (e: any) {
    passkeyError.value = e.response?.data?.detail || '重命名失败'
  }
}

async function loadOtpConfig() {
  try {
    const res = await otpApi.getConfig()
    otpConfig.value = res.data
  } catch (e) {
    console.error('Failed to load OTP config:', e)
  }
}

async function loadOtpStatus() {
  try {
    const res = await otpApi.getStatus()
    otpStatus.value = res.data
  } catch (e) {
    console.error('Failed to load OTP status:', e)
  }
}

async function handleOtpSetup() {
  otpError.value = ''
  otpLoading.value = true
  try {
    const res = await otpApi.setup()
    otpSetupData.value = res.data
    showOtpSetupModal.value = true
  } catch (e: any) {
    otpError.value = e.response?.data?.detail || '获取 2FA 设置失败'
  } finally {
    otpLoading.value = false
  }
}

async function handleOtpVerify() {
  if (!otpVerifyCode.value || otpVerifyCode.value.length !== 6) {
    otpError.value = '请输入6位验证码'
    return
  }

  otpLoading.value = true
  otpError.value = ''
  try {
    await otpApi.verifySetup(otpVerifyCode.value)
    showOtpSetupModal.value = false
    await loadOtpStatus()
    showNotification('success', '2FA 已启用')
  } catch (e: any) {
    otpError.value = e.response?.data?.detail || '验证失败'
  } finally {
    otpLoading.value = false
    otpVerifyCode.value = ''
  }
}

async function handleOtpDisable() {
  const code = prompt('请输入当前 authenticator APP 中的验证码以禁用 2FA：')
  if (!code) return

  try {
    await otpApi.disable(code)
    await loadOtpStatus()
    showNotification('success', '2FA 已禁用')
  } catch (e: any) {
    showNotification('error', '禁用失败', e.response?.data?.detail)
  }
}
</script>

<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">个人设置</h1>
      <p class="text-gray-500 mt-1">管理您的账户信息和通行密钥</p>
    </div>

    <Notification ref="notify" />

    <!-- Alerts -->
    <div v-if="passkeyError" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
      {{ passkeyError }}
    </div>
    <div v-if="passkeySuccess" class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
      {{ passkeySuccess }}
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Profile Info Card -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">账户信息</h2>
          <button
            v-if="!editingProfile"
            @click="editingProfile = true"
            class="text-sm text-blue-600 hover:text-blue-700"
          >
            编辑
          </button>
        </div>

        <template v-if="editingProfile">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
              <input
                :value="userInfo?.username"
                type="text"
                disabled
                class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">昵称</label>
              <input
                v-model="profileForm.nickname"
                type="text"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入昵称"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
              <input
                v-model="profileForm.email"
                type="email"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入邮箱"
              />
            </div>
            <div class="flex gap-2">
              <button
                @click="updateProfile"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                保存
              </button>
              <button
                @click="editingProfile = false; profileForm = { nickname: userInfo?.nickname || '', email: userInfo?.email || '' }"
                class="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                取消
              </button>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-500">用户名</span>
              <span class="font-medium">{{ userInfo?.username }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">昵称</span>
              <span class="font-medium">{{ userInfo?.nickname || '-' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">邮箱</span>
              <span class="font-medium">{{ userInfo?.email || '-' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">角色</span>
              <span class="font-medium capitalize">{{ userInfo?.role }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">注册时间</span>
              <span class="font-medium">{{ formatDate(userInfo?.created_at) }}</span>
            </div>
          </div>
        </template>
      </div>

      <!-- Passkey Card -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">通行密钥</h2>
          <span v-if="passkeyConfig.enabled" class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">已启用</span>
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
          v-if="passkeyConfig.enabled && webAuthnSupported"
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

        <p v-if="passkeyConfig.enabled && !webAuthnSupported" class="text-xs text-amber-600 text-center mt-2">
          您的浏览器不支持通行密钥
        </p>

        <p v-if="!passkeyConfig.enabled" class="text-xs text-gray-500 text-center mt-2">
          通行密钥功能已禁用
        </p>
      </div>

      <!-- 2FA Card -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">双因素认证 (2FA)</h2>
          <span v-if="otpStatus.enabled" class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">已启用</span>
          <span v-else class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">未启用</span>
        </div>

        <p class="text-sm text-gray-500 mb-4">
          使用 authenticator APP 生成验证码进行二次验证，提高账户安全性。
        </p>

        <div v-if="otpError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {{ otpError }}
        </div>

        <div class="flex gap-2">
          <button
            v-if="!otpStatus.enabled && otpConfig.enabled"
            @click="handleOtpSetup"
            :disabled="otpLoading"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ otpLoading ? '加载中...' : '启用 2FA' }}
          </button>
          <button
            v-if="otpStatus.enabled"
            @click="handleOtpDisable"
            class="px-4 py-2 border border-red-200 text-red-600 rounded-lg hover:bg-red-50"
          >
            禁用 2FA
          </button>
          <span v-if="!otpConfig.enabled" class="text-sm text-gray-400">
            系统未启用 2FA 功能
          </span>
        </div>
      </div>
    </div>

    <!-- 2FA Setup Modal -->
    <div v-if="showOtpSetupModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold mb-4">启用双因素认证</h3>

        <div class="space-y-4">
          <div>
            <p class="text-sm text-gray-600 mb-2">1. 扫描下方二维码</p>
            <div class="flex justify-center">
              <img v-if="otpSetupData?.qr_code_base64"
                   :src="`data:image/png;base64,${otpSetupData.qr_code_base64}`"
                   alt="QR Code"
                   class="w-48 h-48" />
            </div>
          </div>

          <div>
            <p class="text-sm text-gray-600 mb-1">2. 或手动输入密钥：</p>
            <code class="block bg-gray-100 p-2 rounded text-sm break-all">{{ otpSetupData?.secret }}</code>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">3. 输入 APP 中的验证码：</label>
            <input
              v-model="otpVerifyCode"
              type="text"
              maxlength="6"
              placeholder="000000"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div v-if="otpError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {{ otpError }}
          </div>

          <div class="flex gap-2 justify-end">
            <button
              @click="showOtpSetupModal = false; otpVerifyCode = ''"
              class="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              取消
            </button>
            <button
              @click="handleOtpVerify"
              :disabled="otpLoading"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {{ otpLoading ? '验证中...' : '验证并启用' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>