<template>
  <main class="coach-workbench">
    <div v-if="loading" class="loading-screen">
      <LoaderCircle :size="24" class="spin" />
      <span>正在加载课程工作台...</span>
    </div>

    <aside v-if="false" class="course-rail">
      <section class="work-panel course-card">
        <p class="eyebrow">Course Track</p>
        <h2>{{ store.course?.title || '真实课程实训' }}</h2>
        <p class="rail-subtitle">{{ store.course?.subtitle || '围绕真实资料完成逐步练习' }}</p>

        <div class="course-switcher" aria-label="课程切换">
          <button
            v-for="course in store.courses"
            :key="course.id"
            type="button"
            :class="{ active: course.id === store.activeCourseId }"
            @click="switchCourse(course.id)"
          >
            <span>{{ courseLabel(course.id) }}</span>
            <small>{{ course.lessons.length }} 节</small>
          </button>
        </div>
      </section>

      <section class="work-panel path-card">
        <div class="section-head compact">
          <div>
            <p class="eyebrow">Learning Path</p>
            <h3>关卡路线</h3>
          </div>
          <strong>{{ currentLessonIndex + 1 }}/{{ lessons.length || 1 }}</strong>
        </div>

        <div class="lesson-list">
          <button
            v-for="(lesson, index) in lessons"
            :key="lesson.id"
            type="button"
            class="lesson-item"
            :class="{ active: lesson.id === store.activeLessonId, done: index < currentLessonIndex }"
            @click="store.loadLesson(lesson.id)"
          >
            <span class="lesson-index">{{ String(index + 1).padStart(2, '0') }}</span>
            <span class="lesson-copy">
              <strong>{{ lesson.title }}</strong>
              <small>{{ lesson.source || lesson.tags.join(' / ') }}</small>
            </span>
            <ChevronRight :size="16" />
          </button>
        </div>
      </section>
    </aside>

    <section class="guide-column">
      <section class="work-panel mission-hero">
        <div>
          <p class="eyebrow">Current Mission</p>
          <h2>{{ store.task?.title || store.lesson?.title || '请选择章节' }}</h2>
          <p>{{ store.task?.goal || store.lesson?.summary || '读取真实课程资料后开始本节任务。' }}</p>
        </div>
        <div class="hero-meta">
          <span>{{ sourceLabel }}</span>
          <span>{{ ragStatus }}</span>
          <RouterLink class="focus-back" to="/student" aria-label="返回关卡路线">
            <ArrowLeft :size="20" />
            <span>返回路线</span>
          </RouterLink>
        </div>
      </section>

      <nav class="step-ribbon" aria-label="学习步骤">
        <button
          v-for="task in runtimeTasks"
          :key="task.id"
          type="button"
          :class="{ active: task.id === store.activeTaskId, completed: task.status === 'completed', locked: task.status === 'locked' }"
          @click="selectRuntimeTask(task.id)"
        >
          <component :is="taskIcon(task.type)" :size="15" />
          <span>{{ task.title }}</span>
        </button>
      </nav>

      <section class="work-panel task-card">
        <div class="section-head">
          <div>
            <p class="eyebrow">{{ store.task?.type || activeStep.label }}</p>
            <h3>{{ store.task?.title || activeStep.title }}</h3>
          </div>
          <span class="step-badge">{{ activeTaskStatusLabel }}</span>
        </div>

        <div v-if="activeStepKey === 'read'" class="read-brief">
          <article class="brief-block primary">
            <p class="eyebrow">Mission Brief</p>
            <h4>{{ store.task?.goal || store.lesson?.practice.title || store.lesson?.title }}</h4>
            <p>{{ store.task?.instruction || store.lesson?.practice.description || store.lesson?.summary }}</p>
          </article>

          <div class="brief-grid">
            <article class="brief-block">
              <BookOpenCheck :size="18" />
              <div>
                <h4>先理解什么</h4>
                <ul>
                  <li v-for="item in readObjectives" :key="item">{{ item }}</li>
                </ul>
              </div>
            </article>

            <article class="brief-block">
              <ClipboardCheck :size="18" />
              <div>
                <h4>最后交付什么</h4>
                <ul>
                  <li v-for="item in readDeliverables" :key="item">{{ item }}</li>
                </ul>
              </div>
            </article>
          </div>

          <details class="source-details">
            <summary>查看资料依据</summary>
            <div class="source-summary">
              <article v-for="source in readableSources" :key="source.label" class="source-chip-card">
                <b>{{ source.label }}</b>
                <span>{{ source.copy }}</span>
              </article>
            </div>
          </details>
        </div>

        <div v-else-if="activeStepKey === 'evidence'" class="evidence-grid">
          <article>
            <h4>学习目标</h4>
            <ul>
              <li v-for="item in taskObjectives" :key="item">{{ item }}</li>
            </ul>
          </article>
          <article>
            <h4>验收依据</h4>
            <ul>
              <li v-for="item in taskRubricLabels" :key="item">{{ item }}</li>
            </ul>
          </article>
          <article class="source-note">
            <h4>资料依据</h4>
            <div class="source-summary compact">
              <article v-for="source in readableSources" :key="source.label" class="source-chip-card">
                <b>{{ source.label }}</b>
                <span>{{ source.copy }}</span>
              </article>
            </div>
          </article>
        </div>

        <div v-else-if="activeStepKey === 'patch'" class="step-note">
          <Code2 :size="20" />
          <div>
            <h4>只补当前步骤需要的片段</h4>
            <p>
              右侧代码块是只读参考。学生只需要在“补全区”提交本节涉及的关键方法、配置、SQL 或说明，
              不提交完整项目目录，重点说明当前步骤的关键实现。
            </p>
          </div>
        </div>

        <div v-else-if="activeStepKey === 'test'" class="step-note">
          <ClipboardCheck :size="20" />
          <div>
            <h4>先自检，再提交检查</h4>
            <p>
              右侧题目用于确认关键概念和实现依据。完成选择后点击“完成自检”，再提交你的补全代码和反思说明。
            </p>
          </div>
        </div>

        <div v-else class="step-note">
          <MessageSquare :size="20" />
          <div>
            <h4>复盘时要留下证据</h4>
            <p>
              说明你改了哪里、为什么这么改、对应哪条课程或项目资料。系统会结合资料依据给出反馈。
            </p>
          </div>
        </div>
      </section>

      <section class="work-panel tutor-panel">
        <div class="section-head compact">
          <div>
            <p class="eyebrow">Learning Coach</p>
            <h3><Sparkles :size="17" /> 引用式助教</h3>
          </div>
          <span class="live-pill" :class="{ online: store.health?.deepseek_live }">
            {{ store.health?.deepseek_live ? '助教在线' : '助教未连接' }}
          </span>
        </div>

        <div ref="chatScrollRef" class="chat-scroll">
          <article
            v-for="message in messages"
            :key="message.id"
            class="message"
            :class="message.role"
          >
            <div class="markdown-body" v-html="renderMarkdown(message.content || message.status || '')"></div>

            <details v-if="message.citations?.length && !message.streaming" class="citation-list">
              <summary>查看引用资料（{{ message.citations.length }}）</summary>
              <article
                v-for="citation in message.citations"
                :key="`${citation.kind}-${citation.source}-${citation.title}`"
                class="citation-card"
              >
                <span>{{ citationKindLabel(citation.kind) }}</span>
                <b>{{ citation.title }}</b>
                <small>{{ readablePath(citation.source) }}</small>
                <div class="citation-snippet markdown-body" v-html="renderMarkdown(citation.snippet)"></div>
              </article>
            </details>

            <div v-if="message.streaming" class="typing-status">
              <LoaderCircle :size="14" class="spin" />
              {{ message.status || '正在基于引用资料组织回答...' }}
            </div>
          </article>
        </div>

        <div class="prompt-bar">
          <button
            v-for="prompt in prompts"
            :key="prompt.label"
            type="button"
            @click="ask(prompt.text, prompt.mode)"
          >
            {{ prompt.label }}
          </button>
        </div>

        <form class="chat-input" @submit.prevent="ask(question, 'coach')">
          <input v-model="question" :placeholder="questionPlaceholder" />
          <button type="submit" :disabled="asking" aria-label="发送问题">
            <LoaderCircle v-if="asking" :size="18" class="spin" />
            <Send v-else :size="18" />
          </button>
        </form>
      </section>
    </section>

    <aside class="lab-column">
      <nav class="lab-tabs" aria-label="学习工具">
        <button type="button" :class="{ active: activeLabTab === 'code' }" @click="activeLabTab = 'code'">
          <Terminal :size="15" />
          参考片段
        </button>
        <button type="button" :class="{ active: activeLabTab === 'patch' }" @click="activeLabTab = 'patch'">
          <Code2 :size="15" />
          补全区
        </button>
        <button type="button" :class="{ active: activeLabTab === 'check' }" @click="activeLabTab = 'check'">
          <ClipboardCheck :size="15" />
          自检
        </button>
        <button type="button" :class="{ active: activeLabTab === 'feedback', hasFeedback: feedback }" @click="activeLabTab = 'feedback'">
          <MessageSquare :size="15" />
          评价
        </button>
      </nav>

      <section v-show="activeLabTab === 'code'" class="work-panel code-card">
        <div class="section-head compact">
          <div>
            <p class="eyebrow">Read Only Code</p>
            <h3><Terminal :size="17" /> 参考片段</h3>
          </div>
          <span class="code-lang">{{ codeLanguage }}</span>
        </div>

        <div class="code-meta">
          <span>{{ readablePath(store.lesson?.source || '') }}</span>
          <span>{{ codeLines.length }} 行</span>
        </div>

        <pre class="code-view" :class="{ empty: isTemplateEmpty }"><code><span
          v-for="line in codeLines"
          :key="line.number"
          class="code-line"
          :class="{ todo: line.isTodo }"
        ><span class="line-no">{{ line.number }}</span><span class="line-code">{{ line.text || ' ' }}</span></span></code></pre>
      </section>

      <section v-show="activeLabTab === 'patch'" class="work-panel patch-card">
        <div class="section-head compact">
          <div>
            <p class="eyebrow">Patch Area</p>
            <h3>补全区</h3>
          </div>
          <span class="step-badge">当前步骤</span>
        </div>

        <label class="field-block">
          <span>代码 / 配置 / SQL 片段</span>
          <textarea v-model="studentCode" :placeholder="codePlaceholder"></textarea>
        </label>

        <label class="field-block">
          <span>实现说明 / 复盘证据</span>
          <textarea v-model="reflection" :placeholder="reflectionPlaceholder"></textarea>
        </label>
      </section>

      <section v-show="activeLabTab === 'check'" class="work-panel check-card">
        <div class="section-head compact">
          <div>
            <p class="eyebrow">Self Check</p>
            <h3>验收自检</h3>
          </div>
          <strong class="progress-count">{{ answeredCount }}/{{ quizBank.length }}</strong>
        </div>

        <div v-if="quizLoading" class="quiz-loading">
          <LoaderCircle :size="16" class="spin" />
          正在读取题库...
        </div>

        <div v-else class="quiz-list">
          <article v-for="(quiz, index) in quizBank" :key="quiz.id" class="quiz-item">
            <p>{{ index + 1 }}. {{ quiz.question }}</p>
            <div class="option-grid">
              <button
                v-for="option in quiz.options"
                :key="option.key"
                type="button"
                :class="optionClass(quiz, option)"
                @click="selectOption(quiz, option)"
              >
                <b>{{ option.key }}</b>
                <span>{{ option.text }}</span>
              </button>
            </div>
            <small v-if="selfChecked && quiz.explanation" class="quiz-explain">
              {{ quiz.explanation }}
            </small>
          </article>
        </div>

        <div v-if="selfChecked" class="self-check-result">
          <CheckCircle2 :size="16" />
          自检正确 {{ selfCheckScore.correct }}/{{ selfCheckScore.total }}，继续把证据补完整。
        </div>

        <div class="action-row">
          <button type="button" class="btn-ghost" :disabled="!answeredCount" @click="finishSelfCheck">
            完成自检
          </button>
          <button type="button" class="btn-primary" :disabled="submitting || !canSubmitPractice" @click="submitPractice">
            <LoaderCircle v-if="submitting" :size="17" class="spin" />
            <span>{{ submitting ? '正在检查...' : '提交实现检查' }}</span>
          </button>
        </div>
      </section>

      <section v-show="activeLabTab === 'feedback'" class="work-panel feedback-panel">
        <div class="section-head compact">
          <div>
            <p class="eyebrow">Review</p>
            <h3>评价与建议</h3>
          </div>
          <span class="step-badge">{{ feedback ? `${feedback.score} 分` : '等待提交' }}</span>
        </div>

        <div v-if="feedback" class="feedback-result">
          <div class="score-box">
            <strong>{{ feedback.score }}</strong>
            <span>综合评分</span>
          </div>
          <div class="feedback-copy">
            <div class="markdown-body" v-html="renderMarkdown(feedback.ai_comment)"></div>
            <div v-if="feedback.improvements?.length" class="feedback-tags">
              <span v-for="item in feedback.improvements" :key="item">{{ item }}</span>
            </div>
            <div v-if="feedback.rubricScores?.length" class="rubric-list">
              <article v-for="item in feedback.rubricScores" :key="item.criterion_id" :class="{ passed: item.passed }">
                <b>{{ item.score }}</b>
                <div>
                  <strong>{{ item.name }}</strong>
                  <span>{{ item.reason }}</span>
                </div>
              </article>
            </div>
          </div>
        </div>

        <div v-else class="empty-feedback">
          <MessageSquare :size="22" />
          <h4>先完成自检，再提交你的实现说明</h4>
          <p>选择题用于阶段自检；提交补全代码或复盘说明后，系统会给出综合反馈。</p>
        </div>
      </section>
    </aside>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch, type Component } from 'vue'
