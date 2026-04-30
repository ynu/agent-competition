<template>
  <section class="article-content-page min-h-[calc(100vh-200px)] bg-white pb-[83px] pt-[27px]">
    <div class="mx-auto w-full max-w-[1200px] px-[16px] xl:px-0">
      <el-breadcrumb separator=">" class="article-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">
          <span class="inline-flex items-center gap-[7px] text-[#777]">
            <i class="iconfont icon-shouye gap-[7px] text-[#999999]"></i>
            您当前位置：<span class="text-[#047eff]">首页</span>
          </span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>内容页</el-breadcrumb-item>
      </el-breadcrumb>

      <article class="mt-[25px]">
        <header class="text-center">
          <h1 class="text-[30px] font-[800] leading-[38px] text-[#222]">{{ article.title }}</h1>
          <div class="mt-[14px] flex flex-wrap items-center justify-center gap-x-[48px] gap-y-[8px] text-[14px] leading-[22px] text-[#999]">
            <span>发布日期：{{ article.date }}</span>
            <span>发布人：{{ article.author }}</span>
          </div>
        </header>

        <div class="mt-[18px] border-t border-dashed border-[#b8b8b8] pt-[21px]">
          <img :src="article.image" :alt="article.title" class="mx-auto h-auto w-[540px] max-w-full object-contain" />

          <div class="article-body mx-auto mt-[37px] max-w-[1128px] text-[16px] leading-[28px] text-[#1f1f1f]">
            <p v-for="paragraph in article.paragraphs" :key="paragraph" class="mb-[15px] indent-[2em]">
              {{ paragraph }}
            </p>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { House } from '@element-plus/icons-vue';
import articleImage from '@/assets/images/img_article_yunxiaozhi.png';

const article = {
  title: '云小智和智能体开发平台正式上线！',
  date: '2026-04-10',
  author: 'admin',
  image: articleImage,
  paragraphs: [
    '您好，我是云小智，现在正式与全校师生见面！从今天起，我将以7×24小时在线陪伴的方式，为老师和同学们提供便捷、贴心的校园服务。无论是初来云大的新同学，还是在教学科研与管理一线忙碌的老师，我都希望成为您身边的智慧伙伴，让校园事务更简单、信息更清晰、服务更便捷。',
    '我可以随时回答校园相关问题、为您提供办事指引，甚至直接帮您线上办理部分业务（点击“业务导办”按钮即可）！目前我已具备以下能力，并将持续升级。',
    '校园服务全知道',
    '我可直接为您提供：学籍、教学、学位相关事务指引教职工人事与岗位管理相关咨询校内资产与实验设备使用、预约与管理说明财务报销、教育收费、缴费流程等操作指引我会告诉您去哪办、怎么办、需要哪些材料。选课、奖励、住宿生活、校内办事、图书馆……您学习与生活的每一步，我都懂。图书馆资源查询、数据库入口、论文获取、资源访问……我都能即时帮您查、帮您找。网络问题排查、应用系统帮助、常见账号问题解决……再也不用被系统入口在哪、为啥登不上所困扰。宿舍报修、场地预约、生活服务指引……让您的学习和工作环境都保持顺畅无忧。我不仅能告诉您办事的流程，还能带您办、替您办：上网认证密码重置校园邮箱密码管理企业微信邮箱别名修改校园邮箱别名添加和修改更多“即问即办”事项正在不断接入中……职称评审政策咨询本科教学成果奖报指引更多专属服务不断接入中……让繁琐信息不再占用您的宝贵时间。',
    '云小智希望成为您的智能助手云大很大、信息很多，但您不必独自摸索。如果某个问题“小智”暂时无法准确回答，问题会被记录，“小智”会尽快完善相关知识，努力在下一次为您提供更专业、准确的解答。希望“小智”能在学习、工作与生活的每一个需要帮助的时刻陪伴您、支持您，让您把时间留给更重要的事情。云小智，随时为您服务这意味着——我们不仅能使用“云小智”！您也可以创建属于自己的智能体！“云小智”就是基于该平台构建，是平台能力的示范应用。您可以在智能体开发平台上实现：一句话生成智能体生成一个作诗的智能体用生成的智能体作诗可视化拖拽式创建智能体，无需编程基础一键使用场景模板创建智能体，如学习助手、科研助手、生活助手等上传自己的知识文件构建专属知识库配置流程任务（自动问答、信息查询、业务处理）设定智能体角色与风格快速发布与分享，可服务自己、班级、实验室或部门我们已准备操作指南(https://itc.ynu.edu.cn/info/1013/1799.htm)，帮助您“即开即用”。',
  ],
};
</script>

<style scoped>
.article-breadcrumb {
  --el-text-color-regular: #777777;
  --el-color-primary: #047eff;
  font-size: 14px;
  line-height: 20px;
}

.article-breadcrumb :deep(.el-breadcrumb__inner),
.article-breadcrumb :deep(.el-breadcrumb__separator) {
  color: #777777;
  font-weight: 400;
}

.article-body p:last-child {
  margin-bottom: 0;
}

@media (max-width: 767px) {
  .article-content-page {
    padding-top: 20px;
  }

  .article-content-page article {
    margin-top: 22px;
  }

  .article-content-page header {
    text-align: left;
  }

  .article-content-page header > div {
    justify-content: flex-start;
  }

  .article-body {
    margin-top: 28px;
  }
}
</style>
