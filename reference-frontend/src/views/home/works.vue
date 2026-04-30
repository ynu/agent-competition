<template>
  <section class="works-page min-h-[calc(100vh-200px)] bg-white pb-[72px] pt-[24px]">
    <div class="mx-auto max-w-[1200px] px-[16px]">
      <el-breadcrumb separator=">" class="works-breadcrumb text-[14px] text-[#666] font-[400]">
        <el-breadcrumb-item :to="{ path: '/' }">
          <span class="inline-flex items-center gap-[6px] text-[14px] text-[#666] font-[400] mr-[5px]">
            <i class="iconfont icon-shouye gap-[7px] text-[#999999]"></i>
            您当前位置：<span class="text-[#047EFF] cursor-pointer">首页</span> 
          </span>
        </el-breadcrumb-item>
         <el-breadcrumb-item>参赛作品</el-breadcrumb-item>
      </el-breadcrumb>

      <div class="mt-[24px] flex justify-center w-[400px] mx-auto">
        <el-input
          v-model="keyword"
          clearable
          placeholder="请输入关键字"
          class="works-search w-[460px]"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        >
          <template #prefix>
            <el-icon class="text-[#b8bdc6]"><Search /></el-icon>
          </template>
          <template #append>
            <el-button type="primary" class="!w-[86px]" @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>

      <div class="mt-[40px] grid grid-cols-1 gap-x-[34px] gap-y-[36px] sm:grid-cols-2 lg:grid-cols-4">
        <article
          v-for="work in pagedWorks"
          :key="work.id"
          class="work-card cursor-pointer overflow-hidden rounded-[10px] bg-white shadow-[0_4px_18px_rgba(28,51,84,0.10)] transition-transform duration-200 hover:-translate-y-[4px]"
          role="button"
          tabindex="0"
          @click="openWorkDetail(work)"
          @keydown.enter="openWorkDetail(work)"
          @keydown.space.prevent="openWorkDetail(work)"
        >
          <div class="relative h-[104px] overflow-hidden" :class="work.headerClass">
            <span class="absolute left-[-1px] top-[-1px] z-10 rounded-br-[8px] rounded-tl-[8px] bg-[#1189ff] px-[14px] py-[5px] text-[16px] text-white font-[800]">
              {{ work.rank }}
            </span>
            <div class="absolute left-[14px] top-[19px] text-[76px] text-white/35 font-[900] leading-none">Ai</div>
            <div class="flex items-center ml-[60px] mr-[5px] h-full py-[5px] box-border w-[calc(100%-65px)]">
              <h2 class="relative z-10 line-clamp-4 w-full text-[18px] text-[#005cae] font-[800] leading-[24px]">
                {{ work.name }}
              </h2>
            </div>
          </div>

          <div class="px-[18px] pb-[22px] pt-[20px]">
            <dl class="space-y-[8px] text-[14px] text-[#626b78] leading-[18px]">
              <div class="flex w-full">
                <dt class="tracking-[1px] w-[75px]">作品名称：</dt>
                <dd class="w-[calc(100%-75px)] line-clamp-1">{{ work.project }}</dd>
              </div>
              <div class="flex w-full">
                <dt class="tracking-[1px]  w-[75px]">参赛队伍：</dt>
                <dd class="w-[calc(100%-75px)] line-clamp-1">{{ work.team }}</dd>
              </div>
              <div class="flex w-full">
                <dt class="tracking-[1px] w-[75px]">当前票数：</dt>
                <dd class="w-[calc(100%-75px)] line-clamp-1">{{ work.votes }}</dd>
              </div>
              <div class="flex w-full">
                <dt class="tracking-[3px] w-[75px]">浏览量：</dt>
                <dd class="w-[calc(100%-75px)] line-clamp-1">{{ work.views }}</dd>
              </div>
            </dl>

            <div class="mt-[24px] flex justify-center">
              <el-button
                round
                plain
                :type="work.voted ? 'info' : 'primary'"
                :disabled="work.voted"
                class="vote-button !h-[40px] !min-w-[142px] !text-[18px] !font-[400]"
                @click.stop="voteFor(work)"
                @keydown.enter.stop
                @keydown.space.stop
              >
                <i class="iconfont icon-toupiao text-[20px] mr-2"></i>
                {{ work.voted ? '票已投完' : '我要投票' }}
              </el-button>
            </div>
          </div>
        </article>
      </div>

      <div class="mt-[54px] flex justify-center">
        <el-pagination
          v-model:current-page="currentPage"
          background
          layout="prev, pager, next"
          :page-size="pageSize"
          :total="filteredWorks.length"
          class="works-pagination"
          @current-change="scrollToTop"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { House, Search } from '@element-plus/icons-vue';

