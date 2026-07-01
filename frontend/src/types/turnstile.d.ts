// Cloudflare Turnstile type definitions
interface TurnstileObject {
  render(container: string | HTMLElement, options: TurnstileOptions): string
  remove(widgetId: string): void
  reset(widgetId: string): void
}

interface TurnstileOptions {
  sitekey: string
  callback: (token: string) => void
  'expired-callback'?: () => void
  'error-callback'?: () => void
  theme?: 'light' | 'dark' | 'auto'
  size?: 'normal' | 'compact'
  tabindex?: number
}

declare global {
  interface Window {
    turnstile?: TurnstileObject
  }
}

export {}