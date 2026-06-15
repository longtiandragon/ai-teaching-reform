<template>
  <div class="roadmap-scene">
    <!-- 噪点纹理 -->
    <div class="grain-overlay" aria-hidden="true"></div>

    <!-- 顶部：课程概览 -->
    <header class="roadmap-header">
      <div class="header-left">
        <span class="eyebrow-tag">
          <span class="tag-dot"></span>
          学习路线
        </span>
        <h1 class="header-title">
          <span class="title-line">{{ store.course?.title || 'SpringBoot 与农宝项目实训' }}</span>
        </h1>
        <p class="header-sub">{{ store.course?.subtitle || '选择关卡，在 AI 引导下完成学习任务。' }}</p>
      </div>

      <div class="header-right">
        <!-- 课程切换 -->
        <div class="course-switcher">
          <button
            v-for="course in store.courses"
            :key="course.id"
            type="button"
            :class="['switch-btn', { active: course.id === store.activeCourseId }]"
            @click="switchCourse(course.id)"
          >
            <span class="switch-label">{{ courseLabel(course.id) }}</span>
            <span class="switch-count">{{ course.lessons.length }} 关</span>
          </button>
        </div>

        <!-- 继续按钮 -->
        <button
          type="button"
          class="continue-btn"
          :disabled="!activeRouteItem"
          @click="enterRouteItem(activeRouteItem?.id)"
        >
          <span class="btn-text">继续学习</span>
          <span class="btn-icon">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
        </button>
      </div>
    </header>

    <!-- 主体：不对称 Bento Grid -->
    <div class="roadmap-body">
      <!-- 左侧：学习节奏概览 -->
      <aside class="rhythm-panel">
        <div class="panel-header">
          <span class="eyebrow-tag small">学习概览</span>
          <h3>学习节奏</h3>
        </div>

        <div class="rhythm-steps">
          <div v-for="(item, i) in flowItems" :key="i" class="rhythm-step">
            <span class="step-icon">{{ item.icon }}</span>
            <div class="step-content">
              <strong>{{ item.title }}</strong>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>

        <!-- 进度指示器 -->
        <div class="progress-indicator">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
          <span class="progress-text">{{ currentRouteIndex + 1 }} / {{ routeItems.length }}</span>
        </div>
      </aside>

      <!-- 右侧：关卡网格 -->
      <section class="lessons-section">
        <div class="section-header">
          <div>
            <span class="eyebrow-tag small">关卡路径</span>
            <h3>关卡路线</h3>
          </div>
          <span class="source-badge">{{ sourceLabel }}</span>
        </div>

        <!-- 不对称网格 -->
        <div class="lesson-grid">
          <article
            v-for="(lesson, index) in routeItems"
            :key="lesson.id"
            :class="[
              'lesson-card',
              `span-${getSpan(index)}`,
              {
                active: lesson.id === activeRouteItem?.id,
                done: lesson.status === 'completed',
                locked: lesson.status === 'locked',
              },
            ]"
            @click="enterRouteItem(lesson.id)"
          >
            <div class="card-inner">
              <div class="card-top">
                <span class="card-num">{{ String(index + 1).padStart(2, '0') }}</span>
                <span v-if="lesson.status === 'completed'" class="card-check">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M3 8l4 4 6-7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <span v-else-if="lesson.status === 'locked'" class="card-lock">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <rect x="3" y="6" width="8" height="6" rx="1.5" stroke="currentColor" stroke-width="1.2" />
                    <path d="M5 6V4.5a2 2 0 114 0V6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" />
                  </svg>
                </span>
              </div>

              <div class="card-body">
                <h4>{{ lesson.title }}</h4>
                <p>{{ lessonSubtitle(lesson) }}</p>
              </div>

              <div class="card-footer">
                <span class="card-tags">
                  <span v-for="tag in (lesson.tags || []).slice(0, 2)" :key="tag" class="tag">{{ routeTagLabel(tag) }}</span>
                </span>
                <span class="card-arrow">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
              </div>

              <!-- 已发布题目（可展开） -->
              <div v-if="publishedMap[lesson.id]?.length" class="card-questions" @click.stop>
                <button
                  type="button"
                  class="questions-toggle"
                  @click.stop="toggleQuestions(lesson.id)"
                >
                  <span class="toggle-icon">{{ expandedQuestions[lesson.id] ? '▼' : '▶' }}</span>
                  <span>{{ publishedMap[lesson.id].length }} 道已发布题目</span>
                </button>
                <div v-if="expandedQuestions[lesson.id]" class="questions-list">
                  <div
                    v-for="q in publishedMap[lesson.id]"
                    :key="q.id"
                    class="question-item"
                    @click.stop="enterQuestion(lesson.id, q.id)"
                  >
                    <span class="q-type-badge">{{ qTypeShort(q.type) }}</span>
                    <span class="q-stem-text">{{ q.stem }}</span>
                    <button class="q-start-btn" @click.stop="enterQuestion(lesson.id, q.id)">开始答题</button>
                  </div>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span>正在加载课程路线...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCourseStore } from '../stores/course'
