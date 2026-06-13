<template>
  <main class="roadmap-page">
    <div v-if="loading" class="roadmap-loading">
      <LoaderCircle :size="24" class="spin" />
      <span>正在加载课程路线...</span>
    </div>

    <section class="roadmap-hero">
      <div class="hero-copy">
        <p class="eyebrow">Student Learning Route</p>
        <h2>{{ store.course?.title || 'SpringBoot 与农博项目实训' }}</h2>
        <p>{{ store.course?.subtitle || '先选择关卡，再进入专注学习工作台。' }}</p>
      </div>

      <div class="hero-actions">
        <div class="course-tabs" aria-label="课程切换">
          <button
            v-for="course in store.courses"
            :key="course.id"
            type="button"
            :class="{ active: course.id === store.activeCourseId }"
            @click="switchCourse(course.id)"
          >
            <span>{{ courseLabel(course.id) }}</span>
            <small>{{ course.lessons.length }} 关</small>
          </button>
        </div>
        <button type="button" class="continue-btn" :disabled="!activeRouteItem" @click="enterRouteItem(activeRouteItem?.id)">
          <PlayCircle :size="18" />
          继续当前关
        </button>
      </div>
    </section>

    <section class="route-layout">
      <article class="overview-panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Overview</p>
            <h3>学习节奏</h3>
          </div>
          <strong>{{ currentRouteIndex + 1 }}/{{ routeItems.length || 1 }}</strong>
        </div>

        <div class="flow-list">
          <div v-for="item in flowItems" :key="item.title" class="flow-item">
            <component :is="item.icon" :size="18" />
            <div>
              <b>{{ item.title }}</b>
              <span>{{ item.copy }}</span>
            </div>
          </div>
        </div>
      </article>

      <section class="lesson-board">
        <div class="board-head">
          <div>
            <p class="eyebrow">Learning Path</p>
            <h3>关卡路线</h3>
          </div>
          <span>{{ sourceLabel }}</span>
        </div>

        <div class="lesson-grid">
          <article
            v-for="(lesson, index) in routeItems"
            :key="lesson.id"
            class="lesson-card"
            :class="{ active: lesson.id === activeRouteItem?.id, done: lesson.status === 'completed', locked: lesson.status === 'locked' }"
          >
            <button type="button" @click="enterRouteItem(lesson.id)">
              <span class="lesson-no">{{ String(index + 1).padStart(2, '0') }}</span>
              <span class="lesson-main">
                <b>{{ lesson.title }}</b>
                <small>{{ lessonSubtitle(lesson) }}</small>
              </span>
              <ArrowRight :size="18" />
            </button>
          </article>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowRight,
  BookOpenCheck,
  ClipboardCheck,
  Code2,
  LoaderCircle,
  MessageSquareText,
  PlayCircle,
  SearchCheck,
} from 'lucide-vue-next'
import { useCourseStore } from '../stores/course'

interface FlowItem {
  title: string
  copy: string
  icon: Component
}

const router = useRouter()
const route = useRoute()
const store = useCourseStore()
const loading = ref(true)

const lessons = computed(() => store.course?.lessons || [])
const routeItems = computed(() => {
  if (store.learningMap?.tasks?.length) {
    return store.learningMap.tasks.map((task) => ({
      id: task.id,
      title: task.title,
      tags: [task.type, task.required_artifact_type],
      source: task.status,
      status: task.status,
    }))
  }
  return lessons.value.map((lesson) => ({ ...lesson, status: lesson.status }))
})
const currentLessonIndex = computed(() => {
  const index = lessons.value.findIndex((lesson) => lesson.id === store.activeLessonId)
  return index >= 0 ? index : 0
})
const currentRouteIndex = computed(() => {
  const index = routeItems.value.findIndex((item) => item.id === (store.activeTaskId || store.activeLessonId))
  return index >= 0 ? index : 0
})
const activeLesson = computed(() => lessons.value[currentLessonIndex.value] || lessons.value[0])
const activeRouteItem = computed(() => routeItems.value[currentRouteIndex.value] || routeItems.value[0])
const sourceLabel = computed(() => store.activeCourseId === 'nongbo-admin-project' ? '农博项目' : 'SpringBoot 12 讲')