import {
  ArrowLeft,
  BookOpenCheck,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  Code2,
  FileText,
  LoaderCircle,
  MessageSquare,
  Search,
  Send,
  Sparkles,
  Target,
  Terminal,
} from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api, type Citation, type Question, type QuestionOption, type RubricScore } from '../api'
import { useCourseStore } from '../stores/course'
import { useSessionStore } from '../stores/session'
import { renderMarkdown } from '../utils/markdown'

type StepKey = 'read' | 'evidence' | 'patch' | 'test' | 'reflect'
type LabTab = 'code' | 'patch' | 'check' | 'feedback'
type PromptMode = 'hint' | 'explain' | 'check' | 'citation' | 'coach'

interface StepCard {
  key: StepKey
  label: string
  title: string
  badge: string
  icon: Component
}

interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  status?: string
  streaming?: boolean
}

interface QuizOption {
  key: string
  text: string
}

interface QuizItem {
  id: string
  question: string
  options: QuizOption[]
  answer: string
  explanation: string | null
  type: string
}

interface PracticeFeedbackResult {
  score: number
  ai_comment: string
  strengths?: string[]
  improvements?: string[]
  rubricScores?: RubricScore[]
  passed?: boolean
}

const store = useCourseStore()
const session = useSessionStore()
const route = useRoute()
const loading = ref(true)
const activeStepKey = ref<StepKey>('read')
const activeLabTab = ref<LabTab>('code')
const question = ref('')
const code = ref('')
const studentCode = ref('')
const reflection = ref('')
const asking = ref(false)
const submitting = ref(false)
const quizLoading = ref(false)
const selfChecked = ref(false)
const selectedOptions = ref<Record<string, string>>({})
const quizBank = ref<QuizItem[]>([])
const feedback = ref<PracticeFeedbackResult | null>(null)
const chatScrollRef = ref<HTMLElement | null>(null)
const messages = ref<ChatMessage[]>([])

const lessons = computed(() => store.course?.lessons || [])
const runtimeTasks = computed(() => store.learningMap?.tasks?.length ? store.learningMap.tasks : [])
const currentLessonIndex = computed(() => {
  const index = lessons.value.findIndex((lesson) => lesson.id === store.activeLessonId)
  return index >= 0 ? index : 0
})

