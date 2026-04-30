<template>
  <section class="materials-page min-h-[calc(100vh-200px)] bg-white pb-[69px] pt-[27px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px] xl:px-0">
      <el-breadcrumb separator=">" class="materials-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">
          <span class="inline-flex items-center gap-[7px] text-[#777]">
            <i class="iconfont icon-shouye gap-[7px] text-[#999999]"></i>
            您当前位置：<span class="text-[#047eff]">首页</span>
          </span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>课程资料</el-breadcrumb-item>
      </el-breadcrumb>

      <div class="mt-[26px] grid gap-[58px] lg:grid-cols-[384px_1fr]">
        <aside class="materials-sidebar">
          <div class="relative h-[158px] overflow-hidden">
            <img :src="materialsCover" alt="课程资料" class="absolute inset-0 h-full w-full object-cover" />
            <div class="absolute left-[158px] top-[45px]">
              <h1 class="text-[28px] font-[700] leading-[38px] text-[#004385]">课程资料</h1>
              <p class="mt-[7px] text-[18px] leading-[24px] text-[#222]">HiAgent 平台实操培训</p>
            </div>
          </div>

          <nav class="mt-[19px] space-y-[20px]" aria-label="课程资料目录">
            <button
              v-for="(course, index) in courses"
              :key="course.title"
              type="button"
              class="course-tab flex h-[80px] w-full items-center cursor-pointer rounded-[8px] border-0 bg-white px-[14px] text-left shadow-[0_4px_16px_rgba(20,42,80,0.11)] transition-all duration-200 hover:-translate-y-[2px] hover:shadow-[0_8px_20px_rgba(20,42,80,0.14)]"
              :class="{ 'is-active': activeIndex === index }"
              @click="activeIndex = index"
            >
              <span class="flex h-[54px] w-[54px] shrink-0 items-center justify-center rounded-full transition-colors duration-200" :class="activeIndex === index ? 'bg-[#e5f5ff]' : 'bg-[#f5f5f5]'">
                <img :src="materialsIcon" alt="" class="h-[32px] w-[32px]" />
              </span>
              <span class="ml-[13px] line-clamp-2 text-[16px] font-[800] leading-[22px] transition-colors duration-200" :class="activeIndex === index ? 'text-[#007dff]' : 'text-[#202020]'">
                {{ course.title }}
              </span>
            </button>
          </nav>
        </aside>

        <article class="materials-content min-w-0">
          <header class="text-center">
            <h2 class="text-[30px] font-[800] leading-[38px] text-[#2a2a2a]">{{ activeCourse.title }}</h2>
            <div class="mt-[17px] flex flex-wrap items-center justify-center gap-x-[45px] gap-y-[8px] text-[14px] leading-[20px] text-[#999]">
              <span>发布日期：{{ activeCourse.date }}</span>
              <span>来源：{{ activeCourse.source }}</span>
            </div>
          </header>

          <div class="mt-[16px] border-t border-dashed border-[#b8b8b8] pt-[26px]">
            <div class="space-y-[16px] text-[16px] leading-[28px] text-[#5f5f5f]">
              <p v-for="paragraph in activeCourse.paragraphs" :key="paragraph" class="indent-[2em]">
                {{ paragraph }}
              </p>
            </div>

            <div class="mt-[30px] space-y-[31px]">
              <img
                v-for="image in activeCourse.images"
                :key="image.src"
                :src="image.src"
                :alt="image.alt"
                class="w-full object-cover"
                loading="lazy"
              />
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue';
import { House } from '@element-plus/icons-vue';
import materialsCover from '@/assets/images/img_materials.png';
import materialsIcon from '@/assets/images/img_materials_list.png';
import courseImage01 from '@/assets/images/img_materials_course_01.png';
import courseImage02 from '@/assets/images/img_materials_course_02.png';
import courseImage03 from '@/assets/images/img_materials_course_03.png';

const activeIndex = ref(1);

const sharedParagraphs = [
  '为响应国家“人工智能+”行动建设战略部署，在国家教育数字化、AI 融合发展等政策指引下，AI人工智能正迈入场景化落地关键期，智能体作为融合大模型能力、链接技术与需求的核心载体，在教育、校园服务等领域的应用潜力加速释放，恰好为高校实践创新提供了新抓手。',
  '在此背景下，为进一步落实学校《提升师生数字素养与技能实施方案》，云南大学联合火山引擎举办首届“火山杯”AI 应用创新大赛。赛事鼓励学生运用 AI 能力，在多元场景中探索技术创新应用，既为激发师生创新热情与实践能力搭建平台，也为培养兼具理论素养与实操能力、适配智能时代需求的创新型人才提供助力。',
];

const materialImages = [
  { src: courseImage01, alt: 'HiAgent智能创新平台提示词编写技巧' },
  { src: courseImage02, alt: '提示词重要性' },
  { src: courseImage03, alt: '好提示词原则' },
];

const courses = [
  {
    title: 'HiAgent平台智能体搭建入门指南',
    date: '2026-04-08',
    source: '云南大学',
    paragraphs: sharedParagraphs,
    images: materialImages,
  },
  {
    title: 'HiAgent智能体平台-提示词编写技巧',
    date: '2026-04-10',
    source: '云南大学',
    paragraphs: sharedParagraphs,
    images: materialImages,
  },
  {
    title: 'HiAgent智能体平台-智能体开发功能概述',
    date: '2026-04-12',
    source: '云南大学',
    paragraphs: sharedParagraphs,
    images: materialImages,
  },
  {
    title: 'HiAgent智能体平台-案例：智能客服智能体',
    date: '2026-04-15',
    source: '云南大学',
    paragraphs: sharedParagraphs,
    images: materialImages,
  },
];

const activeCourse = computed(() => courses[activeIndex.value]);
</script>

<style scoped>
.materials-breadcrumb {
  --el-text-color-regular: #777777;
  --el-color-primary: #047eff;
  font-size: 14px;
  line-height: 20px;
}

.materials-breadcrumb :deep(.el-breadcrumb__inner),
.materials-breadcrumb :deep(.el-breadcrumb__separator) {
  color: #777777;
  font-weight: 400;
}

.course-tab.is-active {
  box-shadow: 0 6px 18px rgba(20, 42, 80, 0.12);
}

.materials-content img {
  display: block;
}

@media (min-width: 1024px) {
  .materials-sidebar {
    position: sticky;
    top: 104px;
    align-self: start;
  }
}

@media (max-width: 1023px) {
  .materials-page {
    padding-bottom: 52px;
  }

  .materials-sidebar {
    max-width: 520px;
  }
}

@media (max-width: 767px) {
  .materials-page {
    padding-top: 20px;
  }

  .materials-sidebar {
    max-width: none;
  }

  .materials-sidebar > div:first-child {
    height: 150px;
  }

  .materials-sidebar > div:first-child > div {
    left: 145px;
    top: 42px;
  }

  .materials-content header {
    text-align: left;
  }

  .materials-content header > div {
    justify-content: flex-start;
  }
}
</style>