const flowItems: FlowItem[] = [
  { title: '读需求', copy: '先看本关要解决的业务或课程任务。', icon: BookOpenCheck },
  { title: '找依据', copy: '从课程标准、需求、SQL 和源码中找证据。', icon: SearchCheck },
  { title: '补代码', copy: '只补关键片段，不生成完整项目。', icon: Code2 },
  { title: '自测', copy: '做题、看反馈，再提交实现检查。', icon: ClipboardCheck },
  { title: '复盘', copy: '留下为什么这么做和下一步问题。', icon: MessageSquareText },
]

onMounted(async () => {
  await store.load()
  const courseId = typeof route.query.course === 'string' ? route.query.course : ''
  if (courseId && courseId !== store.activeCourseId && store.courses.some((course) => course.id === courseId)) {
    await store.setCourse(courseId)
  }
  await store.loadLearningMap()
  loading.value = false
})

async function switchCourse(courseId: string) {
  await store.setCourse(courseId)
  await store.loadLearningMap()
  await router.replace({ path: '/student', query: { course: courseId } })
}

async function enterRouteItem(itemId?: string) {
  if (!itemId) return
  if (store.learningMap?.tasks.some((task) => task.id === itemId)) {
    await store.loadTask(itemId)
    await router.push({
      name: 'student-learn',
      params: { lessonId: store.activeLessonId || activeLesson.value?.id },
      query: { course: store.activeCourseId, task: itemId },
    })
    return
  }
  await store.loadLesson(itemId)
  await router.push({
    name: 'student-learn',
    params: { lessonId: itemId },
    query: { course: store.activeCourseId },
  })
}

function courseLabel(courseId: string) {
  return courseId === 'nongbo-admin-project' ? '农博项目课' : 'SpringBoot 12 讲'
}

function lessonSubtitle(lesson: { id: string; title: string; tags: string[]; source?: string }) {
  if (store.activeCourseId === 'nongbo-admin-project') {
    return nongboMissionCopy(lesson)
  }
  const tags = (lesson.tags || []).filter((tag) => !/RAG|真实资料|课程资料/i.test(tag))
  return tags.length ? tags.slice(0, 3).join(' / ') : '课程讲解与实训练习'
}

function nongboMissionCopy(lesson: { id: string; title: string; source?: string }) {
  const title = `${lesson.id} ${lesson.title}`.toLowerCase()
  const source = (lesson.source || '').toLowerCase()
  if (/需求|架构/.test(title)) return '读懂业务需求，梳理后端分层与接口边界'
  if (/ioc|di|三层/.test(title)) return '从真实 Controller 入手，理解三层调用关系'
  if (/aop|事务|质量/.test(title)) return '结合补贴政策模块，识别日志、事务与异常处理'
  if (/登录|认证/.test(title) || /auth|login/.test(source)) return '对齐登录接口，理解参数校验、返回结构与令牌'
  if (/校验|异常/.test(title) || /systemmanagement/.test(source)) return '补全系统管理接口中的校验与异常反馈'
  if (/文件|上传/.test(title) || /fileupload/.test(source)) return '完成文件上传接口，明确资源地址和安全边界'
  if (/配置|mybatis-plus/.test(title) || /application/.test(source)) return '检查 Spring Boot 配置与持久层连接'
  if (/mybatis|crud|农产品/.test(title) || /farmproduce/.test(source)) return '对齐农产品表，完成增删改查关键逻辑'
  if (/动态|分页|行情|信贷/.test(title) || /creditloan/.test(source)) return '实现条件查询与分页，处理列表筛选场景'
  if (/综合|知识|内容/.test(title) || /expert/.test(source)) return '串联专家、图文课程与内容管理模块'
  if (/扩展|政策|服务/.test(title)) return '迁移同类业务模块，复用接口与服务模式'
  if (/vue|联调|复盘/.test(title) || /request/.test(source)) return '完成前后端联调，复盘接口路径与返回结构'
  return '围绕真实农博模块完成一个可验证的后端任务'
}
</script>