const stepCards = computed<StepCard[]>(() => [
  { key: 'read', label: '读需求', title: '先读清楚本节要完成什么', badge: '1/5', icon: FileText },
  { key: 'evidence', label: '找依据', title: '从课程资料或真实项目里找证据', badge: '2/5', icon: Search },
  { key: 'patch', label: '补代码', title: '只写当前步骤需要的关键片段', badge: '3/5', icon: Code2 },
  { key: 'test', label: '自测', title: '用题目和运行证据检查实现', badge: '4/5', icon: ClipboardCheck },
  { key: 'reflect', label: '复盘', title: '解释修改依据和下一步问题', badge: '5/5', icon: Target },
])

const activeStep = computed(() => stepCards.value.find((step) => step.key === activeStepKey.value) || stepCards.value[0])
const activeRuntimeTask = computed(() => runtimeTasks.value.find((task) => task.id === store.activeTaskId))
const activeTaskLocked = computed(() => activeRuntimeTask.value?.status === 'locked')
const activeTaskStatusLabel = computed(() => {
  const status = activeRuntimeTask.value?.status
  if (status === 'completed') return `${activeRuntimeTask.value?.score ?? 100} 分`
  if (status === 'needs_revision') return '需要修改'
  if (status === 'locked') return '预览中'
  return store.task?.required_artifact_type || activeStep.value.badge
})

const sourceLabel = computed(() =>
  store.activeCourseId === 'nongbo-admin-project' ? '农博项目' : 'SpringBoot 课程资料',
)

const ragStatus = computed(() => {
  const backend = store.health?.rag_backend || '资料库'
  const chunks = store.health?.rag_chunks
  return chunks ? `${backend} / ${chunks} chunks` : backend
})

const readObjectives = computed(() => {
  if (store.task) return [store.task.goal, store.task.scenario].filter(Boolean).slice(0, 4)
  const objectives = store.lesson?.objectives || []
  if (objectives.length) return objectives.slice(0, 4)
  return [store.lesson?.summary || '先读清本关对应的业务场景、课程知识点和真实资料来源。']
})

const readDeliverables = computed(() => {
  if (store.task) return [
    `提交类型：${store.task.required_artifact_type}`,
    `解锁分数：${store.task.unlock_policy?.minScore ?? 70}`,
    ...taskRubricLabels.value.slice(0, 2),
  ]
  const checklist = store.lesson?.practice.checklist || []
  if (checklist.length) return checklist.slice(0, 4)
  return ['提交当前步骤需要的关键代码、配置、SQL 或说明片段', '写清楚实现依据和自测结果']
})

const taskObjectives = computed(() => {
  if (store.task) return [store.task.goal, store.task.scenario, store.task.instruction].filter(Boolean)
  return store.lesson?.objectives || []
})

const taskRubricLabels = computed(() => {
  if (store.task?.rubrics?.length) {
    return store.task.rubrics.map((rubric) => `${rubric.required ? '必选' : '加分'}：${rubric.name}`)
  }
  return store.lesson?.practice.checklist || []
})

const prompts = computed(() => {
  if (store.activeCourseId === 'nongbo-admin-project') {
    return [
      { label: '只给提示', mode: 'hint' as PromptMode, text: '我卡在当前模块了，请只给下一步提示，不要生成完整文件。' },
      { label: '解释源码', mode: 'explain' as PromptMode, text: '请结合真实源码解释这个模块的 Controller、Service 和返回结构。' },
      { label: '检查片段', mode: 'check' as PromptMode, text: '请检查我右侧补全区的实现思路是否符合农博项目代码风格。' },
      { label: '找依据', mode: 'citation' as PromptMode, text: '请列出本模块接口、字段或需求依据，必须给引用。' },
    ]
  }
  return [
    { label: '只给提示', mode: 'hint' as PromptMode, text: '我卡在本节练习了，请只给一到两步提示，不要直接给完整答案。' },
    { label: '解释重点', mode: 'explain' as PromptMode, text: '请解释本节最关键的概念和调用链，并结合课程资料。' },
    { label: '检查思路', mode: 'check' as PromptMode, text: '请检查我的练习思路是否满足本节验收标准。' },
    { label: '追问题', mode: 'coach' as PromptMode, text: '请基于本节内容生成一道进阶追问，用来确认我真的理解了。' },
  ]
})

const questionPlaceholder = computed(() =>
  store.activeCourseId === 'nongbo-admin-project'
    ? '围绕当前农博模块提问，AI 只按引用资料辅导...'
    : '围绕当前 SpringBoot 章节提问，AI 只给分步引导...',
)

const codePlaceholder = computed(() =>
  store.activeCourseId === 'nongbo-admin-project'
    ? '只粘贴当前模块要补的 Controller 方法、Service 调用、Entity 字段或 Mapper 片段。'
    : '只粘贴本节要补的 Java/XML/SQL/配置片段，或命令输出。'
)

const reflectionPlaceholder = computed(() =>
  store.activeCourseId === 'nongbo-admin-project'
    ? '说明你的实现对应哪个真实接口、数据库字段、需求规格或源码风格。'
    : '说明你的实现依据来自哪一讲、哪条验收点，以及你如何验证。'
)

const isTemplateEmpty = computed(() => !code.value.trim() || code.value.includes('未提供固定代码模板'))

const codeLanguage = computed(() => {
  const source = store.lesson?.source || ''
  const text = code.value
  if (source.endsWith('.vue') || /<template>|defineStore|router/i.test(text)) return 'Vue'
  if (source.endsWith('.sql') || /CREATE TABLE|SELECT|INSERT|UPDATE/i.test(text)) return 'SQL'
  if (source.endsWith('.xml') || /<project|<dependency|pom\.xml/i.test(text)) return 'XML'
  if (/public class|@RestController|package com\./.test(text)) return 'Java'
  return 'Text'
})

const codeLines = computed(() => {
  const fallback = '当前章节没有可展示的完整代码模板。请根据任务说明，在下方补全区提交你的关键片段。'
  const raw = code.value.trim() ? code.value : fallback
  return raw.replace(/\t/g, '  ').split(/\r?\n/).map((text, index) => ({
    number: index + 1,
    text,
    isTodo: /TODO|todo|待实现|补全|请根据|未提供/.test(text),
  }))
})

const answeredCount = computed(() => quizBank.value.filter((quiz) => selectedOptions.value[quiz.id]).length)
const selfCheckScore = computed(() => {
  const total = quizBank.value.length
  const correct = quizBank.value.filter((quiz) => selectedOptions.value[quiz.id] === normalizeAnswer(quiz.answer)).length
  return { total, correct }
})

const canSubmitPractice = computed(() => !activeTaskLocked.value && (studentCode.value.trim().length > 0 || reflection.value.trim().length > 0))

const readableSources = computed(() => {
  const content = store.lesson?.content || ''
  const cards = new Map<string, { label: string; copy: string }>()
  if (/课程标准对应/.test(content)) {
    cards.set('课程标准', { label: '课程标准', copy: lessonStandardUnit(content) || '对应本关的课程标准项目与能力要求' })
  }
  if (/Controller\.java|ServiceImpl\.java|entity\/|mapper\//i.test(content)) {
    cards.set('真实源码', { label: '真实源码', copy: '来自农博后台的 Controller、Service、Entity 或 Mapper 片段' })
  }
  if (/nb_database\.sql|CREATE TABLE|数据库规划/.test(content)) {
    cards.set('数据库设计', { label: '数据库设计', copy: '使用表结构、字段和数据库规划作为实现依据' })
  }
  if (/接口规范|需求分析|需求规格/.test(content)) {
    cards.set('项目文档', { label: '项目文档', copy: '来自接口规范、需求分析或技术方案文档' })
  }
  if (cards.size === 0) {
    cards.set('课程资料', { label: '课程资料', copy: readablePath(store.lesson?.source || '当前关卡资料') })
  }
  return Array.from(cards.values())
})

