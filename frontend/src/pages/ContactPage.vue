<script setup lang="ts">
import { ref, computed } from 'vue'
import markdownIt from 'markdown-it'

const content = ref(`
## 组织机构
- **主办单位**：云南大学信息技术中心、共青团云南大学委员会、学生处、教务处、研究生处
- **协办单位**：北京火山引擎科技有限公司、云南尚雅科技文化有限公司

## 联系方式
- **联系人**：信息技术中心规划建设部
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
})

const renderedContent = computed(() => {
  return md.render(content.value)
})
</script>

<template>
  <section class="work-detail-page min-h-[calc(100vh-200px)] bg-white pb-[82px] pt-[27px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px] xl:px-0">
      <div class="detail-breadcrumb flex items-center gap-[7px] text-[#777]">
        <i class="iconfont icon-shouye text-[#999999]"></i>
        <span>您当前位置：</span>
        <RouterLink to="/" class="text-[#047eff] hover:underline">首页</RouterLink>
        <span class="mx-1">/</span>
        <span>联系我们</span>
      </div>

      <article class="mt-[19px] overflow-hidden rounded-[12px] bg-white shadow-[0_4px_18px_rgba(24,42,78,0.12)]">
        <!-- Header -->
        <div class="relative h-[150px] overflow-hidden bg-[#e7f8ff]">
          <div class="absolute inset-0 bg-gradient-to-r from-[#0066cc]/80 to-[#004385]/80"></div>
          <div class="absolute inset-0 flex flex-col justify-center px-[39px]">
            <h1 class="text-[28px] font-[800] leading-[34px] text-white">联系我们</h1>
            <p class="mt-[10px] text-[16px] text-white/80">2026云南大学首届人工智能创新应用大赛组委会</p>
          </div>
        </div>

        <!-- Content -->
        <div class="px-[39px] pr-[12px] pb-[31px] pt-[17px]">
          <div class="article-content detail-scroll" v-html="renderedContent"></div>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.detail-breadcrumb {
  font-size: 14px;
  line-height: 20px;
}

.detail-scroll::-webkit-scrollbar,
.detail-scroll::-webkit-scrollbar-thumb,
.detail-scroll::-webkit-scrollbar-thumb:hover,
.detail-scroll::-webkit-scrollbar-thumb:active {
  background: #0a7fff;
  height: 4px;
  width: 5px;
  border-radius: 3px;
}

.detail-scroll::-webkit-scrollbar-track {
  background: #f0f0f0;
  width: 5px;
  border-radius: 3px;
}

.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: #5f5f5f;
}

.article-content :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  color: #007dff;
  margin: 24px 0 16px;
  line-height: 1.4;
}

.article-content :deep(h2) {
  font-size: 20px;
  font-weight: 700;
  color: #007dff;
  margin: 20px 0 14px;
  line-height: 1.4;
}

.article-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 18px 0 12px;
}

.article-content :deep(p) {
  margin: 12px 0;
  text-indent: 2em;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 12px 0;
  padding-left: 2em;
}

.article-content :deep(li) {
  margin: 8px 0;
}

.article-content :deep(code) {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.article-content :deep(a) {
  color: #007dff;
  text-decoration: none;
}

.article-content :deep(a:hover) {
  text-decoration: underline;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.article-content :deep(th),
.article-content :deep(td) {
  border: 1px solid #ddd;
  padding: 10px 14px;
  text-align: left;
}

.article-content :deep(th) {
  background: #f5f5f5;
  font-weight: 600;
}

@media (max-width: 767px) {
  .work-detail-page {
    padding-top: 20px;
  }
}
</style>