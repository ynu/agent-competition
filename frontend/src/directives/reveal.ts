// v-reveal: 元素首次滚动进入视口时的载入动画指令
// 用法：v-reveal 或 v-reveal="{ delay: 120 }"
// 可选方向：up（默认）/ down / left / right / scale
import type { Directive } from 'vue'

interface RevealOptions {
  delay?: number
  direction?: 'up' | 'down' | 'left' | 'right' | 'scale'
}

const observerMap = new WeakMap<Element, IntersectionObserver>()

function applyInitial(el: HTMLElement, direction: RevealOptions['direction']) {
  el.style.opacity = '0'
  el.style.willChange = 'opacity, transform'
  switch (direction) {
    case 'down':
      el.style.transform = 'translateY(-28px)'
      break
    case 'left':
      el.style.transform = 'translateX(-36px)'
      break
    case 'right':
      el.style.transform = 'translateX(36px)'
      break
    case 'scale':
      el.style.transform = 'scale(0.92)'
      break
    default:
      el.style.transform = 'translateY(32px)'
  }
}

function applyReveal(el: HTMLElement, delay: number) {
  // 动画结束后清理内联样式，避免与 hover 过渡冲突（用 setTimeout 兜底，transitionend 会从子元素冒泡）
  window.setTimeout(() => {
    el.style.willChange = ''
    el.style.transition = ''
  }, delay + 900)
  el.style.transition = `opacity 0.8s cubic-bezier(0.22, 1, 0.36, 1) ${delay}ms, transform 0.8s cubic-bezier(0.22, 1, 0.36, 1) ${delay}ms`
  // 延迟一帧再改值，确保浏览器先应用 transition，避免首帧直接跳到最终状态
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      el.style.opacity = '1'
      el.style.transform = 'none'
    })
  })
}

export const vReveal: Directive<HTMLElement, RevealOptions | undefined> = {
  mounted(el, binding) {
    const { delay = 0, direction = 'up' } = binding.value || {}

    // IntersectionObserver 不可用时不隐藏元素，直接显示
    if (typeof window === 'undefined' || typeof IntersectionObserver === 'undefined') return

    applyInitial(el, direction)

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            observer.unobserve(el)
            observerMap.delete(el)
            applyReveal(el, delay)
          }
        }
      },
      { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
    )

    observer.observe(el)
    observerMap.set(el, observer)
  },
  unmounted(el) {
    const observer = observerMap.get(el)
    if (observer) {
      observer.unobserve(el)
      observerMap.delete(el)
    }
  },
}

export default vReveal
