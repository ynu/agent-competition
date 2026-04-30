import axios from "axios";
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

//axios初始化配置
const options = {
  baseURL: import.meta.env.VITE_APP_BASE_URL,
}
//创建axios对象
const request = axios.create(options)

//request拦截器
request.interceptors.request.use(function (config) {
  // 如果已登录，自动添加token到请求头
  config.headers["Content-Type"] = 'application/json'
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers["Authorization"] = `Bearer ${userStore.token}`
  }
  // 在发送请求之前做些什么
  return config
}, function (error) {
  // 对请求错误做些什么
  return Promise.reject(error)
})

//response拦截器
request.interceptors.response.use(function (response) {
  // 对响应数据做点什么
  //只需要返回数据的data
  return response.data
}, function (error) {
  //对响应不正常
  // 保护性地读取 error.response，避免在 network error 或其它情形下访问 null
  const resp = error?.response ?? null
  if (resp && resp.status !== 200) {
    const data = resp
    try {
      ElMessage.error(data.data?.msg ?? data.statusText ?? '请求错误')
    } 
    catch (e) {
      
    }
    return data
  }
  // 发现未登录 (401)
  if (resp?.status === 401) {
    const userStore = (() => {
      try { 
        return useUserStore() 
      } 
      catch (e) { 
        return null 
      }
    })()
    try {
      ElMessage.error(resp.data?.msg ?? '未授权或登录失效')
    } 
    catch (e) { 

    }
    // token过期或无效，清除登录状态
    if (userStore?.logout) userStore.logout()
    // 跳转到登录页（注：库中原来注释掉）
    //window.location.href = '/login'
    return resp
  }
  return Promise.reject(error)
});

//导出默认变量
export default request