const router = useRouter();
const keyword = ref('');
const currentPage = ref(1);
const pageSize = 20;

const baseRanks = [12, 23, 28, 31, 34, 38, 41, 43, 49, 52, 57, 59, 61, 63, 66, 72, 76, 79, 88, 91];
const ranks = Array.from({ length: 100 }, (_, index) => baseRanks[index % baseRanks.length] + Math.floor(index / baseRanks.length) * 100);
const headerClasses = ['work-header-cyan', 'work-header-green', 'work-header-blue', 'work-header-orange'];

const works = ref(
  ranks.map((rank, index) => ({
    id: index + 1,
    rank,
    name: index % 4 === 0 ? '智能客服智能体' : '智能体大赛XXXXX作品',
    project: '智能体大赛020作品',
    team: 80,
    votes: 115,
    views: 1040,
    voted: [2, 5, 10, 11].includes(index),
    headerClass: headerClasses[index % headerClasses.length],
  })),
);

const filteredWorks = computed(() => {
  const value = keyword.value.trim().toLowerCase();

  if (!value) {
    return works.value;
  }

  return works.value.filter((work) =>
    [work.name, work.project, String(work.rank)].some((field) => field.toLowerCase().includes(value)),
  );
});

const pagedWorks = computed(() => {
  const start = (currentPage.value - 1) * pageSize;

  return filteredWorks.value.slice(start, start + pageSize);
});

const handleSearch = () => {
  currentPage.value = 1;
};

const openWorkDetail = (work) => {
  router.push({
    path: '/content',
    query: {
      id: work.id,
    },
  });
};

const voteFor = (work) => {
  if (work.voted) {
    return;
  }

  work.voted = true;
  work.votes += 1;
  ElMessage.success('投票成功');
};

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};
</script>

<style scoped>
.works-page {
  background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(255, 255, 255, 0.98) 34%, #ffffff 100%);
}

.works-breadcrumb {
  --el-text-color-regular: #8f96a3;
  --el-color-primary: #1288ff;
  font-size: 14px;
}

.works-search :deep(.el-input__wrapper) {
  height: 40px;
  border-radius: 4px 0 0 4px;
  background-color: #f5f5f5;
  box-shadow: none;
}

.works-search :deep(.el-input-group__append) {
  overflow: hidden;
  border-radius: 0 4px 4px 0;
  background-color: #0d8bff;
  box-shadow: none;
}

.works-search :deep(.el-input-group__append .el-button) {
  height: 40px;
  border: 0;
  border-radius: 0;
  background-color: #0d8bff;
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
}

.work-card {
  min-height: 314px;
}

.work-header-cyan {
  background: linear-gradient(105deg, #d8fbff 0%, #bff9ff 52%, #cff8ff 100%);
}

.work-header-green {
  background: linear-gradient(105deg, #d9fff7 0%, #bffbee 52%, #cef9ef 100%);
}

.work-header-blue {
  background: linear-gradient(105deg, #d9ebff 0%, #c8dcff 52%, #d8e6ff 100%);
}

.work-header-orange {
  background: linear-gradient(105deg, #ffe9d4 0%, #ffd9b8 52%, #ffe4ca 100%);
}

.vote-button :deep(.el-icon) {
  font-size: 18px;
}

.works-pagination :deep(.el-pager li),
.works-pagination :deep(.btn-prev),
.works-pagination :deep(.btn-next) {
  width: 30px;
  min-width: 30px;
  height: 30px;
  border-radius: 0;
  background-color: #f0f1f3;
  color: #a7adb7;
  font-size: 14px;
  font-weight: 700;
}

.works-pagination :deep(.el-pager li.is-active) {
  background-color: #1288ff;
  color: #ffffff;
}

@media (min-width: 1024px) {
  .works-page > div {
    max-width: 1190px;
  }
}
</style>
