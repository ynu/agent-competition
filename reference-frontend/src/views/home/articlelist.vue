<template>
  <section class="article-list-page min-h-[calc(100vh-200px)] bg-white pb-[69px] pt-[27px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px] xl:px-0">
      <el-breadcrumb separator=">" class="article-list-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">
          <span class="inline-flex items-center gap-[7px] text-[#777]">
            <i class="iconfont icon-shouye gap-[7px] text-[#999999]"></i>
            您当前位置：<span class="text-[#047eff]">首页</span>
          </span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>新闻列表</el-breadcrumb-item>
      </el-breadcrumb>

      <div class="mt-[36px]">
        <button
          v-for="(article, index) in pagedArticles"
          :key="article.id"
          type="button"
          class="article-item group grid w-full grid-cols-[80px_1fr] gap-[22px] border-0 border-b border-dashed border-[#e1e1e1] bg-transparent pb-[16px] pt-[16px] text-left first:pt-0"
          @click="openArticle(article)"
        >
          <time
            class="flex h-[74px] w-[80px] flex-col items-center justify-center text-white transition-colors duration-200 bg-[#b4b4b4] group-hover:bg-[#087fff]"
            :datetime="article.date"
          >
            <span class="text-[28px] font-[700] leading-[32px]">{{ article.day }}</span>
            <span class="mt-[8px] text-[16px] leading-[18px]">{{ article.month }}</span>
          </time>

          <div class="min-w-0 pt-[4px]">
            <h2
              class="line-clamp-1 text-[16px] font-[500] leading-[24px] transition-colors duration-200 text-[#202020] group-hover:text-[#007dff]"
            >
              {{ article.title }}
            </h2>
            <p class="mt-[8px] line-clamp-2 text-[12px] leading-[20px] text-[#999]">
              {{ article.summary }}
            </p>
          </div>
        </button>
      </div>

      <div class="mt-[54px] flex justify-center">
        <el-pagination
          v-model:current-page="currentPage"
          background
          layout="prev, pager, next"
          :page-size="pageSize"
          :total="articles.length"
          class="article-pagination"
          @current-change="scrollToTop"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { House } from '@element-plus/icons-vue';

const router = useRouter();
const currentPage = ref(1);
const pageSize = 8;

const summary =
  '您好，我是云小智，现在正式与全校师生见面！从今天起，我将以7×24小时在线陪伴的方式，为老师和同学们提供便捷、贴心的校园服务。无论是初来云大的新同学，还是在教学科研与管理一线忙碌的老师，我都希望成为您身边的智慧伙伴，让校园事务更简单、信息更清晰、服务更便捷。';

const seedArticles = [
  { day: '27', month: '2026-04', title: '云小智和智能体开发平台正式上线！' },
  { day: '21', month: '2026-04', title: '校园服务AI助手云小智和智能体开发平台正式上线！' },
  { day: '20', month: '2026-04', title: '云小智和智能体开发平台正式上线！' },
  { day: '12', month: '2026-04', title: '校园服务AI助手云小智和智能体开发平台正式上线！' },
  { day: '12', month: '2026-04', title: '校园服务AI助手云小智和智能体开发平台正式上线！' },
  { day: '12', month: '2026-04', title: '校园服务AI助手云小智和智能体开发平台正式上线！' },
  { day: '12', month: '2026-04', title: '校园服务AI助手云小智和智能体开发平台正式上线！' },
  { day: '12', month: '2026-04', title: '校园服务AI助手云小智和智能体开发平台正式上线！' },
];

const articles = Array.from({ length: 40 }, (_, index) => {
  const article = seedArticles[index % seedArticles.length];

  return {
    ...article,
    id: index + 1,
    date: `${article.month}-${article.day}`,
    summary,
  };
});

const pagedArticles = computed(() => {
  const start = (currentPage.value - 1) * pageSize;

  return articles.slice(start, start + pageSize);
});

const openArticle = (article) => {
  router.push({
    path: '/articlecontent',
    query: {
      id: article.id,
    },
  });
};

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};
</script>

<style scoped>
.article-list-breadcrumb {
  --el-text-color-regular: #777777;
  --el-color-primary: #047eff;
  font-size: 14px;
  line-height: 20px;
}

.article-list-breadcrumb :deep(.el-breadcrumb__inner),
.article-list-breadcrumb :deep(.el-breadcrumb__separator) {
  color: #777777;
  font-weight: 400;
}

.article-item {
  cursor: pointer;
}

.article-pagination :deep(.el-pager li),
.article-pagination :deep(.btn-prev),
.article-pagination :deep(.btn-next) {
  width: 30px;
  min-width: 30px;
  height: 30px;
  border-radius: 3px;
  background-color: #eeeeee;
  color: #9c9c9c;
  font-size: 14px;
  font-weight: 400;
}

.article-pagination :deep(.el-pager li.is-active) {
  background-color: #087fff;
  color: #ffffff;
}

.article-pagination :deep(.btn-prev),
.article-pagination :deep(.btn-next) {
  color: #b0b0b0;
}

@media (max-width: 767px) {
  .article-list-page {
    padding-top: 20px;
  }

  .article-item {
    grid-template-columns: 68px 1fr;
    gap: 16px;
    padding-bottom: 18px;
    padding-top: 18px;
  }

  .article-item time {
    width: 68px;
  }
}
</style>