<style scoped>
.roadmap-page {
  min-height: calc(100vh - 82px);
  padding: 18px;
  background: #edf3f8;
}

.roadmap-hero,
.overview-panel,
.lesson-board {
  border: 1px solid #dbe5f1;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.97);
  box-shadow: 0 10px 28px rgba(30, 48, 72, 0.07);
}

.roadmap-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 24px;
  align-items: end;
  padding: 22px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #2672d9;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.hero-copy h2 {
  margin: 0;
  color: #17243a;
  font-size: 26px;
  line-height: 1.25;
}

.hero-copy p:last-child {
  max-width: 760px;
  margin: 10px 0 0;
  color: #52647f;
  font-size: 14px;
  line-height: 1.7;
}

.hero-actions {
  display: grid;
  gap: 10px;
  min-width: 360px;
}

.course-tabs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.course-tabs button,
.continue-btn,
.lesson-card button {
  border: 1px solid #d8e3f0;
  border-radius: 7px;
  background: #fff;
  color: #31425c;
  cursor: pointer;
  font-weight: 900;
}

.course-tabs button {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 11px 12px;
  font-size: 13px;
}

.course-tabs button.active {
  border-color: #2d7be8;
  background: #eaf3ff;
  color: #1d5fbf;
}

.course-tabs small {
  color: #74839a;
}

.continue-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  background: #2d7be8;
  color: #fff;
}

.continue-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.route-layout {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 14px;
  margin-top: 14px;
}

.overview-panel,
.lesson-board {
  overflow: hidden;
}

.panel-head,
.board-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid #e8eef6;
}

.panel-head h3,
.board-head h3 {
  margin: 0;
  color: #18263d;
  font-size: 18px;
}

.panel-head strong,
.board-head span {
  border-radius: 999px;
  padding: 5px 9px;
  background: #e8f6ef;
  color: #108556;
  font-size: 12px;
  font-weight: 900;
}

.flow-list {
  display: grid;
  gap: 10px;
  padding: 14px;
}

.flow-item {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
  padding: 12px;
  border: 1px solid #e1e9f4;
  border-radius: 7px;
  background: #f8fbff;
  color: #2672d9;
}

.flow-item b,
.flow-item span {
  display: block;
}

.flow-item b {
  color: #1b2a44;
  font-size: 14px;
}

.flow-item span {
  margin-top: 3px;
  color: #5d6f87;
  font-size: 12px;
  line-height: 1.5;
}

.lesson-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  padding: 14px;
}

.lesson-card button {
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr) 20px;
  gap: 10px;
  align-items: center;
  width: 100%;
  min-height: 92px;
  padding: 12px;
  text-align: left;
}

.lesson-card button:hover {
  border-color: #9dc5fb;
  background: #f5f9ff;
}

.lesson-card.locked button {
  cursor: pointer;
  opacity: 0.76;
  border-style: dashed;
}

.lesson-card.active button {
  border-color: #2d7be8;
  background: #eaf3ff;
}

.lesson-card.done .lesson-no {
  background: #e6f5ee;
  color: #108556;
}

.lesson-no {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 7px;
  background: #eef3f8;
  color: #637188;
  font-size: 13px;
  font-weight: 900;
}

.lesson-card.active .lesson-no {
  background: #2d7be8;
  color: #fff;
}

.lesson-main {
  min-width: 0;
}

.lesson-main b,
.lesson-main small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lesson-main b {
  color: #20314b;
  font-size: 14px;
  line-height: 1.35;
}

.lesson-main small {
  display: -webkit-box;
  margin-top: 5px;
  color: #74839a;
  font-size: 11px;
  line-height: 1.45;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.roadmap-loading {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 12px;
  background: rgba(238, 243, 248, 0.92);
  color: #2672d9;
  font-weight: 900;
}

.spin {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1180px) {
  .lesson-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 860px) {
  .roadmap-hero,
  .route-layout {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    min-width: 0;
  }
}

@media (max-width: 620px) {
  .roadmap-page {
    padding: 10px;
  }

  .lesson-grid,
  .course-tabs {
    grid-template-columns: 1fr;
  }
}
</style>
