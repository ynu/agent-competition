/**
 * Markdown-it 多媒体扩展插件
 * 支持：
 * 1. 自动识别链接后缀渲染为对应媒体类型（图片、PDF、音频、视频）
 * 2. 前缀语法：@[](url) PDF、#[]() 音频、$[]() 视频、![]() 图片
 * 3. 纯URL自动识别：直接输入 URL 根据后缀渲染
 */

// 媒体类型后缀匹配
const extensions = {
  image: /\.(jpg|jpeg|png|gif|svg|webp|bmp)$/i,
  pdf: /\.(pdf)$/i,
  audio: /\.(mp3|wav|ogg|m4a|flac|aac)$/i,
  video: /\.(mp4|webm|ogv|mov|avi)$/i
}

// URL 正则表达式
const urlPattern = /^https?:\/\/[^\s<>\"']+/i

// 前缀符号映射
const prefixMap: Record<number, string> = {
  64: 'pdf',    // @
  35: 'audio',  // #
  36: 'video',  // $
  37: 'image'   // %
}

function mediaPlugin(md: any) {
  // SVG 图标
  const iconPdf = '<svg class="md-media-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/></svg>'
  const iconAudio = '<svg class="md-media-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>'
  const iconVideo = '<svg class="md-media-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/></svg>'

  // 渲染函数集
  const renderers = {
    image: (href: string, title: string) => `<img src="${href}" alt="${title || ''}" class="md-media md-image" loading="lazy" />`,
    pdf: (href: string, title: string) => `
      <div class="md-media md-pdf">
        ${title ? `<div class="md-media-header">${iconPdf}<span class="md-media-title">${title}</span></div>` : ''}
        <iframe src="/pdfjs/web/viewer.html?file=${encodeURIComponent(href)}" class="md-pdf-frame" loading="lazy"></iframe>
      </div>`,
    audio: (href: string, title: string) => `
      <div class="md-media md-audio">
        ${title ? `<div class="md-media-header">${iconAudio}<span class="md-media-title">${title}</span></div>` : ''}
        <audio controls class="md-audio-player"><source src="${href}">您的浏览器不支持音频播放</audio>
      </div>`,
    video: (href: string, title: string) => `
      <div class="md-media md-video">
        ${title ? `<div class="md-media-header">${iconVideo}<span class="md-media-title">${title}</span></div>` : ''}
        <video controls class="md-video-player" loading="lazy"><source src="${href}">您的浏览器不支持视频播放</video>
      </div>`
  }

  // 检测媒体类型
  function detectMediaType(href: string, forcedType?: string): string | null {
    if (forcedType && renderers[forcedType as keyof typeof renderers]) {
      return forcedType
    }
    for (const [type, pattern] of Object.entries(extensions)) {
      if (pattern.test(href)) {
        return type
      }
    }
    return null
  }

  // 保存默认渲染器
  const defaultLinkOpen = md.renderer.rules.link_open || function(tokens: any, idx: number, options: any, env: any, self: any) {
    return self.renderToken(tokens, idx, options)
  }
  const defaultImage = md.renderer.rules.image || function(tokens: any, idx: number, options: any, env: any, self: any) {
    return self.renderToken(tokens, idx, options)
  }

  // 处理链接自动识别
  md.renderer.rules.link_open = function(tokens: any, idx: number, options: any, env: any, self: any) {
    const aIndex = tokens[idx].attrIndex('href')
    if (aIndex >= 0) {
      const href = tokens[idx].attrs[aIndex][1]
      const mediaType = detectMediaType(href)

      if (mediaType && renderers[mediaType as keyof typeof renderers]) {
        // 尝试获取链接文本作为标题
        let title = ''
        if (tokens[idx + 1] && tokens[idx + 1].type === 'text') {
          title = tokens[idx + 1].content
        }
        // 移除链接标签，直接渲染媒体
        tokens[idx].tag = 'span'
        return renderers[mediaType as keyof typeof renderers](href, title)
      }
    }
    return defaultLinkOpen(tokens, idx, options, env, self)
  }

  // 处理图片自动识别 PDF 等
  md.renderer.rules.image = function(tokens: any, idx: number, options: any, env: any, self: any) {
    const srcIndex = tokens[idx].attrIndex('src')
    if (srcIndex >= 0) {
      const src = tokens[idx].attrs[srcIndex][1]
      const alt = tokens[idx].content || ''
      const mediaType = detectMediaType(src)

      if (mediaType === 'pdf') {
        return renderers.pdf(src, alt)
      }
      if (mediaType === 'image') {
        return renderers.image(src, alt)
      }
    }
    return defaultImage(tokens, idx, options, env, self)
  }

  // 使用 inline ruler 自定义规则处理前缀语法
  md.inline.ruler.push('media_syntax', (state: any, silent: boolean) => {
    const pos = state.pos
    const max = state.posMax
    const src = state.src

    // 检查前缀符号
    const charCode = src.charCodeAt(pos)
    const prefixType = prefixMap[charCode]

    // 如果不是特殊前缀，不处理
    if (!prefixType) return false

    // 检查是否是前缀语法: @[title](url) 或 #[title](url) 等
    // 格式: <prefix>[<title>](<url>)
    const afterPrefix = pos + 1

    // 检查 [ 位置
    if (src.charCodeAt(afterPrefix) !== 0x5B) return false // 0x5B is [

    // 查找匹配的 ]
    let bracketEnd = -1
    for (let i = afterPrefix + 1; i < max; i++) {
      if (src.charCodeAt(i) === 0x5D) { // ]
        bracketEnd = i
        break
      }
    }
    if (bracketEnd === -1) return false

    // 检查 ( 位置
    const parenStart = bracketEnd + 1
    if (parenStart >= max || src.charCodeAt(parenStart) !== 0x28) return false // 0x28 is (

    // 查找匹配的 )
    let parenEnd = -1
    for (let i = parenStart + 1; i < max; i++) {
      if (src.charCodeAt(i) === 0x29) { // )
        parenEnd = i
        break
      }
    }
    if (parenEnd === -1) return false

    // 提取 title 和 url
    const title = src.slice(afterPrefix + 1, bracketEnd)
    const url = src.slice(parenStart + 1, parenEnd)

    if (!url) return false

    if (!silent) {
      // 创建 media token
      const mediaType = detectMediaType(url, prefixType)
      const html = renderers[mediaType as keyof typeof renderers]?.(url, title) ||
                   (mediaType === 'image' ? renderers.image(url, title) : renderers.pdf(url, title))

      const token = state.push('html_inline', '', 0)
      token.content = html
    }

    // 移动光标
    state.pos = parenEnd + 1
    return true
  })

  // 从 URL 获取文件名作为标题
  function getUrlFileName(url: string): string {
    try {
      const pathname = new URL(url).pathname
      const filename = pathname.split('/').pop() || ''
      return filename.replace(/\.[^.]+$/, '') || url
    } catch {
      return url
    }
  }

  // 自动识别纯 URL
  md.inline.ruler.push('auto_url', (state: any, silent: boolean) => {
    const pos = state.pos
    const max = state.posMax
    const src = state.src

    // 检查是否是 URL 开头
    const remaining = src.slice(pos)
    const match = remaining.match(urlPattern)
    if (!match) return false

    const url = match[0]
    const mediaType = detectMediaType(url)

    // 如果是媒体文件类型，自动渲染
    if (mediaType && renderers[mediaType as keyof typeof renderers]) {
      if (!silent) {
        const title = getUrlFileName(url)
        const html = renderers[mediaType as keyof typeof renderers](url, title)
        const token = state.push('html_inline', '', 0)
        token.content = html
      }
      state.pos = pos + url.length
      return true
    }

    return false
  })
}

export { mediaPlugin }