import { useSessionStore } from '../stores/session'
import { ElMessage } from 'element-plus'
import { api, type Question } from '../api'

const router = useRouter()
const route = useRoute()
const store = useCourseStore()
const session = useSessionStore()
const loading = ref(true)

// Published questions state
const publishedMap = ref<Record<string, Question[]>>({})
const expandedQuestions = reactive<Record<string, boolean>>({})

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

const currentRouteIndex = computed(() => {
  const index = routeItems.value.findIndex((item) => item.id === (store.activeTaskId || store.activeLessonId))
  return index >= 0 ? index : 0
})

const activeRouteItem = computed(() => routeItems.value[currentRouteIndex.value] || routeItems.value[0])
const sourceLabel = computed(() => store.activeCourseId === 'nongbo-admin-project' ? '农宝项目' : 'SpringBoot 12 讲')
const progressPercent = computed(() => {
  if (!routeItems.value.length) return 0
  return Math.round(((currentRouteIndex.value + 1) / routeItems.value.length) * 100)
})

const flowItems = [
  { icon: '◎', title: '读需求', desc: '理解本关要解决的业务或课程任务。' },
  { icon: '◈', title: '找依据', desc: '从需求文档、接口、SQL 和源码中找证据。' },
  { icon: '◉', title: '补代码', desc: '只补关键片段，不生成完整项目。' },
  { icon: '◎', title: '自测', desc: '做题、看反馈，再提交实现检查。' },
  { icon: '◈', title: '复盘', desc: '总结为什么这么做和下一步问题。' },
]

onMounted(async () => {
  try {
    await store.load()
    const courseId = typeof route.query.course === 'string' ? route.query.course : ''
    if (courseId && courseId !== store.activeCourseId && store.courses.some((c) => c.id === courseId)) {
      await store.setCourse(courseId)
    }
    await store.loadLearningMap(session.currentUser?.id)
    await loadPublishedQuestions()
  } catch {
    ElMessage.error('课程路线加载失败，请确认后端服务已启动。')
  } finally {
    loading.value = false
  }
})

async function switchCourse(courseId: string) {
  await store.setCourse(courseId)
  await store.loadLearningMap(session.currentUser?.id)
  await loadPublishedQuestions()
  await router.replace({ path: '/student', query: { course: courseId } })
}

async function enterRouteItem(itemId?: string) {
  if (!itemId) return
  if (publishedMap.value[itemId]?.length) {
    toggleQuestions(itemId)
    return
  }
  await router.push({ name: 'task-workspace', params: { taskId: itemId } })
}

// ---------- Published Questions ----------
async function loadPublishedQuestions() {
  try {
    const res = await api.publishedByCourse(store.activeCourseId)
    const map: Record<string, Question[]> = {}
    for (const group of res.tasks) {
      map[group.taskId] = group.questions
    }
    publishedMap.value = map
  } catch { /* ignore */ }
}

function toggleQuestions(taskId: string) {
  expandedQuestions[taskId] = !expandedQuestions[taskId]
}

function enterQuestion(taskId: string, questionId: string) {
  router.push({ name: 'task-workspace', params: { taskId }, query: { questionId } })
}

