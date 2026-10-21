<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'
import { passkeyApi } from '@/api/passkey'
import { otpApi } from '@/api/otp'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const showPasswordTab = ref(false)
const error = ref('')
const loading = ref(false)

// Turnstile config
const turnstileEnabled = ref(false)
const turnstileSiteKey = ref('')
const turnstileToken = ref('')
const turnstileWidgetId = ref<string | null>(null)

// Passkey 相关
const passkeyEnabled = ref(false)
const passkeyLoading = ref(false)
const passkeyError = ref('')

// 2FA 验证状态
const requiresOtp = ref(false)
const tempToken = ref('')
const otpCode = ref('')
const otpLoading = ref(false)

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

// 检测浏览器是否支持 WebAuthn
const webAuthnSupported = computed(() => {
  const creds = navigator.credentials
  return !!(creds && typeof creds.create === 'function' && typeof creds.get === 'function')
})

// Watch for password tab visibility to re-render turnstile
watch(showPasswordTab, async (newVal) => {
  if (newVal && showBothTabs.value) {
    // Password tab is now visible, render turnstile
    await loadTurnstileConfig()
  }
})

async function loadPasskeyConfig() {
  try {
    const res = await passkeyApi.getConfig()
    passkeyEnabled.value = res.data.enabled
  } catch (e) {
    console.error('Failed to load passkey config:', e)
  }
}

async function handlePasskeyLogin() {
  passkeyError.value = ''
  passkeyLoading.value = true

  try {
    // 获取登录选项（无需用户名）
    const optionsRes = await passkeyApi.getLoginOptionsDiscoverable()
    const options = JSON.parse(optionsRes.data.options)

    // 将 base64url 字符串转换回 ArrayBuffer
    const publicKeyOptions = {
      challenge: base64urlToBuffer(options.challenge),
      allowCredentials: [],  // 空数组表示可发现凭证
      timeout: options.timeout,
      userVerification: options.userVerification
    }

    // 调用 WebAuthn
    const credential = await navigator.credentials.get({
      publicKey: publicKeyOptions
    })

    if (!credential) {
      passkeyError.value = '认证已取消'
      passkeyLoading.value = false
      return
    }

    // 验证登录（无需用户名）
    const verifyRes = await passkeyApi.verifyLoginDiscoverable({
      options: JSON.stringify(credential)
    })

    // 检查是否需要 2FA 验证
    if (verifyRes.data.requires_otp && verifyRes.data.temp_token) {
      // 需要 2FA 验证
      requiresOtp.value = true
      tempToken.value = verifyRes.data.temp_token!
      passkeyLoading.value = false
      return
    }

    // 保存 token 并跳转
    localStorage.setItem('token', verifyRes.data.access_token!)
    const redirect = route.query.redirect as string || '/admin'
    window.location.href = redirect
  } catch (e: any) {
    console.error('Passkey login failed:', e)
    passkeyError.value = e.response?.data?.detail || 'Passkey 登录失败'
    passkeyLoading.value = false
  }
}

// Default: show only unified auth, show both when ?localAccount=true
const showBothTabs = computed(() => route.query.localAccount === 'true')

function loadTurnstileScript(): Promise<void> {
  return new Promise((resolve) => {
    if (window.turnstile) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js'
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    document.head.appendChild(script)
  })
}

async function loadTurnstileConfig() {
  try {
    const res = await authApi.getTurnstileConfig()
    turnstileEnabled.value = res.data.enabled
    turnstileSiteKey.value = res.data.site_key || ''

    if (turnstileEnabled.value && turnstileSiteKey.value) {
      await loadTurnstileScript()
      // Wait for turnstile to be ready
      await new Promise<void>((resolve) => {
        if (window.turnstile) {
          resolve()
          return
        }
        const check = setInterval(() => {
          if (window.turnstile) {
            clearInterval(check)
            resolve()
          }
        }, 100)
      })
      renderTurnstile()
    }
  } catch (e) {
    console.error('Failed to load turnstile config:', e)
  }
}

