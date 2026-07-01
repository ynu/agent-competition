import api from './index'

// Passkey 相关类型
export interface PasskeyConfig {
  enabled: boolean
  require_for_roles: string[]
}

export interface PasskeyCredential {
  id: number
  device_name: string | null
  created_at: string
  last_used_at: string | null
}

export interface PasskeyLoginOptions {
  options: string
  challenge: string
  username: string
}

export interface PasskeyRegisterOptions {
  options: string
  challenge: string
}

// Passkey API
export const passkeyApi = {
  // 配置
  getConfig: () => api.get<PasskeyConfig>('/auth/passkey/config'),

  // 注册流程
  getRegisterOptions: () => api.get<PasskeyRegisterOptions>('/auth/passkey/register-options'),
  verifyRegistration: (data: {
    options: string
    device_name?: string
  }) => api.post('/auth/passkey/register-verify', data),

  // 登录流程
  getLoginOptions: (username: string) => api.post<PasskeyLoginOptions>('/auth/passkey/login-options', { username }),
  verifyLogin: (data: {
    username: string
    credential_id: string
    options: string
  }) => api.post<{ access_token: string; token_type: string; user: any }>('/auth/passkey/login-verify', data),

  // 用户凭证管理
  getMyCredentials: () => api.get<PasskeyCredential[]>('/passkey/credentials'),
  deleteCredential: (credentialId: number) => api.delete(`/passkey/credentials/${credentialId}`),
  renameCredential: (credentialId: number, deviceName: string) =>
    api.patch(`/passkey/credentials/${credentialId}/rename`, { device_name: deviceName })
}