<template>
  <section class="overflow-hidden bg-white">
    <div class="home-banner h-[500px] overflow-hidden bg-[#07148f]">
      <el-carousel height="500px" :interval="2500" trigger="click" arrow="never" indicator-position="inside">
        <el-carousel-item v-for="banner in banners" :key="banner.alt">
          <img :src="banner.image" :alt="banner.alt" class="h-full w-full object-cover" />
        </el-carousel-item>
      </el-carousel>
    </div>

    <div class="bg-[url('@/assets/images/bg_home_01.png')] bg-no-repeat [background-size:100%_100%] [background-position:top_center] pb-[58px] pt-[54px]">
      <div class="mx-auto max-w-[1200px]">
        <div class="grid items-center gap-[48px] lg:grid-cols-[520px_1fr]">
          <img :src="overviewImage" alt="基于大模型的校园生活智能体创新应用" class="w-full rounded-[2px]" />
          <div>
            <SectionTitle title="大赛介绍" />
            <p class="mt-[24px] text-[15px] text-[#5d6472] leading-[30px] indent-[2em]">
              为响应国家“人工智能+”行动建设战略部署，在国家教育数字化、AI 融合发展等政策指引下，AI人工智能正迈入场景化落地关键期。
              智能体作为融合大模型能力、链接技术与需求的核心载体，在教育、校园服务等领域的应用潜力加速释放。
            </p>
            <p class="mt-[14px] text-[15px] text-[#5d6472] leading-[30px] indent-[2em]">
              在此背景下，为进一步落实学校“提升师生数字素养与技能实施方案”，云南大学联合火山引擎举办首届“火山杯”AI应用创新大赛。
              赛事鼓励学生运用AI能力，在多元场景中探索技术创新应用，为数智化校园建设提供助力。
            </p>
          </div>
        </div>

        <div class="pt-[62px]">
          <SectionTitle title="赛程安排" center />
          <div class="mt-[30px] rounded-[12px] bg-white/92 px-[66px] py-[50px] shadow-[0_18px_45px_rgba(42,126,255,0.10)]">
            <div class="relative grid gap-[26px] md:grid-cols-4">
              <div class="absolute left-[11%] right-[11%] top-[150px] hidden border-t border-dashed border-[#1b8cff] md:block" />
              <div v-for="(item, index) in timeline" :key="item.title" class="relative text-center">
                <img :src="item.icon" :alt="item.title" class="h-[155px] w-full rounded-t-[12px] object-contain" />
                <img
                  v-if="index < timeline.length - 1"
                  :src="timelineArrow"
                  alt=""
                  class="absolute right-[-35px] top-[36px] hidden h-[50px] w-[50px] object-contain md:block"
                />
                <h3 class="mt-[18px] text-[18px] font-[700]" :class="item.active ? 'text-[#ff8832]' : 'text-[#1687ff]'">
                  {{ item.title }}
                </h3>
                <p class="mt-[6px] text-[16px] font-[400]" :class="item.active ? 'text-[#ff8832]' : 'text-[#1687ff]'">
                  {{ item.date }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="pt-[62px]">
          <SectionTitle title="参赛指南" center />
          <div class="mt-[32px] grid gap-[32px] md:grid-cols-3">
            <button
              v-for="guide in guides"
              :key="guide.title"
              type="button"
              class="group overflow-hidden relative rounded-[8px] border-0 bg-transparent p-0 text-left shadow-[0_10px_24px_rgba(37,116,210,0.08)] cursor-pointer"
              @click="openGuide(guide)"
            >
              <img :src="guide.image" :alt="guide.title" class="h-[180px] w-full object-cover transition-transform group-hover:scale-105" />
              <div class="absolute top-0 left-157 h-full w-[calc(100%-157px)] z-20 flex flex-col justify-center">
                <p class="text-[28px] font-[800] text-[#004385]">{{ guide.title }}</p>
                <div v-if="guide.hasBotton" class="w-full">
                  <p class="text-[16px] font-[400] text-[#666] mb-10">截止时间：6月19日</p>
                  <el-button type="primary" round>立即报名</el-button>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-[url('@/assets/images/bg_home_02.png')] bg-no-repeat [background-size:100%_100%] [background-position:top_center] py-[70px]">
      <div class="mx-auto max-w-[1200px]">
        <SectionTitle title="参赛作品" center />
        <div class="mt-[36px] grid gap-x-[32px] gap-y-[28px] sm:grid-cols-2 lg:grid-cols-4">
          <el-card @click="openWorkDetail(work)" v-for="work in works" :key="work.id" shadow class="home-work-card !rounded-[10px] border-0! cursor-pointer">
            <div class="relative">
              <span class="absolute left-[-1px] top-[-1px] z-10 rounded-br-[8px] rounded-tl-[8px] bg-[#1189ff] px-[14px] py-[5px] text-[16px] text-white font-[800]">
                {{ work.id }}
              </span>
              <img :src="work.image" :alt="work.title" class="h-[104px] rounded-t-[8px] w-full" />
            <div class="flex items-center ml-[60px] mr-[5px] h-full py-[5px] box-border w-[calc(100%-65px)] absolute top-0 right-0">
              <h2 class="relative z-10 line-clamp-4 w-full text-[18px] text-[#005cae] font-[800] leading-[24px]">
                {{ work.title }}
              </h2>
            </div>
            </div>
            <div class="px-[16px] py-[18px] text-[13px] text-[#5e6673] leading-[26px]">
              <p class="line-clamp-1">作品名称：{{ work.title }}</p>
              <p class="line-clamp-1">参赛队伍：{{ work.team }}</p>
              <p class="line-clamp-1">当前票数：{{ work.votes }}</p>
              <p class="line-clamp-1">浏览量：{{ work.views }}</p>
              <div class="mt-[12px] text-center">
                <el-button :type="work.voted ? 'info' : 'primary'" round plain :disabled="work.voted">
                  <i class="iconfont icon-toupiao text-[20px] mr-2"></i>
                  {{ work.voted ? '票已投完' : '我要投票' }}
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
        <div class="mt-[36px] text-center">
          <el-button type="primary" round @click="router.push('/works')">更多作品 》</el-button>
        </div>
      </div>
    </div>

    <div class="bg-white py-[70px]">
      <div class="mx-auto max-w-[1200px]">
        <SectionTitle title="新闻资讯" center />
        <div class="mt-[36px] grid gap-[44px] lg:grid-cols-[520px_1fr]">
          <div class="cursor-pointer" @click="router.push('/articlelist')">
            <img :src="homeNewsImage" alt="校园服务AI助手" class="h-[300px] cursor-pointer w-full rounded-[2px] bg-[#eefaff] object-contain" />
            <h3 class="mt-[22px] text-[18px] text-[#202734] font-[800] line-clamp-1 hover:text-[#1189ff]">校园服务AI助手云小智和智能体开发平台正式上线！</h3>
            <p class="mt-[12px] text-[14px] text-[#9aa1ad] leading-[26px] line-clamp-1">
              我将以 7×24 小时在线陪伴的方式，为老师和同学们提供便捷、贴心的校园服务。
            </p>
          </div>
          <div class="grid gap-[16px]">
            <button
              v-for="(news, index) in newsList"
              :key="news.day"
              type="button"
              class="news-item grid grid-cols-[74px_1fr] gap-[18px] border-0 bg-transparent p-0 text-left cursor-pointer"
              @click="router.push('/articlecontent')"
            >
              <div class="news-date h-[74px] text-center text-white">
                <div class="pt-[8px] text-[26px] font-[800] leading-[32px]">{{ news.day }}</div>
                <div class="text-[14px]">{{ news.month }}</div>
              </div>
              <div class="border-b border-[#eef0f4] pb-[12px]">
                <h3 class="text-[16px] text-[#333] font-[500] line-clamp-1">{{ news.title }}</h3>
                <p class="mt-[8px] line-clamp-2 text-[13px] text-[#9aa1ad] leading-[23px] line-clamp-2">{{ news.desc }}</p>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { h } from 'vue';
import { useRouter } from 'vue-router';
import { Suitcase } from '@element-plus/icons-vue';
import bannerHome from '@/assets/images/banner_1.png';
import overviewImage from '@/assets/images/img_home_overview.png';
import guideSignup from '@/assets/images/img_home_01.png';
import guideMaterials from '@/assets/images/img_home_02.png';
import guideEntry from '@/assets/images/img_home_03.png';
import homeNewsImage from '@/assets/images/banner_works_detail.png';
import titleIcon1 from '@/assets/images/img_title_01.png';
import titleIcon2 from '@/assets/images/img_title_02.png';
import titleIcon3 from '@/assets/images/img_title_03.png';
import titleIcon4 from '@/assets/images/img_title_04.png';
import titleIcon5 from '@/assets/images/img_title_05.png';
import timeline01 from '@/assets/images/img_timeline_01.png';
import timeline02 from '@/assets/images/img_timeline_02.png';
import timeline03 from '@/assets/images/img_timeline_03.png';
import timeline04 from '@/assets/images/img_timeline_04.png';
import timelineArrow from '@/assets/images/img_timeline_arrow.png';
import work01 from '@/assets/images/img_list01.png';
import work02 from '@/assets/images/img_list02.png';
import work03 from '@/assets/images/img_list03.png';
import work04 from '@/assets/images/img_list04.png';

const router = useRouter();
const defaultGuideUrl = 'https://itc.ynu.edu.cn/info/1013/1799.htm';
const signupUrl = import.meta.env.VITE_SIGNUP_URL || defaultGuideUrl;

const banners = [
  {
    image: bannerHome,
    alt: '2026年云南大学首届人工智能创新应用大赛',
  },
  {
    image: bannerHome,
    alt: '数启云大 智创未来',
  },
  {
    image: bannerHome,
    alt: '基于大模型的校园生活智能体创新应用',
  },
];

const SectionTitle = (props) =>
  h('div', { class: props.center ? 'flex justify-center' : '' }, [
    h('img', { src: sectionTitleImages[props.title] || titleIcon1, alt: props.title, class: 'h-auto w-[258px] object-contain' }),
  ]);

SectionTitle.props = {
  title: {
    type: String,
    required: true,
  },
  center: {
    type: Boolean,
    default: false,
  },
};

const sectionTitleImages = {
  大赛介绍: titleIcon1,
  赛程安排: titleIcon2,
  参赛指南: titleIcon5,
  参赛作品: titleIcon3,
  新闻资讯: titleIcon4,
};

const timeline = [
  { title: '大赛报名', date: '5月11日 - 6月19日', icon: timeline01, active: true },
  { title: 'HiAgent 平台实操培训', date: '5月23日 - 5月24日', icon: timeline02 },
  { title: '截止提交作品', date: '6月19日', icon: timeline03, active: true },
  { title: '作品评审', date: '6月下旬', icon: timeline04 },
];

const guides = [
  { title: '报名要求', image: guideSignup, externalUrl: signupUrl,hasBotton: false },
  { title: '课程资料', image: guideMaterials, path: '/materials',hasBotton: false },
  { title: '报名入口', image: guideEntry, externalUrl: signupUrl,hasBotton: true },
];

const workBackgrounds = ['bg-[#d6fbff]', 'bg-[#d7fff4]', 'bg-[#dce9ff]', 'bg-[#ffe4c8]'];

const works = Array.from({ length: 8 }, (_, index) => ({
  id: [12, 23, 28, 31, 1, 23, 28, 31][index],
  title: '智能体大赛020作品',
  team: 80,
  votes: 115,
  views: 1040,
  voted: index === 2 || index === 5,
  image: [work01, work02, work03, work04][index % 4],
  bg: workBackgrounds[index % 4],
}));

const newsList = [
  {
    day: '27',
    month: '2026-04',
    title: '云小智和智能体开发平台正式上线！',
    desc: '智能客服智能体是一种能帮助校园用户咨询解答服务，它可以通过理解用户问题，查询相关信息，生成合适回复。'
  },
  {
    day: '21',
    month: '2026-04',
    title: '校园服务AI助手云小智和智能体开发平台正式上线！',
    desc: '智能客服智能体是一种能帮助校园用户咨询解答服务，它可以通过理解用户问题，查询相关信息，生成合适回复。'
  },
  {
    day: '20',
    month: '2026-04',
    title: '云小智和智能体开发平台正式上线！',
    desc: '智能客服智能体是一种能帮助校园用户咨询解答服务，它可以通过理解用户问题，查询相关信息，生成合适回复。'
  },
  {
    day: '12',
    month: '2026-04',
    title: '校园服务AI助手云小智和智能体开发平台正式上线！',
    desc: '智能客服智能体是一种能帮助校园用户咨询解答服务，它可以通过理解用户问题，查询相关信息，生成合适回复。'
  },
];

const openWorkDetail = (work) => {
  router.push({
    path: '/content',
    query: {
      id: work.id,
    },
  });
};

const openGuide = (guide) => {
  if (guide.externalUrl) {
    window.open(guide.externalUrl, '_blank', 'noopener,noreferrer');
    return;
  }

  router.push(guide.path);
};

</script>

<style scoped>
.home-banner :deep(.el-carousel__indicators) {
  bottom: 24px;
}

.home-banner :deep(.el-carousel__indicator) {
  padding: 0 5px;
}

.home-banner :deep(.el-carousel__button) {
  width: 28px;
  height: 4px;
  border-radius: 999px;
  background-color: #ffffff;
  opacity: 1;
}

.home-banner :deep(.el-carousel__indicator.is-active .el-carousel__button) {
  width: 30px;
  background-color: #16d8ff;
}

.home-work-card :deep(.el-card__body) {
  padding: 0;
}

.news-date {
  background-color: #B1B1B1;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.news-date.is-active,
.news-item:hover .news-date {
  background-color: #1189ff;
  box-shadow: 0 8px 18px rgba(17, 137, 255, 0.18);
}

.news-item h3 {
  transition: color 0.2s ease;
}

.news-item:hover h3 {
  color: #1189ff;
}
</style>
