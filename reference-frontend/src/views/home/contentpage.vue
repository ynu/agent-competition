<template>
  <section class="work-detail-page min-h-[calc(100vh-200px)] bg-white pb-[82px] pt-[27px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px] xl:px-0">
      <el-breadcrumb separator=">" class="detail-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">
          <span class="inline-flex items-center gap-[7px] text-[#777]">
            <i class="iconfont icon-shouye gap-[7px] text-[#999999]"></i>
            您当前位置：<span class="text-[#047eff]">首页</span>
          </span>
        </el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/works' }">
          <span class="text-[#047eff]">参赛作品</span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>作品详情</el-breadcrumb-item>
      </el-breadcrumb>

      <article class="mt-[19px] overflow-hidden rounded-[12px] bg-white shadow-[0_4px_18px_rgba(24,42,78,0.12)]">
        <div class="relative h-[210px] overflow-hidden bg-[#e7f8ff]">
          <img :src="detailBanner" alt="" class="absolute inset-0 h-full w-full object-cover" />
          <span class="absolute left-0 top-0 flex h-[37px] w-[71px] items-center justify-center rounded-br-[14px] bg-[#087fff] text-[22px] font-[800] leading-none text-white">
            {{ work.rank }}
          </span>

          <div class="absolute left-[80px] top-[77px] max-w-[720px]">
            <h1 class="text-[28px] font-[800] leading-[34px] text-[#004385]">{{ work.title }}</h1>
            <div class="mt-[15px] flex items-center gap-[31px] text-[16px] leading-[20px] text-[#666]">
              <span class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-zongzhiduiwu text-[22px] text-[#999]"></i>
                {{ work.teamCount }}
              </span>
              <span class="inline-flex items-center gap-[7px]">
                <i class="iconfont icon-icon- text-[22px] text-[#999]"></i>
                {{ work.views }}
              </span>
            </div>
          </div>

          <div class="absolute right-[72px] top-[35px] flex flex-col items-center">
            <div class="flex h-[103px] w-[103px] flex-col items-center justify-center rounded-full bg-white text-center">
              <strong class="text-[32px] font-[800] leading-[38px] text-[#ff3c3c]">{{ voteCount }}</strong>
              <span class="mt-[7px] text-[16px] font-[400] leading-[16px] text-[#ff3c3c]">票</span>
            </div>
            <el-button
              type="danger"
              round
              class="vote-action mt-[10px] !h-[40px] !w-[133px] !border-0 !bg-[#ff5959] !px-0 !text-[18px] !font-[500]"
              :disabled="hasVoted"
              @click="handleVote"
            >
              <i class="iconfont icon-toupiao mr-[4px] text-[18px]"></i>
              {{ hasVoted ? '已投票' : '我要投票' }}
            </el-button>
          </div>
        </div>

        <div class=" pl-[39px] pr-[12px] pb-[31px] pt-[17px]">
          <h2 class="text-[20px] font-[700] leading-[34px] text-[#007dff]">作品描述</h2>
          <div class="mt-[12px] space-y-[14px] text-[16px] leading-[28px] text-[#5f5f5f] detail-scroll max-h-[303px] overflow-y-auto">
            <p v-for="paragraph in description" :key="paragraph" class="indent-[2em]">
              {{ paragraph }}
            </p>
          </div>
        </div>
      </article>

      <section class="mt-[24px] rounded-[12px] bg-white px-[36px] pb-[34px] pt-[17px] shadow-[0_4px_18px_rgba(24,42,78,0.12)]">
        <h2 class="text-[20px] font-[700] leading-[34px] text-[#007dff]">队伍成员</h2>
        <div class="mt-[9px] flex flex-wrap gap-[14px]">
          <div
            v-for="member in members"
            :key="`${member.name}-${member.role}`"
            class="flex h-[63px] w-[177px] items-center rounded-[8px] bg-[#f3f3f3] px-[14px]"
          >
            <img :src="member.avatar" :alt="member.name" class="h-[44px] w-[44px] shrink-0 rounded-full" />
            <div class="ml-[14px] min-w-0">
              <p class="truncate text-[16px] font-[700] leading-[22px] text-[#191919]">{{ member.name }}</p>
              <p class="mt-[1px] text-[14px] leading-[20px] text-[#777]">{{ member.role }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="mt-[24px] rounded-[12px] bg-white px-[36px] pb-[33px] pt-[17px] shadow-[0_4px_18px_rgba(24,42,78,0.12)]">
        <h2 class="text-[20px] font-[700] leading-[34px] text-[#007dff]">作品资源</h2>
        <div class="mt-[8px] grid gap-x-[23px] gap-y-[24px] lg:grid-cols-2">
          <div
            v-for="resource in resources"
            :key="resource.title"
            class="resource-card flex min-h-[80px] items-center rounded-[8px] px-[15px]"
            :class="resource.className"
          >
            <img :src="resource.icon" class="w-[55px] h-[55px] rounded-full" />
            <div class="ml-[15px] min-w-0 flex-1">
              <p class="text-[16px] font-[800] leading-[22px] text-[#1d1d1d] line-clamp-1">{{ resource.title }}</p>
              <p class="mt-[3px] truncate text-[14px] leading-[20px] text-[#666]">{{ resource.value }}</p>
            </div>
            <el-button
              round
              class="resource-button ml-[16px] !h-[40px] !w-[104px] !border-0 !px-0 !text-[16px] !font-[800] !text-white"
              :class="resource.buttonClass"
              @click="handleResource(resource)"
            >
              {{ resource.buttonText }}
            </el-button>
          </div>
        </div>
      </section>
    </div>

    <el-dialog v-model="videoVisible" title="演示视频" width="780px" class="video-dialog" destroy-on-close>
      <div class="flex min-h-[360px] items-center justify-center rounded-[8px] bg-[#111827] text-[16px] text-white">
        当前演示视频地址：{{ videoResource?.value }}
      </div>
    </el-dialog>
  </section>
</template>

<script setup>
import { shallowRef, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { Document, House, Link, User, VideoPlay, View } from '@element-plus/icons-vue';
import detailBanner from '@/assets/images/banner_works_detail.png';
import leaderAvatar from '@/assets/images/img_team_01.png';
import memberAvatar from '@/assets/images/img_team_02.png';
import resourceIcon1 from '@/assets/images/img_works_01.png'
import resourceIcon2 from '@/assets/images/img_works_02.png'
import resourceIcon3 from '@/assets/images/img_works_03.png'



const work = {
  rank: 12,
  title: '智能体大赛012作品-智能客服',
  teamCount: 80,
  views: 1040,
  votes: 115,
};

const voteCount = ref(work.votes);
const hasVoted = ref(false);
const videoVisible = ref(false);
const videoResource = shallowRef(null);

const description = [
  '为响应国家“人工智能+”行动建设战略部署，在国家教育数字化、AI 融合发展等政策指引下，AI人工智能正迈入场景化落地关键期，智能体作为融合大模型能力、链接技术与需求的核心载体，在教育、校园服务等领域的应用潜力加速释放，恰好为高校实践创新提供了新抓手。',
  '在此背景下，为进一步落实学校《提升师生数字素养与技能实施方案》，云南大学联合火山引擎举办首届“火山杯”AI 应用创新大赛。赛事鼓励学生运用 AI 能力，在多元场景中探索技术创新应用，既为激发师生创新热情与实践能力搭建平台，也为培养兼具理论素养与实操能力、适配智能时代需求的创新型人才提供助力。',
  '为响应国家“人工智能+”行动建设战略部署，在国家教育数字化、AI 融合发展等政策指引下，AI人工智能正迈入场景化落地关键期，智能体作为融合大模型能力、链接技术与需求的核心载体，在教育、校园服务等领域的应用潜力加速释放，恰好为高校实践创新提供了新抓手。',
];

const members = [
  { name: '王某某', role: '队长', avatar: leaderAvatar },
  { name: '李某某', role: '队员', avatar: memberAvatar },
  { name: '张某', role: '队员', avatar: memberAvatar },
  { name: '李某', role: '队员', avatar: memberAvatar },
  { name: '王某', role: '队员', avatar: memberAvatar },
];

const resources = [
  {
    title: '智能体URL',
    value: 'http://localhost:5173/admin/works',
    buttonText: '打开链接',
    className: 'bg-[#e0f2ff]',
    iconClass: 'text-[#2b82ff]',
    buttonClass: '!bg-[#2d80ff]',
    icon: resourceIcon1,
    type: 'link',
  },
  {
    title: 'PDF文档',
    value: 'uploads\\pdf\\1774998851.935295.pdf',
    buttonText: '查看PDF',
    className: 'bg-[#fff0f3]',
    iconClass: 'text-[#ff6666]',
    buttonClass: '!bg-[#ff5959]',
    icon: resourceIcon2,
    type: 'pdf',
  },
  {
    title: '演示视频',
    value: 'uploads\\video\\1774998851.94341.mp4',
    buttonText: '播放视频',
    className: 'bg-[#fff6e5]',
    iconClass: 'text-[#ff9d2e]',
    buttonClass: '!bg-[#ff8d45]',
    icon: resourceIcon3,
    type: 'video',
  },
];

const handleVote = () => {
  if (hasVoted.value) {
    return;
  }

  voteCount.value += 1;
  hasVoted.value = true;
  ElMessage.success('投票成功');
};

const handleResource = (resource) => {
  if (resource.type === 'video') {
    videoResource.value = resource;
    videoVisible.value = true;
    return;
  }

  const target = resource.type === 'link' ? resource.value : `/${resource.value.replaceAll('\\', '/')}`;
  window.open(target, '_blank', 'noopener,noreferrer');
};
</script>

<style scoped>
.work-detail-page {
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 100%);
}

.detail-breadcrumb {
  --el-text-color-regular: #777777;
  --el-color-primary: #047eff;
  font-size: 14px;
  line-height: 20px;
}

.detail-breadcrumb :deep(.el-breadcrumb__inner),
.detail-breadcrumb :deep(.el-breadcrumb__separator) {
  color: #777777;
  font-weight: 400;
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
.vote-action.is-disabled {
  opacity: 0.72;
}

.resource-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.resource-card:hover {
  box-shadow: 0 10px 22px rgba(34, 96, 170, 0.12);
  transform: translateY(-2px);
}

.resource-button {
  transition: filter 0.2s ease, transform 0.2s ease;
}

.resource-button:hover {
  filter: brightness(1.04);
  transform: translateY(-1px);
}

.video-dialog :deep(.el-dialog__body) {
  padding-top: 10px;
}

@media (max-width: 1023px) {
  .work-detail-page {
    padding-top: 20px;
  }
}

@media (max-width: 767px) {
  .work-detail-page article > div:first-child {
    height: 300px;
  }

  .work-detail-page article > div:first-child > div:nth-of-type(1) {
    left: 24px;
    top: 70px;
    right: 24px;
  }

  .work-detail-page article > div:first-child > div:nth-of-type(2) {
    left: 24px;
    right: auto;
    top: 166px;
    align-items: flex-start;
  }

  .detail-scroll {
    max-height: none;
    padding-left: 22px;
    padding-right: 22px;
  }

  .resource-card {
    align-items: flex-start;
    flex-wrap: wrap;
    padding-bottom: 18px;
    padding-top: 18px;
  }

  .resource-button {
    margin-left: 69px;
    margin-top: 14px;
  }
}
</style>
