<template>
  <main class="coach-workbench">
    <div v-if="loading" class="loading-screen">
      <LoaderCircle :size="24" class="spin" />
      <span>正在加载课程工作台...</span>
    </div>

    <aside class="course-rail">
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
          <h2>{{ store.lesson?.title || '请选择章节' }}</h2>
          <p>{{ store.lesson?.summary || '读取真实课程资料后开始本节任务。' }}</p>
        </div>
        <div class="hero-meta">
          <span>{{ sourceLabel }}</span>
          <span>{{ ragStatus }}</span>
        </div>
      </section>

      <nav class="step-ribbon" aria-label="学习步骤">
        <button
          v-for="step in stepCards"
          :key="step.key"
          type="button"
          :class="{ active: activeStepKey === step.key }"
          @click="activeStepKey = step.key"
        >
          <component :is="step.icon" :size="15" />
          <span>{{ step.label }}</span>
        </button>
      </nav>

      <section class="work-panel task-card">
        <div class="section-head">
          <div>
            <p class="eyebrow">{{ activeStep.label }}</p>
            <h3>{{ activeStep.title }}</h3>
          </div>
          <span class="step-badge">{{ activeStep.badge }}</span>
        </div>

        <div v-if="activeStepKey === 'read'" class="markdown-body" v-html="renderMarkdown(taskMarkdown)"></div>

        <div v-else-if="activeStepKey === 'evidence'" class="evidence-grid">
          <article>
            <h4>学习目标</h4>
            <ul>
              <li v-for="item in store.lesson?.objectives || []" :key="item">{{ item }}</li>
            </ul>
          </article>
          <article>
            <h4>验收依据</h4>
            <ul>
              <li v-for="item in store.lesson?.practice.checklist || []" :key="item">{{ item }}</li>
            </ul>
          </article>
          <article class="source-note">
            <h4>资料来源</h4>
            <p>{{ store.lesson?.source || '当前章节资料来自课程文档或真实项目代码。' }}</p>
          </article>
        </div>

        <div v-else-if="activeStepKey === 'patch'" class="step-note">
          <Code2 :size="20" />
          <div>
            <h4>只补当前步骤需要的片段</h4>
            <p>
              右侧代码块是只读参考。学生只需要在“补全区”提交本节涉及的关键方法、配置、SQL 或说明，
              不提交完整项目目录，也不让 AI 一次性生成完整工程。
            </p>
          </div>
        </div>

        <div v-else-if="activeStepKey === 'test'" class="step-note">
          <ClipboardCheck :size="20" />
          <div>
            <h4>先自检，再交给 AI 检查</h4>
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
              说明你改了哪里、为什么这么改、对应哪条课程或项目资料。AI 反馈必须基于 RAG 引用，失败就显示真实错误。
            </p>
          </div>
        </div>
      </section>

      <section class="work-panel tutor-panel">
        <div class="section-head compact">
          <div>
            <p class="eyebrow">AI Coach</p>
            <h3><Sparkles :size="17" /> 引用式助教</h3>
          </div>
          <span class="live-pill" :class="{ online: store.health?.deepseek_live }">
            {{ store.health?.deepseek_live ? 'DeepSeek 在线' : '模型未连接' }}
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

            <div v-if="message.citations?.length" class="citation-list">
              <strong>引用资料</strong>
              <article
                v-for="citation in message.citations"
                :key="`${citation.kind}-${citation.source}-${citation.title}`"
                class="citation-card"
              >
                <span>{{ citationKindLabel(citation.kind) }}</span>
                <b>{{ citation.title }}</b>
                <small>{{ citation.source }}</small>
                <div class="citation-snippet markdown-body" v-html="renderMarkdown(citation.snippet)"></div>
              </article>
            </div>

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
      <section class="work-panel code-card">
        <div class="section-head compact">
          <div>
            <p class="eyebrow">Read Only Code</p>
            <h3><Terminal :size="17" /> 参考片段</h3>
          </div>
          <span class="code-lang">{{ codeLanguage }}</span>
        </div>

        <div class="code-meta">
          <span>{{ store.lesson?.source || '真实课程资料' }}</span>
          <span>{{ codeLines.length }} 行</span>
        </div>

        <pre class="code-view" :class="{ empty: isTemplateEmpty }"><code><span
          v-for="line in codeLines"
          :key="line.number"
          class="code-line"
          :class="{ todo: line.isTodo }"
        ><span class="line-no">{{ line.number }}</span><span class="line-code">{{ line.text || ' ' }}</span></span></code></pre>
      </section>

      <section class="work-panel patch-card">
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

      <section class="work-panel check-card">
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

        <div v-if="feedback" class="feedback-result">
          <div class="score-box">
            <strong>{{ feedback.score }}</strong>
            <span>AI 评分</span>
          </div>
          <div class="feedback-copy">
            <div class="markdown-body" v-html="renderMarkdown(feedback.ai_comment)"></div>
            <div v-if="feedback.improvements?.length" class="feedback-tags">
              <span v-for="item in feedback.improvements" :key="item">{{ item }}</span>
            </div>
          </div>
        </div>

        <div class="action-row">
          <button type="button" class="btn-ghost" :disabled="!answeredCount" @click="selfChecked = true">
            完成自检
          </button>
          <button type="button" class="btn-primary" :disabled="submitting" @click="submitPractice">
            <LoaderCircle v-if="submitting" :size="17" class="spin" />
            <span>{{ submitting ? '正在检查...' : '提交 AI 检查' }}</span>
          </button>
        </div>
      </section>
    </aside>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch, type Component } from 'vue'
