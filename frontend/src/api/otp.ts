import api from './index'

export interface OTPConfigResponse {
  enabled: boolean
  required_for_roles: string[]
}

export interface OTPStatusResponse {
  enabled: boolean
  verified: boolean
}

export interface OTPSetupResponse {
  secret: string
  otpauth_uri: string
  qr_code_base64: string
}

export const otpApi = {
  // 获取 2FA 配置
  getConfig: () => api.get<OTPConfigResponse>('/auth/otp/config'),

  // 获取 2FA 状态
  getStatus: () => api.get<OTPStatusResponse>('/auth/otp/status'),

  // 开始 2FA 绑定
  setup: () => api.post<OTPSetupResponse>('/auth/otp/setup'),

  // 验证 OTP 完成绑定
  verifySetup: (code: string) => api.post('/auth/otp/verify-setup', { code }),

  // 禁用 2FA
  disable: (code: string) => api.post('/auth/otp/disable', { code }),

  // 2FA 登录验证
  verifyLogin: (temp_token: string, code: string) =>
    api.post('/auth/otp-login', { temp_token, code }),
}