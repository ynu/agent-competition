import { ElLoading } from 'element-plus'

// 全局状态
let loadinginstace = null

// 显示加载
function showLoading() {
  loadinginstace = ElLoading.service({
    fullscreen: true,
  })
}

// 隐藏加载
function hideLoading() {
 loadinginstace.close()
}

// 导出全局方法供插件使用
export { hideLoading, showLoading }