import {
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
import { ElMessage } from 'element-plus'
import { api, type Citation, type Question, type QuestionOption } from '../api'
import { useCourseStore } from '../stores/course'
import { renderMarkdown } from '../utils/markdown'

type StepKey = 'read' | 'evidence' | 'patch' | 'test' | 'reflect'
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
}

const store = useCourseStore()
const loading = ref(true)
const activeStepKey = ref<StepKey>('read')
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

const sourceLabel = computed(() =>
  store.activeCourseId === 'nongbo-admin-project' ? '农博真实项目' : 'SpringBoot 课程资料',
)

const ragStatus = computed(() => {
  const backend = store.health?.rag_backend || 'RAG'
  const chunks = store.health?.rag_chunks
  return chunks ? `${backend} / ${chunks} chunks` : backend
})

const taskMarkdown = computed(() =>
  [
    store.lesson?.content || store.lesson?.summary || '',
    '',
    '#### 本节练习',
    store.lesson?.practice.description || '',
  ].join('\n'),
)

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

onMounted(async () => {
  try {
    await store.load()
    resetWorkspaceState()
    await loadQuiz()
  } finally {
    loading.value = false
  }
})

watch(
  () => [store.activeCourseId, store.activeLessonId],
  async () => {
    resetWorkspaceState()
    activeStepKey.value = 'read'
    await loadQuiz()
  },
)

async function switchCourse(courseId: string) {
  await store.setCourse(courseId)
}