onMounted(async () => {
  try {
    if (!session.currentUser) await session.load()
    await store.load()
    const courseId = typeof route.query.course === 'string' ? route.query.course : ''
    const lessonId = typeof route.params.lessonId === 'string' ? route.params.lessonId : ''
    if (courseId && courseId !== store.activeCourseId) {
      await store.setCourse(courseId)
    }
    if (lessonId && lessonId !== store.activeLessonId) {
      await store.loadLesson(lessonId)
    }
    await store.loadLearningMap(session.currentUser?.id)
    const taskId = typeof route.query.task === 'string' ? route.query.task : ''
    if (taskId && store.learningMap?.tasks.some((task) => task.id === taskId)) {
      await store.loadTask(taskId)
    }
    resetWorkspaceState()
    await loadQuiz()
  } finally {
    loading.value = false
  }
})

watch(
  () => [store.activeCourseId, store.activeLessonId],
  async () => {
    await store.loadLearningMap(session.currentUser?.id)
    resetWorkspaceState()
    activeStepKey.value = 'read'
    await loadQuiz()
  },
)

async function switchCourse(courseId: string) {
  await store.setCourse(courseId)
  await store.loadLearningMap(session.currentUser?.id)
}

async function selectRuntimeTask(taskId: string) {
  await store.loadTask(taskId)
  activeStepKey.value = 'read'
  activeLabTab.value = 'patch'
  if (runtimeTasks.value.find((task) => task.id === taskId)?.status === 'locked') {
    ElMessage.info('该任务还未解锁，可以先预览目标和评分标准；提交验收需要先通过前一关。')
  }
}

function taskIcon(type: string): Component {
  if (/database|sql/i.test(type)) return Search
  if (/coding|controller|mapper|service/i.test(type)) return Code2
  if (/reflection|test/i.test(type)) return Target
  return FileText
}

function setStep(step: StepKey) {
  activeStepKey.value = step
  const tabByStep: Record<StepKey, LabTab> = {
    read: 'code',
    evidence: 'code',
    patch: 'patch',
    test: 'check',
    reflect: feedback.value ? 'feedback' : 'patch',
  }
  activeLabTab.value = tabByStep[step]
}

function resetWorkspaceState() {
  code.value = store.lesson?.practice.template || ''
  studentCode.value = ''
  reflection.value = ''
  selectedOptions.value = {}
  selfChecked.value = false
  feedback.value = null
  activeLabTab.value = 'code'
  question.value = ''
  messages.value = [
    {
      id: Date.now(),
      role: 'assistant',
      content: `我会围绕《${store.task?.title || store.lesson?.title || '当前任务'}》做引用式辅导。\n\n你可以先读任务，再在右侧补全关键片段。需要帮助时我只给提示、解释或检查，不会替你生成完整项目。`,
    },
  ]
}

async function loadQuiz() {
  if (!store.activeCourseId || !store.activeLessonId) return
  const courseId = store.activeCourseId
  const lessonId = store.activeLessonId
  quizLoading.value = true
  try {
    const res = await api.questions(courseId, lessonId)
    const questions = res.questions.length ? res.questions.slice(0, 4).map(toQuizItem) : fallbackQuestions(courseId, lessonId)
    if (courseId === store.activeCourseId && lessonId === store.activeLessonId) {
      quizBank.value = questions
    }
  } catch {
    quizBank.value = fallbackQuestions(courseId, lessonId)
  } finally {
    quizLoading.value = false
  }
}

function toQuizItem(q: Question): QuizItem {
  return {
    id: q.id,
    question: q.stem,
    options: q.options?.length ? q.options.map(toQuizOption) : trueFalseOptions(),
    answer: normalizeAnswer(q.answer),
    explanation: q.explanation,
    type: q.type,
  }
}

function toQuizOption(option: QuestionOption): QuizOption {
  return {
    key: option.key.toUpperCase(),
    text: option.text,
  }
}

function trueFalseOptions(): QuizOption[] {
  return [
    { key: 'A', text: '正确' },
    { key: 'B', text: '错误' },
  ]
}

function fallbackQuestions(courseId: string, lessonId: string): QuizItem[] {
  if (courseId === 'nongbo-admin-project') {
    return [
      makeQuiz('fallback-nb-1', '补全农博后台接口时，最先要对齐哪类真实依据？', [
        '需求规格、接口路径、数据库字段和已有源码风格',
        '先让 AI 生成完整模块，再慢慢改',
        '只看页面标题，不看后端代码',
        '只保证类名看起来像 Java',
      ], 'A', '真实项目练习必须先找接口、字段和源码依据。'),
      makeQuiz('fallback-nb-2', '农博项目后端返回值应优先保持哪种风格？', [
        'com.movie.nbspringproduct.common.Result<T>',
        '直接返回字符串',
        '返回任意 Map，字段随意',
        '让前端猜返回结构',
      ], 'A', '该项目已有统一 Result<T> 返回结构。'),
      makeQuiz('fallback-nb-3', 'Service 调用命名最应该贴近哪种项目约定？', [
        'IxxxService / xxxService，并通过已有实现类承接业务',
        '在 Controller 里直接写全部 SQL',
        '每个接口新建一个无关工具类',
        '把业务逻辑放到 Vue 页面里',
      ], 'A', '练习目标是延续真实项目的分层和命名。'),
      makeQuiz('fallback-nb-4', '联调失败时，较合理的排查顺序是什么？', [
        '请求前缀、接口路径、参数、返回结构、控制台错误',
        '先重装所有依赖',
        '只改页面颜色',
        '删除后端异常信息',
      ], 'A', '前后端联调要先检查契约和错误链路。'),
    ]
  }

  if (lessonId.includes('maven')) {
    return [
      makeQuiz('fallback-maven-1', '补全 pom.xml 时，dependency 的 scope 主要影响什么？', [
        '依赖参与编译、测试、运行或打包的范围',
        'Controller 的 URL 路径',
        '数据库字段长度',
        'Vue 组件生命周期',
      ], 'A', 'Maven scope 控制依赖在不同生命周期中的可见范围。'),
      makeQuiz('fallback-maven-2', '提交 Maven 练习时，哪类证据最有价值？', [
        'pom.xml 关键依赖、测试类和 mvn test/package 输出',
        '只说“我理解了”',
        '只截图项目目录',
        '让 AI 生成完整项目',
      ], 'A', '验收需要看到配置、测试与运行结果。'),
      makeQuiz('fallback-maven-3', 'JUnit 依赖被错误写成 compile 可能带来什么问题？', [
        '测试依赖进入主程序依赖范围，增大体积并可能冲突',
        '一定能提升运行速度',
        '会自动创建 Controller',
        '会自动连接数据库',
      ], 'A', '测试框架一般应限制在 test 范围。'),
      makeQuiz('fallback-maven-4', '本节 AI 帮助最适合做什么？', [
        '解释依赖、生命周期和报错，而不是生成完整工程',
        '直接替学生写完整文件夹',
        '绕过测试步骤',
        '删除所有配置',
      ], 'A', '助教应促进理解和排错。'),
    ]
  }

  const checklist = store.lesson?.practice.checklist || []
  return (checklist.length ? checklist.slice(0, 4) : ['能说明实现依据', '能提交关键片段', '能给出验证结果', '能解释失败场景']).map(
    (item, index) =>
      makeQuiz(
        `fallback-common-${index}`,
        `围绕“${item}”，最适合作为提交证据的是哪一类？`,
        ['关键代码/配置 + 运行或测试结果', '只写一句完成了', '只让 AI 给完整答案', '不说明资料依据'],
        'A',
        '实训验收要看实现片段、运行证据和资料依据。',
      ),
  )
}

function makeQuiz(id: string, questionText: string, options: string[], answer: string, explanation: string): QuizItem {
  return {
    id,
    question: questionText,
    options: options.map((text, index) => ({ key: String.fromCharCode(65 + index), text })),
    answer,
    explanation,
    type: 'single_choice',
  }
}