function renderTurnstile() {
  if (!turnstileEnabled.value || !turnstileSiteKey.value) return

  // Wait for container to be in DOM
  const waitForContainer = () => {
    return new Promise<HTMLElement | null>((resolve) => {
      const container = document.getElementById('turnstile-container')
      if (container) {
        resolve(container)
        return
      }
      // Wait a bit for DOM to update
      setTimeout(() => {
        resolve(document.getElementById('turnstile-container'))
      }, 50)
    })
  }

  waitForContainer().then((container) => {
    if (!container) return

    // Clear existing widget
    container.innerHTML = ''
    if (turnstileWidgetId.value) {
      try {
        window.turnstile?.remove(turnstileWidgetId.value)
      } catch (e) {
        // ignore
      }
    }

    const result = window.turnstile?.render(container, {
      sitekey: turnstileSiteKey.value,
      callback: (token: string) => {
        turnstileToken.value = token
      },
      'expired-callback': () => {
        turnstileToken.value = ''
      },
      'error-callback': () => {
        turnstileToken.value = ''
      },
      theme: 'light'
    })
    turnstileWidgetId.value = typeof result === 'string' ? result : null
  })
}

onMounted(async () => {
  // Check if there's a token in URL (from CAS callback)
  const token = route.query.token as string
  if (token) {
    console.log('CAS callback: got token', token.substring(0, 20) + '...')
    localStorage.setItem('token', token)
    // Use window.location to force full page reload
    const redirect = route.query.redirect as string || '/admin'
    window.location.href = redirect
  }

  // Default to unified auth if not showing both tabs
  if (!showBothTabs.value) {
    showPasswordTab.value = false
  }

  // Load turnstile config if showing password tab
  if (showBothTabs.value) {
    await loadTurnstileConfig()
  }

  // Load passkey config
  await loadPasskeyConfig()
})

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    const res = await authApi.login({ username: username.value, password: password.value, turnstile_token: turnstileToken.value || undefined })

    if (res.data.requires_otp && res.data.temp_token) {
      // 需要 2FA 验证
      requiresOtp.value = true
      tempToken.value = res.data.temp_token
      loading.value = false
    } else {
      // 直接登录成功
      localStorage.setItem('token', res.data.access_token!)
      // 更新 authStore 的 token
      authStore.$patch({ token: res.data.access_token! })
      await authStore.fetchUser()
      const redirect = route.query.redirect as string || '/admin'
      router.push(redirect)
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败'
    // Reset turnstile on error
    if (turnstileEnabled.value) {
      renderTurnstile()
    }
  } finally {
    loading.value = false
  }
}

function handleCasLogin() {
  // Redirect to CAS login (backend will handle service URL)
  window.location.href = '/api/auth/cas/login'
}

async function handleOtpVerify() {
  if (!otpCode.value || otpCode.value.length !== 6) {
    error.value = '请输入6位验证码'
    return
  }

  const code = otpCode.value  // Save code before clearing
  otpLoading.value = true
  error.value = ''

  try {
    const res = await otpApi.verifyLogin(tempToken.value, code)
    console.log('OTP verify response:', res)

    // Success - update everything and redirect
    const accessToken = res.data.access_token
    if (!accessToken) {
      throw new Error('No access token')
    }

    // Update auth state
    localStorage.setItem('token', accessToken)

    // Use store methods to update state properly
    authStore.$patch({
      token: accessToken,
      user: res.data.user
    })

    // Clear 2FA state and input
    requiresOtp.value = false
    otpCode.value = ''
    tempToken.value = ''

    // Redirect immediately
    const redirect = route.query.redirect as string || '/admin'
    console.log('Redirecting to:', redirect)
    router.push(redirect)
  } catch (e: any) {
    console.error('OTP verify error:', e)
    error.value = e.response?.data?.detail || e.message || '验证失败'
    otpCode.value = ''  // Only clear on error
  } finally {
    otpLoading.value = false
  }
}
</script>