function resetWorkspaceState() {
  code.value = store.lesson?.practice.template || ''
  studentCode.value = ''
  reflection.value = ''
  selectedOptions.value = {}
  selfChecked.value = false
  feedback.value = null
  question.value = ''
  messages.value = [
    {
      id: Date.now(),
      role: 'assistant',
      content: `我会围绕《${store.lesson?.title || '当前章节'}》做引用式辅导。\n\n你可以先读任务，再在右侧补全关键片段。需要帮助时我只给提示、解释或检查，不会替你生成完整项目。`,
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
        mode,
      },
      {
        onStatus(data) {
          updateAssistant(assistantId, { status: data.message || '正在处理...' })
          scrollChatToBottom()
        },
        onCitations(citations) {
          updateAssistant(assistantId, { citations })
          scrollChatToBottom()
        },
        onDelta(delta) {
          const msg = messages.value.find((item) => item.id === assistantId)
          if (msg) msg.content += delta
          scrollChatToBottom()
        },
        onDone() {
          updateAssistant(assistantId, { streaming: false, status: '' })
          scrollChatToBottom()
        },
        onError(data) {
          streamFailed = true
          updateAssistant(assistantId, {
            streaming: false,
            status: '',
            content: `**AI 调用失败**\n\n${data.message || '模型或知识库返回错误。'}`,
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
      content: `**AI 调用失败**\n\n${errorMessage(error)}`,
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

function updateAssistant(id: number, patch: Partial<ChatMessage>) {
  const message = messages.value.find((item) => item.id === id)
  if (message) Object.assign(message, patch)
}

async function scrollChatToBottom() {
  await nextTick()
  if (chatScrollRef.value) {
    chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight
  }
}

async function submitPractice() {
  if (submitting.value) return
  if (!studentCode.value.trim() && !reflection.value.trim()) {
    ElMessage.warning('请先填写补全片段或实现说明，再提交检查。')
    return
  }

  submitting.value = true
  try {
    const answers = quizBank.value.map((quiz) => {
      const key = selectedOptions.value[quiz.id] || '未选择'
      const option = quiz.options.find((item) => item.key === key)
      return `${quiz.question} => ${key}${option ? `. ${option.text}` : ''}`
    }).join('\n')

    feedback.value = await api.submitPractice({
      course_id: store.activeCourseId,
      lesson_id: store.activeLessonId,
      code: studentCode.value,
      notes: [
        `章节：${store.lesson?.title || store.activeLessonId}`,
        `自检：\n${answers}`,
        `说明：${reflection.value || '未填写'}`,
      ].join('\n\n'),
    })
  } catch (error) {
    ElMessage.error(errorMessage(error))
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

function errorMessage(error: unknown) {
  if (typeof error === 'object' && error && 'response' in error) {
    const data = (error as any).response?.data
    return data?.detail || data?.message || (error as any).message || '请求失败。'
  }
  const raw = error instanceof Error ? error.message : '请求失败。'
  try {
    const parsed = JSON.parse(raw)
    return parsed.detail || parsed.message || raw
  } catch {
    return raw
  }
}
</script>

<style scoped>
.coach-workbench {
  display: grid;
  grid-template-columns: 248px minmax(420px, 1fr) minmax(420px, 520px);
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

.course-rail,
.guide-column,
.lab-column {
  display: grid;
  gap: 12px;
}

.course-rail {
  grid-template-rows: auto minmax(0, 1fr);
}

.guide-column {
  grid-template-rows: auto auto minmax(190px, 0.95fr) minmax(260px, 1.05fr);
}

.lab-column {
  grid-template-rows: minmax(240px, 0.85fr) auto minmax(260px, 1fr);
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

.step-ribbon {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
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

.task-card {
  overflow: auto;
}

.task-card > .markdown-body,
.evidence-grid,
.step-note {
  padding: 16px;
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

.citation-list > strong {
  color: #1d5fbf;
  font-size: 12px;
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
  grid-template-columns: 58px minmax(0, 1fr);
  gap: 10px;
  margin: 0 14px 10px;
  padding: 10px;
  border: 1px solid #f2d58f;
  border-radius: 7px;
  background: #fff9e8;
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
  font-size: 12px;
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
    grid-template-columns: 230px minmax(360px, 1fr) minmax(360px, 460px);
  }

  .option-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1040px) {
  .coach-workbench {
    grid-template-columns: 230px minmax(0, 1fr);
    height: auto;
    min-height: calc(100vh - 82px);
    overflow: visible;
  }

  .lab-column {
    grid-column: 1 / -1;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-template-rows: auto auto;
  }

  .code-card {
    min-height: 420px;
  }

  .check-card {
    grid-column: 1 / -1;
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
  .lab-column {
    grid-template-columns: 1fr;
  }
}
</style>