function qTypeShort(type: string): string {
  const m: Record<string, string> = { single_choice: '单选', multi_choice: '多选', true_false: '判断', short_answer: '简答', code_fill: '填空' }
  return m[type] || type
}

function courseLabel(courseId: string) {
  return courseId === 'nongbo-admin-project' ? '农宝项目课' : 'SpringBoot 12 讲'
}

function lessonSubtitle(lesson: { id: string; title: string; tags: string[]; source?: string }) {
  if (store.activeCourseId === 'nongbo-admin-project') {
    return nongboMissionCopy(lesson)
  }
  const tags = (lesson.tags || []).filter((tag) => !/RAG|真实资料|课程资料/i.test(tag))
  return tags.length ? tags.slice(0, 3).map(routeTagLabel).join(' / ') : '课程讲解与实训练习'
}

function routeTagLabel(tag: string): string {
  const labels: Record<string, string> = {
    analysis: '资料分析',
    coding: '代码练习',
    text: '文字答案',
    java_snippet: 'Java 片段',
    sql: 'SQL 练习',
    api_design: '接口设计',
    lesson_practice: '章节练习',
    code_or_text: '代码或文字',
    project_document: '项目资料',
    'project-document': '项目资料',
    'course-standard': '课程标准',
    'course-material': '课程资料',
    waiting: '引导中',
    active: '进行中',
    locked: '未解锁',
    completed: '已完成',
    needs_revision: '需修改',
  }
  return labels[tag] || tag.replace(/_/g, ' ')
}

function nongboMissionCopy(lesson: { id: string; title: string; source?: string }) {
  const title = `${lesson.id} ${lesson.title}`.toLowerCase()
  if (/需求|架构/.test(title)) return '读懂业务需求，梳理后端分层与接口边界'
  if (/ioc|di|三层/.test(title)) return '从真实 Controller 入手，理解三层调用关系'
  if (/aop|事务|质量/.test(title)) return '结合补贴政策模块，识别日志、事务与异常处理'
  if (/登录|认证/.test(title)) return '对齐登录接口，理解参数校验、返回结构与令牌'
  if (/校验|异常/.test(title)) return '补全系统管理接口中的校验与异常反馈'
  if (/文件|上传/.test(title)) return '完成文件上传接口，明确资源地址和安全边界'
  if (/配置|mybatis-plus/.test(title)) return '检查 Spring Boot 配置与持久层连接'
  if (/mybatis|crud|农产品/.test(title)) return '对齐农产品表，完成增删改查关键逻辑'
  if (/动态|分页|行情|信贷/.test(title)) return '实现条件查询与分页，处理列表筛选场景'
  if (/综合|知识|内容/.test(title)) return '串联专家、图文课程与内容管理模块'
  if (/扩展|政策|服务/.test(title)) return '迁移同类业务模块，复用接口与服务模式'
  if (/vue|联调|复盘/.test(title)) return '完成前后端联调，复盘接口路径与返回结构'
  return '围绕真实农宝模块完成一个可验证的后端任务'
}

// 不对称网格：交替 span
function getSpan(index: number): string {
  const pattern = ['7', '5', '4', '4', '4', '8', '5', '7', '4', '4', '4', '8']
  return pattern[index % pattern.length]
}
</script>

<style scoped>
/* ─── 字体 ─── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* ─── 场景 ─── */
.roadmap-scene {
  min-height: 100dvh;
  background: #FFFBEB;
  font-family: 'Inter', 'Noto Sans SC', sans-serif;
  color: #0F172A;
  padding: 32px 40px 60px;
  position: relative;
}

.grain-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  pointer-events: none;
  opacity: 0.025;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 256px 256px;
}

/* ─── 顶部 ─── */
.roadmap-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 32px;
  margin-bottom: 48px;
  opacity: 0;
  transform: translateY(16px);
  animation: fadeUp 0.8s cubic-bezier(0.32, 0.72, 0, 1) 0.1s forwards;
}

.eyebrow-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px 5px 10px;
  border-radius: 100px;
  background: rgba(0, 0, 0, 0.03);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #78716C;
  margin-bottom: 16px;
}

