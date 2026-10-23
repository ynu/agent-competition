// v-reveal: 元素首次滚动进入视口时的载入动画指令
// 用法：v-reveal 或 v-reveal="{ delay: 120 }"
// 可选方向：up（默认）/ down / left / right / scale
import type { Directive } from 'vue'

interface RevealOptions {
  delay?: number
  direction?: 'up' | 'down' | 'left' | 'right' | 'scale'
}

const observerMap = new WeakMap<Element, IntersectionObserver>()
// 等待显示的元素集合（用于兜底：瞬时滚动跳过的元素）
const pending = new Set<HTMLElement>()
let scrollFallbackBound = false

function isAboveViewport(el: HTMLElement) {
  return el.getBoundingClientRect().bottom < 0
}

function checkPending() {
  for (const el of Array.from(pending)) {
    if (isAboveViewport(el)) {
      pending.delete(el)
      const observer = observerMap.get(el)
      if (observer) observer.unobserve(el)
      applyReveal(el, Number(el.dataset.revealDelay || 0))
    }
  }
  if (pending.size === 0) unbindScrollFallback()
}

function bindScrollFallback() {
  if (scrollFallbackBound) return
  scrollFallbackBound = true
  window.addEventListener('scroll', onScroll, { passive: true })
}

function unbindScrollFallback() {
  if (!scrollFallbackBound) return
  scrollFallbackBound = false
  window.removeEventListener('scroll', onScroll)
}

let ticking = false
function onScroll() {
  if (ticking) return
  ticking = true
  window.requestAnimationFrame(() => {
    ticking = false
    checkPending()
  })
}

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
    el.dataset.revealDelay = String(delay)

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            pending.delete(el)
            observer.unobserve(el)
            observerMap.delete(el)
            if (pending.size === 0) unbindScrollFallback()
            applyReveal(el, delay)
          }
        }
      },
      { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
    )

    observer.observe(el)
    observerMap.set(el, observer)
    // 兜底：滚动惯性/锚点跳转可能瞬间掠过元素，使其从未触发 IntersectionObserver
    pending.add(el)
    bindScrollFallback()
  },
  unmounted(el) {
    pending.delete(el)
    const observer = observerMap.get(el)
    if (observer) {
      observer.unobserve(el)
      observerMap.delete(el)
    }
  },
}

export default vReveal
