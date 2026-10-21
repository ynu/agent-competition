<script setup lang="ts">
import { ref, computed } from 'vue'
import markdownIt from 'markdown-it'
import { mediaPlugin } from '@/plugins/markdown'

const content = ref(`
## 组织机构
- **主办单位**：云南大学信息技术中心、共青团云南大学委员会、学生处、教务处、研究生处
- **协办单位**：北京火山引擎科技有限公司、云南尚雅科技文化有限公司

## 联系方式
- **联系人**：李老师
- **邮箱**：agent-competition@itc.ynu.edu.cn
- **联系电话**：0871-65939411（工作日 9:00-17:00）

## 地址
云南省昆明市呈贡区大学城东外环南路 云南大学呈贡校区敬宾楼1416 

## 相关链接
- [云南大学官网](https://www.ynu.edu.cn/)
- [云南大学信息技术中心](https://www.itc.ynu.edu.cn/)
- [HiAgent平台](https://agent.volcengine.com/)

## 大赛答疑交流
 - ![QQ群](/src/assets/images/agent-competition-qq.png)

`)

const md = markdownIt({
  html: true,
  linkify: true,
  typographer: true
}).use(mediaPlugin)

const renderedContent = computed(() => {
  return md.render(content.value)
})
</script>

<template>
  <section class="min-h-[calc(100vh-200px)] pb-[80px] pt-[28px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px]">
      <div class="flex items-center gap-[6px] text-[14px] text-[#86868b]">
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#0071e3] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <span>联系我们</span>
      </div>

      <article class="anim-fade-up mt-[20px] overflow-hidden rounded-[24px] border border-white/70 bg-white/85 shadow-[var(--shadow-card)] backdrop-blur-xl">
        <!-- 绚丽渐变 Header -->
        <div class="relative h-[160px] overflow-hidden bg-gradient-to-br from-[#0090ff] via-[#6a5cff] to-[#ff5ca8]">
          <div class="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-white/15 blur-3xl"></div>
          <div class="absolute inset-0 flex flex-col justify-center px-[36px] lg:px-[44px]">
            <h1 class="text-[28px] font-[800] leading-[36px] text-white drop-shadow-lg">联系我们</h1>
            <p class="mt-[10px] text-[15px] text-white/85">2026年云南大学首届人工智能创新应用大赛组委会</p>
          </div>
        </div>

        <!-- Content -->
        <div class="px-[32px] pb-[36px] pt-[24px] lg:px-[44px]">
          <div class="article-content" v-html="renderedContent"></div>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.article-content {
  font-size: 16px;
  line-height: 1.9;
  color: #3a3a3c;
}

.article-content :deep(h2) {
  font-size: 20px;
  font-weight: 700;
  color: #1d1d1f;
  margin: 20px 0 14px;
  padding-left: 12px;
  border-left: 4px solid;
  border-image: linear-gradient(to bottom, #0090ff, #6a5cff) 1;
}

.article-content :deep(p) {
  margin: 12px 0;
}

.article-content :deep(ul) {
  margin: 12px 0;
  padding-left: 2em;
}

.article-content :deep(li) {
  margin: 8px 0;
}

.article-content :deep(a) {
  color: #0071e3;
  text-decoration: none;
}

.article-content :deep(a:hover) {
  text-decoration: underline;
}

.article-content :deep(img) {
  max-width: 100%;
  border-radius: 16px;
  margin: 16px 0;
  box-shadow: var(--shadow-card);
}
</style>