.eyebrow-tag.small {
  padding: 3px 10px 3px 8px;
  font-size: 10px;
  margin-bottom: 10px;
}

.tag-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #D97706;
}

.header-title {
  margin: 0 0 10px;
  font-family: 'Playfair Display', serif;
  font-size: clamp(32px, 4vw, 48px);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: #0F172A;
}

.header-sub {
  margin: 0;
  font-size: 15px;
  color: #78716C;
  line-height: 1.6;
  max-width: 480px;
}

.header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 14px;
}

.course-switcher {
  display: flex;
  gap: 8px;
}

.switch-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  padding: 12px 18px;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 14px;
  background: transparent;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
}

.switch-btn:hover {
  border-color: rgba(217, 119, 6, 0.2);
  transform: translateY(-1px);
}

.switch-btn.active {
  border-color: #D97706;
  background: rgba(217, 119, 6, 0.04);
}

.switch-label {
  font-size: 13px;
  font-weight: 600;
  color: #0F172A;
}

.switch-count {
  font-size: 11px;
  color: #A8A29E;
}

.continue-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 12px 12px 22px;
  border: none;
  border-radius: 100px;
  background: #0F172A;
  color: #FFFBEB;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
}

.continue-btn:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.2);
}

.continue-btn:not(:disabled):active {
  transform: scale(0.98);
}

.continue-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-text {
  font-size: 14px;
  font-weight: 600;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 251, 235, 0.12);
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.continue-btn:not(:disabled):hover .btn-icon {
  transform: translate(2px, -1px);
}

/* ─── 主体 ─── */
.roadmap-body {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 32px;
  opacity: 0;
  transform: translateY(16px);
  animation: fadeUp 0.8s cubic-bezier(0.32, 0.72, 0, 1) 0.25s forwards;
}

/* ─── 左侧面板 ─── */
.rhythm-panel {
  padding: 24px;
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 100px;
  align-self: start;
}

.panel-header h3 {
  margin: 0 0 20px;
  font-family: 'Playfair Display', serif;
  font-size: 18px;
  font-weight: 600;
  color: #0F172A;
}

.rhythm-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 28px;
}

.rhythm-step {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.step-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(217, 119, 6, 0.08);
  color: #D97706;
  font-size: 12px;
  flex-shrink: 0;
}

.step-content strong {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 2px;
}

.step-content p {
  margin: 0;
  font-size: 12px;
  color: #A8A29E;
  line-height: 1.5;
}

.progress-indicator {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  height: 4px;
  border-radius: 2px;
  background: rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 2px;
  background: linear-gradient(90deg, #D97706, #F59E0B);
  transition: width 0.6s cubic-bezier(0.32, 0.72, 0, 1);
}

.progress-text {
  font-size: 12px;
  color: #A8A29E;
  font-weight: 500;
}

/* ─── 右侧关卡区 ─── */
.section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-family: 'Playfair Display', serif;
  font-size: 22px;
  font-weight: 600;
  color: #0F172A;
}

.source-badge {
  padding: 5px 12px;
  border-radius: 100px;
  background: rgba(217, 119, 6, 0.08);
  color: #D97706;
  font-size: 12px;
  font-weight: 600;
}

/* ─── 不对称网格 ─── */
.lesson-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 14px;
}

.lesson-card.span-7 { grid-column: span 7; }
.lesson-card.span-5 { grid-column: span 5; }
.lesson-card.span-8 { grid-column: span 8; }
.lesson-card.span-4 { grid-column: span 4; }

.lesson-card {
  border-radius: 18px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
  opacity: 0;
  transform: translateY(12px);
}

.lesson-card:nth-child(1) { animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.3s forwards; }
.lesson-card:nth-child(2) { animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.38s forwards; }
.lesson-card:nth-child(3) { animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.46s forwards; }
.lesson-card:nth-child(4) { animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.54s forwards; }
.lesson-card:nth-child(5) { animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.62s forwards; }
.lesson-card:nth-child(6) { animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.7s forwards; }
.lesson-card:nth-child(n+7) { animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.78s forwards; }