function selectOption(quiz: QuizItem, option: QuizOption) {
  selectedOptions.value = { ...selectedOptions.value, [quiz.id]: option.key }
}

async function finishSelfCheck() {
  if (!session.currentUser?.id || session.currentUser.role !== 'student') {
    ElMessage.warning('请先在右上角选择学生身份，再保存自检记录。')
    return
  }
  selfChecked.value = true
  const score = selfCheckScore.value.total
    ? Math.round((selfCheckScore.value.correct / selfCheckScore.value.total) * 100)
    : 0
  await api.submitSelfCheck({
    student_id: session.currentUser.id,
    course_id: store.activeCourseId,
    lesson_id: store.activeLessonId,
    score,
    correct: selfCheckScore.value.correct,
    total: selfCheckScore.value.total,
    answers: quizBank.value.map((quiz) => ({
      question_id: quiz.id,
      question: quiz.question,
      selected: selectedOptions.value[quiz.id] || '',
      answer: normalizeAnswer(quiz.answer),
      correct: selectedOptions.value[quiz.id] === normalizeAnswer(quiz.answer),
    })),
  })
  ElMessage.success('自检结果已保存到我的记录。')
}

function optionClass(quiz: QuizItem, option: QuizOption) {
  const selected = selectedOptions.value[quiz.id] === option.key
  const correct = normalizeAnswer(quiz.answer) === option.key
  return {
    selected,
    correct: selfChecked.value && correct,
    wrong: selfChecked.value && selected && !correct,
  }
}

async function ask(value: string, mode: PromptMode) {
  const text = value.trim()
  if (!text || asking.value) return

  if (isLowInformationQuestion(text)) {
    messages.value.push({ id: Date.now(), role: 'user', content: text })
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: '我还不能判断你想问什么。请把问题写具体一点，例如：“这个模块的需求范围是什么？”或“Controller 和 Service 分别负责什么？”',
    })
    question.value = ''
    await scrollChatToBottom()
    return
  }

  asking.value = true
  messages.value.push({ id: Date.now(), role: 'user', content: text })
  const assistantId = Date.now() + 1
  messages.value.push({
    id: assistantId,
    role: 'assistant',
    content: '',
    citations: [],
    status: '正在检索当前课程资料...',
    streaming: true,
  })
  question.value = ''
  await scrollChatToBottom()

  try {
    let streamFailed = false
    await api.streamChat(
      {
        course_id: store.activeCourseId,
        lesson_id: store.activeLessonId,
        question: buildTutorPrompt(text, mode),
        mode: 'student',
      },
      {
        onStatus(data) {
          updateAssistant(assistantId, { status: data.message || '正在处理...' })
          scrollChatToBottom()
        },
        onCitations() {
          // Citations are displayed only after the answer is complete.
        },
        onDelta(delta) {
          const msg = messages.value.find((item) => item.id === assistantId)
          if (msg) msg.content += delta
          scrollChatToBottom()
        },
        onDone(data) {
          updateAssistant(assistantId, {
            streaming: false,
            status: '',
            citations: sanitizeCitations(data?.citations || []),
          })
          scrollChatToBottom()
        },
        onError(data) {
          streamFailed = true
          updateAssistant(assistantId, {
            streaming: false,
            status: '',
            content: formatAiFailure(data),
          })
          scrollChatToBottom()
        },
      },
    )
    const msg = messages.value.find((item) => item.id === assistantId)
    if (msg && !streamFailed) {
      msg.streaming = false
      if (!msg.content.trim()) msg.content = '**AI 回答为空**'
    }
  } catch (error) {
    updateAssistant(assistantId, {
      streaming: false,
      status: '',
      content: formatAiFailure(error),
    })
  } finally {
    asking.value = false
    await scrollChatToBottom()
  }
}

function buildTutorPrompt(text: string, mode: PromptMode) {
  const guardrails: Record<PromptMode, string> = {
    hint: '只给一到两步提示，不能输出完整项目、完整文件夹或完整答案。',
    explain: '解释概念、调用链和资料依据，可以给小片段，但不要生成完整工程。',
    check: `检查学生当前补全片段，指出缺口和下一步。学生片段：\n${studentCode.value || '尚未填写'}`,
    citation: '优先列出引用依据和来源，不能无引用发挥。',
    coach: '采用分步辅导方式回答，不要代替学生完成整个项目。',
  }
  return [
    `当前课程：${store.course?.title || store.activeCourseId}`,
    `当前章节：${store.lesson?.title || store.activeLessonId}`,
    `助教约束：${guardrails[mode]}`,
    `学生问题：${text}`,
  ].join('\n')
}

function isLowInformationQuestion(text: string) {
  const normalized = text.trim().toLowerCase()
  if (!normalized) return true
  if (/^[\d\W_]+$/.test(normalized)) return true
  if (/^(test|测试|111+|123+|aaa+|你好|hello|hi)$/i.test(normalized)) return true
  const knownTerms = [
    'ioc', 'di', 'aop', 'bean', 'spring', 'springboot', 'controller', 'service', 'mapper',
    'mybatis', 'mysql', 'sql', 'rest', 'api', 'jwt', 'token', 'session', 'vue', 'pinia',
    '事务', '注入', '依赖', '控制反转', '切面', '日志', '接口', '字段', '数据库', '登录',
    '认证', '分页', '查询', '新增', '修改', '删除', '上传', '配置', '异常', '项目',
  ]
  const hasKnownTerm = knownTerms.some((term) => normalized.includes(term))
  const latinOnly = /^[a-z0-9_+-]+$/i.test(normalized)
  if (latinOnly && !hasKnownTerm) return true
  const meaningful = normalized.match(/[a-zA-Z\u4e00-\u9fff]/g) || []
  return meaningful.length < 2 && !hasKnownTerm
}

function updateAssistant(id: number, patch: Partial<ChatMessage>) {
  const message = messages.value.find((item) => item.id === id)
  if (message) Object.assign(message, patch)
}

