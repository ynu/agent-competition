import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { user } from '@/api'

// 使用 defineStore 定义 store，建议使用 use 前缀 + store 名称 + Store
export const useUserStore = defineStore('user', () => {
  //Composition API 风格详解 Vue 3 推荐使用

  // ==================== State ====================
  // 用户信息
  const userInfo = ref({})
  //用户token
  const token = ref('')

  // ==================== Getters ====================
  // 判断用户是否登录的计算属性
  const isLogin = computed(() => Boolean(token.value))

  // ==================== Actions ====================
  /** 获取用户信息 */
  const getUserInfo = async () => {
    const { success, data, msg } = await user.myuserinfo()
    if (success) {
      // 删除所有value为或null的属性
      const newData = Object.fromEntries(Object.entries(data).filter(([_, value]) => value !== '' && value !== null))
      userInfo.value = newData
    }
    return { success, data, msg }
  }

  /** 清除用户信息 */
  const clearUserInfo = () => {
    userInfo.value = {}
    token.value = ''
  }

  /** 登录方法 */
  const loginByAccount = async (params) => {
    try {
      const { success, data, msg } = await account.login(params)
      if (!success || !data) {
        return { success: false, error: msg || '登录失败' }
      }
      token.value = data
      // 获取用户信息
      const { success: userInfoSuccess, msg: userInfoMsg } = await getUserInfo()
      // 获取用户信息失败
      if (!userInfoSuccess) {
        clearUserInfo()
        return { success: true, msg: userInfoMsg || '登录失败' }
      }
      return { success: true, data: data }
    } catch (error) {
      clearUserInfo()
      return { success: false, error: error.msg || '登录异常' }
    }
  }

  /** 退出登录 */
  const logout = () => {
    clearUserInfo()
  }

  // ========== 返回所有需要暴露的内容 ==========
  return {
    // state
    userInfo,
    token,

    // getters
    isLogin,

    // actions
    loginByAccount,
    logout,
    clearUserInfo,
    getUserInfo,
  }
},
  //第三个参数：options （可选）
  {
    // 持久化配置：将 userInfo 和 token 存储到 localStorage，刷新页面不丢失
    persist: {
      key: 'user',  // localStorage 的 key
      storage: localStorage,  // 存储位置
      paths: ['userInfo', 'token'],  // 只持久化这两个字段
    }
  })