.card-inner {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 140px;
  padding: 20px;
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.015);
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
}

.lesson-card:hover .card-inner {
  border-color: rgba(217, 119, 6, 0.15);
  background: rgba(217, 119, 6, 0.02);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.04);
}

.lesson-card.active .card-inner {
  border-color: #D97706;
  background: rgba(217, 119, 6, 0.04);
}

.lesson-card.done .card-inner {
  border-color: rgba(125, 211, 168, 0.3);
  background: rgba(125, 211, 168, 0.04);
}

.lesson-card.locked {
  opacity: 0.5;
  cursor: default;
}

.lesson-card.locked .card-inner {
  border-style: dashed;
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-num {
  font-size: 12px;
  font-weight: 700;
  color: #A8A29E;
  font-family: 'Inter', monospace;
}

.lesson-card.active .card-num {
  color: #D97706;
}

.lesson-card.done .card-num {
  color: #7DD3A8;
}

.card-check {
  color: #7DD3A8;
}

.card-lock {
  color: #D4D4D4;
}

.card-body h4 {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 600;
  color: #0F172A;
  line-height: 1.3;
}

.card-body p {
  margin: 0;
  font-size: 12px;
  color: #A8A29E;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 14px;
}

.card-tags {
  display: flex;
  gap: 6px;
}

.tag {
  padding: 2px 8px;
  border-radius: 100px;
  background: rgba(0, 0, 0, 0.03);
  font-size: 10px;
  font-weight: 500;
  color: #A8A29E;
}

.card-arrow {
  color: #D4D4D4;
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.lesson-card:hover .card-arrow {
  transform: translate(2px, -1px);
  color: #D97706;
}

/* ─── 加载状态 ─── */
.loading-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: rgba(255, 251, 235, 0.9);
  color: #78716C;
  font-size: 14px;
  font-weight: 500;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-top-color: #D97706;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* ─── 已发布题目 ─── */
.card-questions {
  margin-top: 10px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
  padding-top: 8px;
}

.questions-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  color: #D97706;
  padding: 4px 0;
  font-family: inherit;
}

.toggle-icon {
  font-size: 9px;
  transition: transform 0.2s;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 6px;
  max-height: 180px;
  overflow-y: auto;
}

.question-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border-radius: 8px;
  background: rgba(217, 119, 6, 0.03);
  cursor: pointer;
  transition: background 0.2s;
}

.question-item:hover {
  background: rgba(217, 119, 6, 0.08);
}

.q-type-badge {
  flex-shrink: 0;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(217, 119, 6, 0.1);
  color: #D97706;
  font-size: 10px;
  font-weight: 600;
}

.q-stem-text {
  flex: 1;
  font-size: 12px;
  color: #0F172A;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.q-start-btn {
  flex-shrink: 0;
  padding: 2px 8px;
  border: 1px solid rgba(217, 119, 6, 0.2);
  border-radius: 6px;
  background: transparent;
  color: #D97706;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.q-start-btn:hover {
  background: rgba(217, 119, 6, 0.1);
  border-color: #D97706;
}

/* ─── 动画 ─── */
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ─── 响应式 ─── */
@media (max-width: 1024px) {
  .roadmap-scene {
    padding: 24px 24px 48px;
  }

  .roadmap-body {
    grid-template-columns: 1fr;
  }

  .rhythm-panel {
    position: static;
  }

  .lesson-grid {
    grid-template-columns: repeat(8, 1fr);
  }

  .lesson-card.span-7,
  .lesson-card.span-8 { grid-column: span 8; }
  .lesson-card.span-5 { grid-column: span 5; }
  .lesson-card.span-4 { grid-column: span 4; }
}

@media (max-width: 768px) {
  .roadmap-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-right {
    align-items: flex-start;
    width: 100%;
  }

  .course-switcher {
    width: 100%;
  }

  .switch-btn {
    flex: 1;
  }

  .lesson-grid {
    grid-template-columns: 1fr;
  }

  .lesson-card.span-7,
  .lesson-card.span-8,
  .lesson-card.span-5,
  .lesson-card.span-4 {
    grid-column: span 1;
  }
}
</style>