function sanitizeCitations(citations: Citation[]) {
  const seen = new Set<string>()
  return citations
    .filter((citation) => citation && citation.snippet && Number(citation.score || 0) > 0)
    .filter((citation) => {
      const key = `${citation.kind}-${citation.source}-${citation.title}-${citation.snippet.slice(0, 32)}`
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
    .slice(0, 3)
}

async function scrollChatToBottom() {
  await nextTick()
  if (chatScrollRef.value) {
    chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight
  }
}

async function submitPractice() {
  if (submitting.value) return
  if (!session.currentUser?.id || session.currentUser.role !== 'student') {
    ElMessage.warning('请先在右上角选择学生身份，再提交检查。')
    return
  }
  if (!studentCode.value.trim() && !reflection.value.trim()) {
    ElMessage.warning('请先填写补全片段或实现说明，再提交检查。')
    return
  }
  if (activeTaskLocked.value) {
    ElMessage.warning('当前任务还未解锁。你可以预览任务，但需要先通过前一关后再提交验收。')
    return
  }

  submitting.value = true
  try {
    const answers = quizBank.value.map((quiz) => {
      const key = selectedOptions.value[quiz.id] || '未选择'
      const option = quiz.options.find((item) => item.key === key)
      return `${quiz.question} => ${key}${option ? `. ${option.text}` : ''}`
    }).join('\n')

    if (!store.task) {
      await store.loadLearningMap(session.currentUser.id)
    }
    if (!store.task) {
      throw new Error('当前课程任务未加载，无法提交检查。')
    }
    const result = await api.aiCheck({
      courseLineId: store.activeCourseId,
      moduleId: store.task.module_id,
      taskId: store.task.id,
      studentId: session.currentUser.id,
      artifactType: store.task.required_artifact_type,
      studentInput: [
        studentCode.value.trim(),
        `自检：\n${answers || '未完成题目自检'}`,
        `说明：${reflection.value || '未填写'}`,
      ].filter(Boolean).join('\n\n'),
      chatHistory: messages.value.map((item) => ({ role: item.role, content: item.content })).slice(-8),
    })
    feedback.value = {
      score: result.score,
      ai_comment: result.reply,
      strengths: result.strengths,
      improvements: [
        ...(result.problems || []).map((item) => `${item.message}${item.suggestion ? `：${item.suggestion}` : ''}`),
        ...(result.nextActions || []),
      ],
      rubricScores: result.rubricScores,
      passed: result.passed,
    }
    await store.loadLearningMap(session.currentUser.id)
    activeLabTab.value = 'feedback'
    if (result.nextTaskUnlocked) {
      ElMessage.success('本关已通过，下一关已解锁。')
    } else if (result.passed) {
      ElMessage.success('本关已通过。')
    }
  } catch (error) {
    ElMessage.error(errorMessage(error))
    feedback.value = {
      score: 0,
      ai_comment: formatPlainFailure(error),
      improvements: ['检查暂时不可用，请稍后重试或先根据自检结果修改。'],
    }
    activeLabTab.value = 'feedback'
  } finally {
    submitting.value = false
  }
}

function normalizeAnswer(answer: string) {
  const match = answer.trim().toUpperCase().match(/[A-D]/)
  return match?.[0] || answer.trim().toUpperCase()
}

function courseLabel(courseId: string) {
  return courseId === 'nongbo-admin-project' ? '农博项目课' : 'SpringBoot 12 讲'
}

function citationKindLabel(kind: string) {
  const labels: Record<string, string> = {
    concept: '知识点',
    lesson: '章节',
    practice: '实训',
    'course-material': '课程资料',
    'project-document': '项目文档',
    'database-schema': '库表结构',
    standard: '职业标准',
    'requirement-spec': '需求规格',
  }
  return labels[kind] || '引用'
}

function lessonStandardUnit(content: string) {
  const match = content.match(/课程标准对应：(.+)/)
  return match?.[1]?.trim() || ''
}

function readablePath(path: string) {
  if (!path) return '当前关卡资料'
  const normalized = path.replace(/\\/g, '/')
  const filename = normalized.split('/').filter(Boolean).pop() || normalized
  if (filename.endsWith('.java')) return filename.replace('.java', ' 类')
  if (filename.endsWith('.md')) return filename.replace('.md', '')
  if (filename.endsWith('.doc')) return '课程标准'
  if (filename.endsWith('.docx')) return '需求规格说明书'
  if (filename.endsWith('.sql')) return '数据库脚本'
  return filename
}

function formatAiFailure(error: unknown) {
  const plain = formatPlainFailure(error)
  if (/请把问题写具体一点|问题写具体|不能判断/.test(plain)) {
    return plain
  }
  return [
    '**暂时无法完成 AI 回复**',
    '',
    plain,
    '',
    '你可以先继续完成自检和代码补全；稍后再试一次提交检查。',
  ].join('\n')
}

function formatPlainFailure(error: unknown) {
  const message = errorMessage(error)
  if (/literal_error|Input should be|body|loc|Pydantic|validation/i.test(message)) {
    return '请求参数没有通过校验。我已经保留了你的问题，请刷新后重试；如果仍然出现，请检查当前课程和关卡是否加载完成。'
  }
  if (/DeepSeek|API|timeout|超时|模型|503|401|429/i.test(message)) {
    return `智能助教暂时不可用。${message}`
  }
  return message || '请求没有成功完成，请稍后再试。'
}

function errorMessage(error: unknown) {
  if (typeof error === 'object' && error && 'response' in error) {
    const data = (error as any).response?.data
    return stringifyErrorDetail(data?.detail || data?.message || (error as any).message || data)
  }
  const raw = error instanceof Error ? error.message : '请求失败。'
  try {
    const parsed = JSON.parse(raw)
    return stringifyErrorDetail(parsed.detail || parsed.message || parsed)
  } catch {
    return stringifyErrorDetail(raw)
  }
}

function stringifyErrorDetail(value: unknown): string {
  if (typeof value === 'string') return value
  if (value == null) return '请求失败。'
  if (Array.isArray(value)) {
    const messages = value
      .map((item) => {
        if (typeof item === 'string') return item
        if (item && typeof item === 'object' && 'msg' in item) return String((item as any).msg)
        return ''
      })
      .filter(Boolean)
    if (messages.length) return messages.join('；')
  }
  if (typeof value === 'object' && 'msg' in value) {
    return String((value as any).msg)
  }
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return '请求失败。'
  }
}
</script>

<style scoped>
.coach-workbench {
  display: grid;
  grid-template-columns: minmax(520px, 1fr) minmax(380px, 480px);
  gap: 12px;
  height: calc(100vh - 82px);
  padding: 12px;
  overflow: hidden;
  background: #edf3f8;
}

.course-rail,
.guide-column,
.lab-column {
  min-height: 0;
}

.course-rail {
  display: none;
}

.guide-column,
.lab-column {
  display: grid;
  gap: 12px;
}

.course-rail {
  grid-template-rows: auto minmax(0, 1fr);
}

.guide-column {
  grid-template-rows: auto auto minmax(150px, 0.65fr) minmax(300px, 1.35fr);
}

.lab-column {
  grid-template-rows: auto minmax(0, 1fr);
}

.lab-tabs {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  min-width: 0;
}

.lab-tabs button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 0;
  min-height: 40px;
  border: 1px solid #d8e3f0;
  border-radius: 7px;
  background: #fff;
  color: #53647d;
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
}

.lab-tabs button.active {
  border-color: #2d7be8;
  background: #2d7be8;
  color: #fff;
}

.lab-tabs button.hasFeedback:not(.active) {
  border-color: #f2d58f;
  background: #fff9e8;
  color: #9a5a00;
}

.work-panel {
  min-width: 0;
  min-height: 0;
  border: 1px solid #dbe5f1;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.97);
  box-shadow: 0 10px 28px rgba(30, 48, 72, 0.07);
  overflow: hidden;
}

.eyebrow {
  margin: 0 0 5px;
  color: #2672d9;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.course-card {
  padding: 16px;
}

.course-card h2,
.mission-hero h2 {
  margin: 0;
  color: #17243a;
  font-size: 18px;
  line-height: 1.35;
}

.rail-subtitle {
  margin: 8px 0 14px;
  color: #5f7088;
  font-size: 13px;
  line-height: 1.55;
}

.course-switcher {
  display: grid;
  gap: 8px;
}

.course-switcher button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
  padding: 10px 11px;
  border: 1px solid #d7e2ef;
  border-radius: 7px;
  background: #f8fbff;
  color: #31425c;
  cursor: pointer;
  font-size: 13px;
  font-weight: 800;
}

.course-switcher button.active {
  border-color: #2d7be8;
  background: #eaf3ff;
  color: #1d5fbf;
}

.course-switcher small {
  color: #74839a;
  font-size: 11px;
  font-weight: 700;
}

.path-card {
  display: flex;
  flex-direction: column;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid #e8eef6;
}

.section-head.compact {
  align-items: center;
  padding: 12px 14px;
}

.section-head h3 {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin: 0;
  color: #18263d;
  font-size: 16px;
  line-height: 1.35;
}

.section-head strong {
  color: #2672d9;
  font-size: 13px;
}

.lesson-list {
  display: grid;
  gap: 7px;
  padding: 10px;
  overflow: auto;
}

.lesson-item {
  display: grid;
  grid-template-columns: 30px minmax(0, 1fr) 16px;
  align-items: center;
  gap: 9px;
  width: 100%;
  padding: 10px 8px;
  border: 1px solid transparent;
  border-radius: 7px;
  background: transparent;
  color: #31425c;
  text-align: left;
  cursor: pointer;
}

.lesson-item:hover {
  background: #f5f8fc;
}

.lesson-item.active {
  border-color: #bed7fb;
  background: #eaf3ff;
}

.lesson-item.done .lesson-index {
  background: #e6f5ee;
  color: #108556;
}

.lesson-index {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 7px;
  background: #eef3f8;
  color: #637188;
  font-size: 12px;
  font-weight: 900;
}

.lesson-item.active .lesson-index {
  background: #2d7be8;
  color: #fff;
}

.lesson-copy {
  min-width: 0;
}