<template>
  <div class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#0b0b14] py-12 px-4">
    <!-- 绚丽极光背景 -->
    <div class="absolute inset-0" style="background: radial-gradient(at 15% 20%, rgba(0,144,255,0.4) 0px, transparent 50%), radial-gradient(at 85% 15%, rgba(255,92,168,0.32) 0px, transparent 50%), radial-gradient(at 70% 85%, rgba(106,92,255,0.38) 0px, transparent 50%), radial-gradient(at 20% 80%, rgba(0,198,255,0.28) 0px, transparent 50%)"></div>
    <div class="absolute inset-0 backdrop-blur-[2px]"></div>
    <!-- 漂浮光斑 -->
    <div class="anim-float pointer-events-none absolute -top-32 right-10 h-72 w-72 rounded-full bg-[#6a5cff]/25 blur-3xl"></div>
    <div class="anim-float pointer-events-none absolute -bottom-32 left-10 h-72 w-72 rounded-full bg-[#ff5ca8]/20 blur-3xl" style="animation-delay: 1.6s"></div>

    <div class="relative w-full max-w-md">
      <!-- Logo & Title -->
      <div class="anim-fade-up mb-8 text-center">
        <div class="anim-float mx-auto mb-5 inline-flex h-[68px] w-[68px] items-center justify-center rounded-[22px] bg-gradient-to-br from-[#0090ff] via-[#6a5cff] to-[#ff5ca8] text-[32px] shadow-[0_16px_48px_rgba(106,92,255,0.5)]">
          🤖
        </div>
        <h1 class="mb-2 text-[30px] font-[700] text-white drop-shadow">智能体创新大赛</h1>
        <p class="text-white/70">登录到管理系统</p>
      </div>

      <!-- Login Card：毛玻璃 -->
      <div class="anim-fade-up rounded-[26px] border border-white/25 bg-white/[0.12] p-8 shadow-[0_32px_90px_rgba(0,0,0,0.45)] backdrop-blur-2xl" style="animation-delay: 0.12s">
        <!-- Login Mode Toggle (only show when ?localAccount=true) -->
        <div v-if="showBothTabs" class="mb-6 flex rounded-full bg-white/15 p-1 backdrop-blur">
          <button
            @click="showPasswordTab = true"
            class="flex-1 rounded-full py-2.5 text-sm font-[600] transition-all duration-300"
            :class="showPasswordTab ? 'bg-white text-[#0071e3] shadow-md' : 'text-white/70 hover:text-white'"
          >
            账号密码
          </button>
          <button
            v-if="passkeyEnabled && webAuthnSupported"
            @click="showPasswordTab = false"
            class="flex-1 rounded-full py-2.5 text-sm font-[600] transition-all duration-300"
            :class="!showPasswordTab ? 'bg-white text-[#30d158] shadow-md' : 'text-white/70 hover:text-white'"
          >
            通行密钥
          </button>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Passkey Login (only when ?localAccount=true and passkey tab selected) -->
          <template v-if="showBothTabs && !showPasswordTab && passkeyEnabled && webAuthnSupported">
            <div class="text-center py-4 mb-2">
              <p class="mb-6 text-sm text-white/70">点击按钮使用已注册的通行密钥登录，无需输入用户名</p>
            </div>

            <!-- Error Message -->
            <div v-if="passkeyError" class="flex items-center gap-2 rounded-[14px] bg-[#ff3b30]/15 p-3 text-sm text-[#ffb3ae] backdrop-blur">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              {{ passkeyError }}
            </div>

            <!-- Passkey Login Button -->
            <button
              type="button"
              @click="handlePasskeyLogin"
              :disabled="passkeyLoading"
              class="flex w-full items-center justify-center gap-2 rounded-full bg-gradient-to-r from-[#30d158] to-[#00c6ff] py-3.5 font-[600] text-white shadow-[0_12px_36px_rgba(48,209,88,0.4)] transition-transform duration-300 hover:-translate-y-0.5 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg v-if="passkeyLoading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
              </svg>
              {{ passkeyLoading ? '验证中...' : '使用通行密钥登录' }}
            </button>
          </template>

          <!-- Password Login -->
          <template v-if="showBothTabs && showPasswordTab">
            <div>
              <label class="mb-2 block text-sm font-[500] text-white/80">用户名/学工号</label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg class="w-5 h-5 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                  </svg>
                </div>
                <input
                  v-model="username"
                  type="text"
                  required
                  class="w-full rounded-[14px] border border-white/25 bg-white/12 py-3 pl-12 pr-4 text-white outline-none transition-all duration-300 placeholder:text-white/40 focus:border-[#0090ff]/60 focus:bg-white/18 focus:ring-4 focus:ring-[#0090ff]/25"
                  placeholder="请输入用户名"
                />
              </div>
            </div>

            <div>
              <label class="mb-2 block text-sm font-[500] text-white/80">密码</label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg class="w-5 h-5 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                </div>
                <input
                  v-model="password"
                  type="password"
                  required
                  class="w-full rounded-[14px] border border-white/25 bg-white/12 py-3 pl-12 pr-4 text-white outline-none transition-all duration-300 placeholder:text-white/40 focus:border-[#0090ff]/60 focus:bg-white/18 focus:ring-4 focus:ring-[#0090ff]/25"
                  placeholder="请输入密码"
                />
              </div>
            </div>
          </template>

          <!-- Unified Auth / Default content (when not ?localAccount=true) -->
          <template v-if="!showBothTabs">
            <div class="text-center py-4 mb-2">
              <p class="mb-6 text-sm text-white/70">使用学校统一身份认证账号登录，首次登录将自动创建用户</p>
            </div>

            <!-- Unified Auth Button -->
            <button
              type="button"
              @click="handleCasLogin"
              class="anim-gradient flex w-full items-center justify-center gap-2 rounded-full bg-gradient-to-r from-[#0090ff] via-[#6a5cff] to-[#ff5ca8] py-3.5 font-[600] text-white shadow-[0_12px_36px_rgba(106,92,255,0.5)] transition-transform duration-300 hover:-translate-y-0.5 active:scale-[0.98]"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/>
              </svg>
              使用统一身份认证登录
            </button>
          </template>

          <!-- Error Message -->
          <div v-if="error" class="flex items-center gap-2 rounded-[14px] bg-[#ff3b30]/15 p-3 text-sm text-[#ffb3ae] backdrop-blur">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            {{ error }}
          </div>

          <!-- Turnstile verification -->
          <div v-if="showBothTabs && showPasswordTab && turnstileEnabled" class="flex justify-center">
            <div id="turnstile-container"></div>
          </div>

          <!-- 2FA 验证码输入 (两步验证) -->
          <div v-if="requiresOtp" class="space-y-4">
            <div class="text-center py-4">
              <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-white/15 backdrop-blur">
                <svg class="w-6 h-6 text-[#4d9df0]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
              </div>
              <p class="mb-4 text-white/80">请输入 authenticator APP 中的验证码</p>
              <input
                v-model="otpCode"
                type="text"
                maxlength="6"
                placeholder="000000"
                class="w-32 rounded-[14px] border border-white/25 bg-white/12 px-4 py-3 text-center text-2xl tracking-widest text-white outline-none transition-all duration-300 focus:border-[#0090ff]/60 focus:ring-4 focus:ring-[#0090ff]/25"
                @keyup.enter="handleOtpVerify"
              />
            </div>

            <button
              @click="handleOtpVerify"
              :disabled="otpLoading"
              class="w-full rounded-full bg-gradient-to-r from-[#0090ff] to-[#6a5cff] py-3 font-[600] text-white shadow-[0_10px_30px_rgba(0,144,255,0.4)] transition-transform duration-300 hover:-translate-y-0.5 disabled:opacity-50"
            >
              <svg v-if="otpLoading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ otpLoading ? '验证中...' : '验证并登录' }}
            </button>

            <button
              @click="requiresOtp = false; otpCode = ''; tempToken = ''"
              class="w-full py-2 text-sm text-white/60 hover:text-white transition-colors"
            >
              返回重新登录
            </button>
          </div>

          <!-- Submit Button (password login) -->
          <button
            v-if="showBothTabs && showPasswordTab && !requiresOtp"
            type="submit"
            :disabled="loading"
            class="anim-gradient flex w-full items-center justify-center gap-2 rounded-full bg-gradient-to-r from-[#0090ff] via-[#6a5cff] to-[#ff5ca8] py-3.5 font-[600] text-white shadow-[0_12px_36px_rgba(106,92,255,0.5)] transition-transform duration-300 hover:-translate-y-0.5 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="loading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <div class="mt-6 text-center">
          <RouterLink to="/" class="text-sm text-white/60 hover:text-white transition">
            ← 返回首页
          </RouterLink>
        </div>
      </div>

      <!-- Footer -->
      <div class="anim-fade-up mt-6 text-center text-white/55 text-sm" style="animation-delay: 0.2s">
        <p>如有问题请联系管理员</p>
      </div>
    </div>
  </div>
</template>