.lesson-copy strong,
.lesson-copy small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lesson-copy strong {
  font-size: 13px;
  line-height: 1.35;
}

.lesson-copy small {
  margin-top: 3px;
  color: #74839a;
  font-size: 11px;
}

.mission-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 16px;
}

.mission-hero p {
  margin: 8px 0 0;
  color: #52647f;
  font-size: 13px;
  line-height: 1.6;
}

.hero-meta {
  display: flex;
  flex-direction: column;
  gap: 7px;
  align-items: flex-end;
  flex: 0 0 auto;
}

.hero-meta span,
.step-badge,
.code-lang,
.live-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 5px 9px;
  background: #eef4fb;
  color: #40536f;
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
}

.hero-meta span:first-child {
  background: #e8f6ef;
  color: #108556;
}

.focus-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  padding: 6px 10px;
  background: #fff;
  color: #1d5fbf;
  border: 1px solid #cfe0f6;
  font-size: 12px;
  font-weight: 900;
  text-decoration: none;
  white-space: nowrap;
}

.focus-back:hover {
  border-color: #2d7be8;
  background: #eaf3ff;
}

.step-ribbon {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(132px, 1fr));
  gap: 8px;
}

.step-ribbon button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-width: 0;
  padding: 10px 8px;
  border: 1px solid #d8e3f0;
  border-radius: 7px;
  background: #fff;
  color: #53647d;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
}

.step-ribbon button.active {
  border-color: #2d7be8;
  background: #2d7be8;
  color: #fff;
}

.step-ribbon button.completed {
  border-color: #bfe9d4;
  background: #e9f8f0;
  color: #108556;
}

.step-ribbon button.locked {
  cursor: pointer;
  opacity: 0.78;
  border-style: dashed;
}

.task-card {
  overflow: auto;
}

.task-card > .markdown-body,
.evidence-grid,
.step-note,
.read-brief {
  padding: 16px;
}

.read-brief {
  display: grid;
  gap: 12px;
}

.brief-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.brief-block {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 10px;
  min-width: 0;
  border: 1px solid #e1e9f4;
  border-radius: 7px;
  padding: 14px;
  background: #f8fbff;
  color: #2672d9;
}

.brief-block.primary {
  display: block;
  border-color: #cfe0f6;
  background: #f5f9ff;
}

.brief-block h4 {
  margin: 0 0 8px;
  color: #17243a;
  font-size: 16px;
  line-height: 1.35;
}

.brief-block p,
.brief-block li {
  color: #4d5f79;
  font-size: 13px;
  line-height: 1.7;
}

.brief-block p,
.brief-block ul {
  margin: 0;
}

.brief-block ul {
  padding-left: 18px;
}

.brief-block li + li {
  margin-top: 5px;
}

.source-details {
  border: 1px solid #e1e9f4;
  border-radius: 7px;
  background: #fff;
  overflow: hidden;
}

.source-details summary {
  cursor: pointer;
  padding: 12px 14px;
  color: #40536f;
  font-size: 13px;
  font-weight: 900;
}

.source-details .markdown-body {
  padding: 0 14px 14px;
  border-top: 1px solid #edf2f7;
}

.source-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  padding: 0 14px 14px;
  border-top: 1px solid #edf2f7;
}

.source-summary.compact {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  padding: 0;
  border-top: none;
}

.source-chip-card {
  display: grid;
  gap: 5px;
  min-width: 0;
  border: 1px solid #e1e9f4;
  border-radius: 7px;
  padding: 10px;
  background: #f8fbff;
}

.source-chip-card b {
  color: #1d5fbf;
  font-size: 12px;
}

.source-chip-card span {
  color: #52647f;
  font-size: 12px;
  line-height: 1.55;
}

.evidence-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.evidence-grid article {
  border: 1px solid #e1e9f4;
  border-radius: 7px;
  padding: 13px;
  background: #f8fbff;
}

.evidence-grid .source-note {
  grid-column: 1 / -1;
}

.evidence-grid h4,
.step-note h4 {
  margin: 0 0 10px;
  color: #1b2a44;
  font-size: 15px;
}

.evidence-grid ul {
  margin: 0;
  padding-left: 18px;
}

.evidence-grid li,
.evidence-grid p,
.step-note p {
  color: #4d5f79;
  font-size: 13px;
  line-height: 1.7;
}

.step-note {
  display: grid;
  grid-template-columns: 30px minmax(0, 1fr);
  gap: 10px;
  color: #2672d9;
}

.tutor-panel {
  display: flex;
  flex-direction: column;
}

.live-pill.online {
  background: #e8f6ef;
  color: #108556;
}

.chat-scroll {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 12px 14px;
  background: #f8fbff;
}

.message {
  max-width: 92%;
  margin-bottom: 10px;
  padding: 11px 12px;
  border: 1px solid #e1e9f4;
  border-radius: 8px;
  background: #fff;
  color: #24344e;
  font-size: 13px;
  line-height: 1.65;
}

.message.user {
  margin-left: auto;
  border-color: #b9d5ff;
  background: #eaf3ff;
}

.citation-list {
  display: grid;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e2e8f0;
}

.citation-list summary {
  cursor: pointer;
  color: #1d5fbf;
  font-size: 12px;
  font-weight: 900;
}

.citation-card {
  display: grid;
  gap: 5px;
  padding: 9px;
  border: 1px solid #dbe5f1;
  border-radius: 7px;
  background: #fff;
}

.citation-card span {
  justify-self: start;
  border-radius: 4px;
  padding: 2px 6px;
  background: #e8f6ef;
  color: #108556;
  font-size: 11px;
  font-weight: 900;
}

.citation-card b {
  color: #26364f;
  font-size: 12px;
}

.citation-card small {
  color: #6f7d91;
  font-size: 11px;
  word-break: break-all;
}

.citation-snippet {
  max-height: 138px;
  overflow: auto;
  color: #465771;
  font-size: 12px;
}

.typing-status,
.quiz-loading {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.prompt-bar {
  display: flex;
  gap: 7px;
  padding: 10px 12px 0;
  overflow-x: auto;
}

.prompt-bar button {
  flex: 0 0 auto;
  border: 1px solid #dbe5f1;
  border-radius: 999px;
  background: #fff;
  color: #40536f;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.prompt-bar button:hover {
  border-color: #2d7be8;
  color: #1d5fbf;
}

.chat-input {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 40px;
  gap: 8px;
  padding: 10px 12px 12px;
}

.chat-input input {
  min-width: 0;
  height: 40px;
  border: 1px solid #d8e3f0;
  border-radius: 999px;
  padding: 0 14px;
  color: #26364f;
  outline: none;
}

.chat-input input:focus {
  border-color: #2d7be8;
  box-shadow: 0 0 0 3px rgba(45, 123, 232, 0.12);
}

.chat-input button,
.btn-primary,
.btn-ghost {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border: none;
  cursor: pointer;
  font-weight: 900;
}

.chat-input button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #2d7be8;
  color: #fff;
}

.chat-input button:disabled,
.btn-primary:disabled,
.btn-ghost:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.code-card {
  display: flex;
  flex-direction: column;
  background: #101827;
  border-color: #1f2c42;
}

.code-card .section-head {
  border-bottom-color: #26374f;
}

.code-card .eyebrow,
.code-card h3 {
  color: #e5edf7;
}

.code-lang {
  background: #20314b;
  color: #b9d5ff;
}

.code-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 14px;
  border-bottom: 1px solid #26374f;
  color: #90a3bd;
  font-size: 12px;
}

.code-meta span:first-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.code-view {
  flex: 1;
  min-height: 0;
  margin: 0;
  padding: 12px 0 14px;
  overflow: auto;
  color: #dbeafe;
  font-family: "Cascadia Code", "Consolas", monospace;
  font-size: 12.5px;
  line-height: 1.62;
  tab-size: 2;
}

.code-view.empty {
  color: #fbd38d;
}

.code-line {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  min-width: max-content;
  padding-right: 12px;
}

.code-line.todo {
  background: rgba(245, 158, 11, 0.12);
}

.line-no {
  padding-right: 12px;
  color: #64748b;
  text-align: right;
  user-select: none;
}

.line-code {
  white-space: pre;
}

.patch-card {
  display: flex;
  flex-direction: column;
  padding-bottom: 12px;
}

.field-block {
  display: block;
  padding: 0 14px 10px;
}

.field-block span {
  display: block;
  margin-bottom: 7px;
  color: #33445f;
  font-size: 12px;
  font-weight: 900;
}

.field-block textarea {
  display: block;
  width: 100%;
  min-height: 92px;
  resize: vertical;
  border: 1px solid #d8e3f0;
  border-radius: 7px;
  padding: 10px 11px;
  color: #26364f;
  font-family: "Cascadia Code", "Microsoft YaHei", sans-serif;
  font-size: 13px;
  line-height: 1.6;
  outline: none;
}

.field-block + .field-block textarea {
  min-height: 72px;
  font-family: inherit;
}

.field-block textarea:focus {
  border-color: #2d7be8;
  box-shadow: 0 0 0 3px rgba(45, 123, 232, 0.1);
}

.check-card {
  display: flex;
  flex-direction: column;
}

.feedback-panel {
  display: flex;
  flex-direction: column;
}

.progress-count {
  color: #2672d9;
}

.quiz-loading {
  padding: 16px;
}

.quiz-list {
  flex: 1;
  min-height: 0;
  display: grid;
  gap: 10px;
  padding: 12px 14px;
  overflow: auto;
}

.quiz-item {
  display: grid;
  gap: 8px;
  padding-bottom: 10px;
  border-bottom: 1px solid #edf2f7;
}

.quiz-item:last-child {
  border-bottom: none;
}

.quiz-item p {
  margin: 0;
  color: #24344e;
  font-size: 13px;
  font-weight: 900;
  line-height: 1.55;
}

.option-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
}

.option-grid button {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr);
  align-items: center;
  gap: 7px;
  min-height: 36px;
  border: 1px solid #d8e3f0;
  border-radius: 7px;
  background: #fff;
  color: #41536d;
  padding: 7px 8px;
  text-align: left;
  cursor: pointer;
}

.option-grid button b {
  display: grid;
  width: 21px;
  height: 21px;
  place-items: center;
  border-radius: 50%;
  background: #edf3f8;
  color: #637188;
  font-size: 11px;
}

.option-grid button span {
  min-width: 0;
  font-size: 12px;
  line-height: 1.35;
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.option-grid button.selected {
  border-color: #2d7be8;
  background: #eaf3ff;
  color: #1d5fbf;
}

.option-grid button.selected b {
  background: #2d7be8;
  color: #fff;
}

.option-grid button.correct {
  border-color: #16a36a;
  background: #e8f6ef;
  color: #0f7a4f;
}

.option-grid button.wrong {
  border-color: #e06464;
  background: #fff1f1;
  color: #b42323;
}

.quiz-explain {
  color: #68788f;
  font-size: 12px;
  line-height: 1.55;
}

.self-check-result {
  display: flex;
  align-items: center;
  gap: 7px;
  margin: 0 14px 10px;
  padding: 9px 10px;
  border-radius: 7px;
  background: #e8f6ef;
  color: #108556;
  font-size: 12px;
  font-weight: 900;
}

.feedback-result {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr);
  gap: 16px;
  margin: 14px;
  padding: 18px;
  border: 1px solid #f2d58f;
  border-radius: 7px;
  background: #fff9e8;
  overflow: auto;
}

.score-box {
  display: grid;
  place-items: center;
  align-content: center;
}

.score-box strong {
  color: #b76b00;
  font-size: 28px;
  line-height: 1;
}

.score-box span {
  color: #9a5a00;
  font-size: 11px;
  font-weight: 900;
}

.feedback-copy {
  min-width: 0;
  color: #3b4b63;
  font-size: 13px;
}

.empty-feedback {
  display: grid;
  place-items: center;
  align-content: center;
  gap: 10px;
  flex: 1;
  padding: 28px;
  color: #52647f;
  text-align: center;
}

.empty-feedback h4 {
  margin: 0;
  color: #1b2a44;
  font-size: 16px;
}

.empty-feedback p {
  max-width: 340px;
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
}

.feedback-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.feedback-tags span {
  border-radius: 999px;
  background: #fff0c2;
  color: #8a5200;
  padding: 4px 7px;
  font-size: 11px;
  font-weight: 800;
}

.rubric-list {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}

.rubric-list article {
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr);
  gap: 10px;
  align-items: start;
  padding: 10px;
  border: 1px solid #f1d4bd;
  border-radius: 7px;
  background: #fff8f1;
}

.rubric-list article.passed {
  border-color: #bfe9d4;
  background: #f0fbf5;
}

.rubric-list b {
  display: grid;
  place-items: center;
  width: 38px;
  height: 30px;
  border-radius: 6px;
  background: #10233f;
  color: #fff;
  font-size: 12px;
}

.rubric-list strong,
.rubric-list span {
  display: block;
}

.rubric-list span {
  margin-top: 4px;
  color: #65758b;
  font-size: 12px;
  line-height: 1.55;
}

.action-row {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 8px;
  padding: 0 14px 14px;
}

.btn-ghost,
.btn-primary {
  min-height: 40px;
  border-radius: 7px;
  padding: 0 12px;
  font-size: 13px;
}

.btn-ghost {
  border: 1px solid #d8e3f0;
  background: #fff;
  color: #40536f;
}

.btn-primary {
  background: #2d7be8;
  color: #fff;
}

.markdown-body {
  color: #34455f;
  font-size: 13px;
  line-height: 1.72;
  word-break: break-word;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin: 12px 0 8px;
  color: #17243a;
  line-height: 1.35;
}

.markdown-body :deep(h1) {
  font-size: 20px;
}

.markdown-body :deep(h2) {
  font-size: 18px;
}

.markdown-body :deep(h3) {
  font-size: 16px;
}

.markdown-body :deep(h4) {
  font-size: 15px;
}

.markdown-body :deep(p) {
  margin: 0 0 10px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0 0 10px;
  padding-left: 19px;
}

.markdown-body :deep(li) {
  margin-bottom: 5px;
}

.markdown-body :deep(code) {
  border-radius: 4px;
  background: #eef4fb;
  color: #be123c;
  padding: 2px 5px;
  font-family: "Cascadia Code", "Consolas", monospace;
  font-size: 0.92em;
}

.markdown-body :deep(.md-code) {
  max-height: 260px;
  margin: 10px 0;
  overflow: auto;
  border-radius: 7px;
  background: #101827;
  color: #dbeafe;
  padding: 12px;
  font-family: "Cascadia Code", "Consolas", monospace;
  font-size: 12.5px;
  line-height: 1.6;
}

.markdown-body :deep(.md-code code) {
  background: transparent;
  color: inherit;
  padding: 0;
}

.loading-screen {
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

@media (max-width: 1280px) {
  .coach-workbench {
    grid-template-columns: minmax(460px, 1fr) minmax(340px, 430px);
  }

  .option-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1040px) {
  .coach-workbench {
    grid-template-columns: minmax(0, 1fr);
    height: auto;
    min-height: calc(100vh - 82px);
    overflow: visible;
  }

  .lab-column {
    grid-column: 1 / -1;
    grid-template-columns: 1fr;
    grid-template-rows: auto minmax(0, 1fr);
  }

  .code-card {
    min-height: 420px;
  }

  .check-card,
  .feedback-panel,
  .patch-card {
    min-height: 420px;
  }
}

@media (max-width: 760px) {
  .coach-workbench {
    grid-template-columns: 1fr;
    padding: 10px;
  }

  .guide-column,
  .lab-column,
  .course-rail {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }

  .step-ribbon {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .mission-hero,
  .section-head {
    flex-direction: column;
  }

  .hero-meta {
    align-items: flex-start;
  }

  .evidence-grid,
  .brief-grid,
  .source-summary,
  .lab-column {
    grid-template-columns: 1fr;
  }
}
</style>
