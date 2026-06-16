<template>
  <div class="workspace-page">
    <div v-if="loading" class="loading-state" role="status">
      <Loader2 class="spin-icon" :size="22" />
      <span>正在加载任务...</span>
    </div>

    <div v-else-if="loadError" class="empty-state" role="alert">
      <AlertTriangle :size="24" />
      <strong>任务加载失败</strong>
      <p>{{ loadError }}</p>
    </div>

    <template v-else-if="task">
      <header class="task-header">
        <div class="task-copy">
          <div class="task-meta">
            <span>{{ taskTypeLabel(task.type) }}</span>
            <span>{{ artifactTypeLabel(task.required_artifact_type) }}</span>
          </div>
          <h1>{{ task.title }}</h1>
          <p>{{ task.goal }}</p>
        </div>

        <div class="header-actions" aria-label="任务操作">
          <button
            type="button"
            class="icon-action secondary"
            :disabled="hintLoading || guidedLoading"
            aria-label="获取提示"
            title="获取提示"
            @click="getHint"
          >
            <Loader2 v-if="hintLoading" class="spin-icon" :size="17" />
            <Lightbulb v-else :size="17" />
            <span>提示</span>
          </button>
          <button
            type="button"
            class="icon-action primary"
            :disabled="checkLoading || !canSubmitCheck"
            aria-label="提交验收"
            title="提交验收"
            @click="submitCheck"
          >
            <Loader2 v-if="checkLoading" class="spin-icon" :size="17" />
            <CheckCircle2 v-else :size="17" />
            <span>提交验收</span>
          </button>
        </div>
      </header>

      <main class="workspace-grid">
        <section class="dialogue-panel" aria-labelledby="guided-title">
          <div v-if="activeQuestion" class="question-strip">
            <div class="question-strip-head">
              <span class="status-pill">已发布题目</span>
              <span class="question-type">{{ qTypeLabel(activeQuestion.type) }}</span>
              <button
                type="button"
                class="close-button"
                aria-label="关闭当前题目"
                title="关闭当前题目"
                @click="clearActiveQuestion"
              >
                <X :size="16" />
              </button>
            </div>
            <p class="question-stem">{{ activeQuestion.stem }}</p>
            <div v-if="activeQuestion.options?.length" class="option-list">
              <span v-for="opt in activeQuestion.options" :key="opt.key">
                {{ opt.key }}. {{ opt.text }}
              </span>
            </div>
          </div>

          <div class="panel-heading">
            <div>
              <span class="panel-kicker">
                <Bot :size="15" />
                智能体引导
              </span>
              <h2 id="guided-title">分步对话</h2>
            </div>
            <span v-if="guidedStatus" class="session-status">{{ guidedStatusLabel }}</span>
          </div>

          <div v-if="showStartGuidedAction" class="understood-actions start-guided-actions">
            <button
              type="button"
              class="understood-button"
              :disabled="guidedLoading"
              @click="startQuestionGuidance"
            >
              <Bot :size="16" />
              <span>开始 AI 分步讲解</span>
            </button>
          </div>

          <div v-if="guidedSteps.length" class="guided-stepper" aria-label="引导步骤进度">
            <div class="stepper-top">
              <strong>{{ currentStepTitle }}</strong>
              <span>{{ guidedCurrentStep + 1 }} / {{ guidedTotalSteps || guidedSteps.length }}</span>
            </div>
            <div class="stepper-track" aria-hidden="true">
              <span
                v-for="(_, index) in guidedSteps"
                :key="index"
                :class="['step-dot', { active: index === guidedCurrentStep, done: index < guidedCurrentStep }]"
              >
                {{ index + 1 }}
              </span>
            </div>
            <p v-if="currentStepGoal">{{ currentStepGoal }}</p>
            <p class="stepper-tip">可以点击“已理解，下一步”，也可以在对话框输入“下一步”或“继续”。</p>
          </div>

          <div v-if="guidedCitations.length" class="citation-strip" aria-label="参考资料">
            <div v-for="item in guidedCitations" :key="`${item.kind}-${item.source}-${item.snippet}`" class="citation-item">
              <span class="source-kind">{{ citationKindLabel(item.kind) }}</span>
              <a
                v-if="isUrl(item.source)"
                :href="item.source"
                target="_blank"
                rel="noreferrer"
              >
                {{ item.title || shortSource(item.source) }}
              </a>
              <span v-else>{{ item.title || shortSource(item.source) }}</span>
            </div>
          </div>

          <div ref="chatContainer" class="chat-messages" aria-live="polite">
            <div v-if="!messages.length" class="empty-chat">
              <Bot :size="22" />
              <span>等待题目或提问</span>
            </div>

            <article
              v-for="(msg, index) in messages"
              :key="index"
              :class="['message-row', msg.role]"
            >
              <div v-if="msg.role !== 'system'" class="message-avatar" aria-hidden="true">
                {{ msg.role === 'assistant' ? 'AI' : '我' }}
              </div>
              <div :class="['message-bubble', { 'system-bubble': msg.role === 'system' }]">
                <div class="message-content" v-html="renderMarkdown(msg.content)"></div>
              </div>
            </article>

            <div v-if="showGuidedThinking" class="message-row assistant">
              <div class="message-avatar" aria-hidden="true">AI</div>
              <div class="message-bubble pending">
                <Loader2 class="spin-icon" :size="16" />
                <span>{{ guidedThinkingText }}</span>
              </div>
            </div>

          </div>

          <div v-if="showUnderstoodAction" class="understood-actions">
            <button
              type="button"
              class="understood-button"
              :disabled="guidedLoading"
              @click="markUnderstood"
            >
              <CheckCircle2 :size="16" />
              <span>已理解，下一步</span>
            </button>
          </div>

          <form class="chat-input" @submit.prevent="sendMessage">
            <label class="sr-only" for="student-question">向智能体提问</label>
            <textarea
              id="student-question"
              v-model="userInput"
              rows="2"
              placeholder="输入你的问题、当前思路，或输入“下一步/继续”推进"
              aria-label="向智能体提问"
              @keydown.enter.ctrl.prevent="sendMessage"
            ></textarea>
            <button
              type="submit"
              class="send-button"
              :disabled="!userInput.trim() || guidedLoading"
              aria-label="发送消息"
              title="发送"
            >
              <Send :size="17" />
            </button>
          </form>
        </section>

        <section class="answer-panel" aria-labelledby="answer-title">
          <div class="panel-heading">
            <div>
              <span class="panel-kicker">
                <Code2 :size="15" />
                练习区
              </span>
              <h2 id="answer-title">代码 / 答案</h2>
            </div>
            <span class="artifact-pill">{{ artifactTypeLabel(task.required_artifact_type) }}</span>
          </div>

          <div v-if="activeQuestion" class="answer-context">
            <FileText :size="16" />
            <span>{{ qTypeLabel(activeQuestion.type) }}</span>
          </div>

          <div v-if="activeQuestion && questionOptions(activeQuestion).length" class="question-answer-options">
            <label
              v-for="opt in questionOptions(activeQuestion)"
              :key="opt.key"
              :class="['answer-option', { selected: selectedOptionKeys.includes(opt.key) }]"
            >
              <input
                :type="activeQuestion.type === 'multi_choice' ? 'checkbox' : 'radio'"
                :name="activeQuestion.id"
                :value="opt.key"
                :checked="selectedOptionKeys.includes(opt.key)"
                @change="toggleOptionAnswer(opt.key)"
              />
              <strong>{{ opt.key }}</strong>
              <span>{{ opt.text }}</span>
            </label>
          </div>
          <div v-if="activeQuestion && isObjectiveQuestion(activeQuestion)" class="selected-answer-summary">
            <strong>已选答案</strong>
            <span>{{ selectedAnswerKeys.length ? selectedAnswerKeys.join('、') : '请先选择答案' }}</span>
          </div>

          <div v-if="activeQuestion?.type === 'code_fill'" class="code-fill-preview">
            <div class="code-fill-preview-title">
              <FileText :size="15" />
              <strong>填空预览</strong>
            </div>
            <pre>{{ codeFillPreview(activeQuestion) }}</pre>
          </div>

          <div v-if="!activeQuestion || !isObjectiveQuestion(activeQuestion)" class="editor-shell">
            <div class="editor-gutter" aria-hidden="true">
              <span v-for="n in editorLineCount" :key="n">{{ n }}</span>
            </div>
            <label class="sr-only" for="answer-editor">代码或答案输入区</label>
            <textarea
              id="answer-editor"
              v-model="codeInput"
              class="code-editor"
              spellcheck="false"
              aria-label="代码或答案输入区"
              placeholder="// 在这里写你的代码、SQL 或文字答案"
            ></textarea>
          </div>

          <div class="editor-footer">
            <span>{{ codeInput.length }} 字符</span>
            <span>AI 验收会结合右侧内容与课程资料</span>
          </div>
        </section>
      </main>

      <section v-if="checkResult" class="result-section" aria-labelledby="result-title">
        <div class="result-header">
          <h2 id="result-title">验收结果</h2>
          <span :class="['result-badge', checkResult.level]">
            {{ checkResult.passed ? '通过' : '需修改' }}
          </span>
        </div>

        <div class="score-row">
          <div class="score-ring">
            <strong>{{ checkResult.score }}</strong>
            <span>/100</span>
          </div>
          <p>{{ checkResult.reply }}</p>
        </div>

        <div class="result-grid">
          <div v-if="checkResult.strengths.length" class="result-block">
            <h3>亮点</h3>
            <ul>
              <li v-for="(item, index) in checkResult.strengths" :key="index">{{ item }}</li>
            </ul>
          </div>
          <div v-if="checkResult.problems.length" class="result-block">
            <h3>问题</h3>
            <ul>
              <li v-for="(item, index) in checkResult.problems" :key="index">
                <strong>{{ item.type }}</strong>
                <span>{{ item.message }}</span>
                <em v-if="item.suggestion">{{ item.suggestion }}</em>
              </li>
            </ul>
          </div>
          <div v-if="checkResult.nextActions.length" class="result-block">
            <h3>下一步</h3>
            <ul>
              <li v-for="(item, index) in checkResult.nextActions" :key="index">{{ item }}</li>
            </ul>
          </div>
        </div>

        <div v-if="activeQuestion && (previousQuestion || checkResult?.passed)" class="question-nav-actions">
          <button
            v-if="previousQuestion"
            type="button"
            class="icon-action secondary"
            @click="goPreviousQuestion"
          >
            <ArrowLeft :size="16" />
            <span>上一题</span>
          </button>
          <button v-if="checkResult?.passed" type="button" class="icon-action primary" @click="goNextQuestionOrRoadmap">
            <ArrowRight :size="16" />
            <span>{{ nextStepLabel }}</span>
          </button>
        </div>
      </section>
    </template>

    <div v-else class="empty-state">
      <AlertTriangle :size="24" />
      <strong>未找到任务</strong>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Bot,
  CheckCircle2,
  Code2,
  FileText,
  Lightbulb,
  Loader2,
  Send,
  X,
} from 'lucide-vue-next'
import { api, type AICheckResult, type Citation, type LearningTaskDetail, type Question, type TaskSubmissionSnapshot } from '../api'
import { useSessionStore } from '../stores/session'

type ChatRole = 'assistant' | 'student' | 'system'

interface ChatMessage {
  role: ChatRole
  content: string
}

interface GuidedStep {
  title: string
  goal: string
  knowledge_points: string[]
}

interface GuidedResponse {
  sessionId: string
  intent?: string
  steps?: GuidedStep[]
  currentStep: number
  totalSteps: number
  currentStepTitle?: string
  message: string
  citations?: Citation[]
  status: string
}

const route = useRoute()
const router = useRouter()
const session = useSessionStore()

const loading = ref(true)
const loadError = ref('')
const task = ref<LearningTaskDetail | null>(null)
const codeInput = ref('')
const selectedAnswerKeys = ref<string[]>([])
const userInput = ref('')
const messages = ref<ChatMessage[]>([])
const chatContainer = ref<HTMLElement | null>(null)

const checkLoading = ref(false)
const hintLoading = ref(false)
const guidedLoading = ref(false)
const checkResult = ref<AICheckResult | null>(null)

const activeQuestion = ref<Question | null>(null)
const taskQuestions = ref<Question[]>([])
const guidedSessionId = ref('')
const guidedIntent = ref('')
const guidedStatus = ref('')
const guidedSteps = ref<GuidedStep[]>([])
const guidedCurrentStep = ref(0)
const guidedTotalSteps = ref(0)
const guidedCitations = ref<Citation[]>([])
const streamingAssistantVisible = ref(false)
const guidedThinkingText = ref('AI 正在准备引导...')

const studentId = computed(() => session.currentUser?.id || '')

const currentStep = computed(() => guidedSteps.value[guidedCurrentStep.value])
const currentStepTitle = computed(() => currentStep.value?.title || '当前步骤')
const currentStepGoal = computed(() => currentStep.value?.goal || '')
const guidedStatusLabel = computed(() => {
  if (guidedStatus.value === 'completed') return '已完成'
  if (guidedStatus.value === 'active') return '进行中'
  if (guidedStatus.value === 'waiting') return '等待学生回应'
  if (guidedStatus.value === 'teaching') return '引导中'
  if (guidedStatus.value === 'planning') return '规划中'
  return guidedStatus.value || '引导中'
})

const showUnderstoodAction = computed(() =>
  Boolean(
    task.value &&
      messages.value.length &&
      !guidedLoading.value &&
      activeQuestion.value &&
      (guidedSessionId.value || activeQuestion.value.type === 'short_answer') &&
      (!guidedSessionId.value || guidedStatus.value !== 'completed'),
  ),
)
const showStartGuidedAction = computed(() =>
  Boolean(activeQuestion.value && activeQuestion.value.type !== 'short_answer' && !guidedSessionId.value && !guidedLoading.value),
)
const showGuidedThinking = computed(() => guidedLoading.value && !streamingAssistantVisible.value)
const selectedOptionKeys = computed(() => {
  if (!activeQuestion.value || !isObjectiveQuestion(activeQuestion.value)) return []
  return [...selectedAnswerKeys.value]
})
const submissionInput = computed(() => {
  if (activeQuestion.value && isObjectiveQuestion(activeQuestion.value)) {
    return selectedAnswerKeys.value.join('')
  }
  return codeInput.value
})
const canSubmitCheck = computed(() => Boolean(submissionInput.value.trim()))
const editorLineCount = computed(() => Math.max(24, codeInput.value.split('\n').length))
const nextQuestion = computed(() => {
  if (!activeQuestion.value) return null
  const index = taskQuestions.value.findIndex((item) => item.id === activeQuestion.value?.id)
  return index >= 0 ? taskQuestions.value[index + 1] || null : null
})
const previousQuestion = computed(() => {
  if (!activeQuestion.value) return null
  const index = taskQuestions.value.findIndex((item) => item.id === activeQuestion.value?.id)
  return index > 0 ? taskQuestions.value[index - 1] || null : null
})
const nextStepLabel = computed(() => {
  if (nextQuestion.value) return '进入下一题'
  return '进入下一关'
})

onMounted(async () => {
  const taskId = route.params.taskId as string | undefined
  try {
    if (!taskId) {
      loadError.value = '缺少任务 ID'
      return
    }

    task.value = await api.learningTask(taskId)
    await loadRecordSnapshot()
    const questionId = firstQueryValue(route.query.questionId)
    if (questionId) {
      await loadActiveQuestion(taskId, questionId)
      showQuestionIntro()
      await loadLatestSubmission(taskId, questionId)
    } else {
      await loadLatestSubmission(taskId)
    }
  } catch (error: any) {
    loadError.value = errorMessage(error)
  } finally {
    loading.value = false
  }

})

async function loadRecordSnapshot() {
  const recordId = firstQueryValue(route.query.recordId)
  if (!recordId || !studentId.value) return
  const res = await api.studentRecords(studentId.value)
  const record = res.records.find((item) => String(item.id) === recordId)
  if (!record) return
  codeInput.value = record.code || record.notes || ''
  messages.value = [
    { role: 'student', content: `历史提交：\n\n${codeInput.value || '无提交内容'}` },
    { role: 'assistant', content: record.feedback || '本次记录没有保存 AI 反馈。' },
  ]
  if (typeof record.score === 'number') {
    checkResult.value = {
      passed: record.score >= 60,
      score: record.score,
      level: record.score >= 60 ? 'passed' : 'needs_revision',
      reply: record.feedback || '历史验收记录',
      strengths: [],
      problems: [],
      nextActions: [],
      evidence: [],
      rubricScores: [],
      nextTaskUnlocked: false,
    }
  }
}

async function loadLatestSubmission(taskId: string, questionId?: string) {
  if (!studentId.value || route.query.recordId) return
  const res = await api.latestTaskSubmission(taskId, studentId.value, questionId)
  if (!res.submission) return
  applySubmissionSnapshot(res.submission)
}

function applySubmissionSnapshot(submission: TaskSubmissionSnapshot) {
  checkResult.value = submission.result
  if (activeQuestion.value && isObjectiveQuestion(activeQuestion.value)) {
    selectedAnswerKeys.value = normalizeAnswer(submission.studentInput, activeQuestion.value.type).split('').filter(Boolean)
  } else {
    codeInput.value = submission.studentInput
  }
  messages.value.push({
    role: 'system',
    content: `已恢复最近一次提交：${submission.result.passed ? '已通过' : '未通过'}，${submission.result.score} 分。`,
  })
  messages.value.push({
    role: 'assistant',
    content: `## 最近一次验收评析\n${submission.result.reply}`,
  })
}

function firstQueryValue(value: unknown): string | undefined {
  if (Array.isArray(value)) return typeof value[0] === 'string' ? value[0] : undefined
  return typeof value === 'string' ? value : undefined
}

function renderMarkdown(text: string): string {
  const blocks: string[] = []
  let html = escapeHtml(text).replace(/```(\w*)\n([\s\S]*?)```/g, (_match, lang, code) => {
    const language = lang ? ` class="lang-${lang}"` : ''
    const index = blocks.length
    blocks.push(`<pre><code${language}>${code}</code></pre>`)
    return `@@CODE_BLOCK_${index}@@`
  })

  html = html
    .replace(/^###\s+(.+)$/gm, '<h4>$1</h4>')
    .replace(/^##\s+(.+)$/gm, '<h3>$1</h3>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')

  blocks.forEach((block, index) => {
    html = html.replace(`@@CODE_BLOCK_${index}@@`, block)
  })
  return html
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

async function sendMessage() {
  if (!userInput.value.trim() || !task.value || guidedLoading.value) return

  const question = userInput.value.trim()
  messages.value.push({ role: 'student', content: question })
  userInput.value = ''
  await scrollToBottom()

  if (guidedSessionId.value || activeQuestion.value) {
    if (guidedSessionId.value) {
      await sendGuidedMessage(question)
    } else {
      await startGuidedSession(question)
    }
    return
  }

  try {
    const res = await api.aiTaskChat({
      courseLineId: task.value.course_line_id,
      moduleId: task.value.module_id,
      taskId: task.value.id,
      studentId: studentId.value,
      question,
    })
    messages.value.push({ role: 'assistant', content: res.answer })
  } catch (error: any) {
    messages.value.push({ role: 'assistant', content: `**请求失败**\n\n${errorMessage(error)}` })
  }
  await scrollToBottom()
}

async function markUnderstood() {
  if (!task.value || guidedLoading.value) return
  if (!guidedSessionId.value && activeQuestion.value) {
    await startQuestionGuidance()
    return
  }
  if (!guidedSessionId.value) return

  const message = '已理解'
  messages.value.push({ role: 'student', content: message })
  await scrollToBottom()

  await sendGuidedMessage(message)
}

async function getHint() {
  if (!task.value || hintLoading.value || guidedLoading.value) return

  messages.value.push({ role: 'system', content: '学生发起了提示' })
  await scrollToBottom()
  hintLoading.value = true
  try {
    const prompt = activeQuestion.value
      ? `请只围绕当前发布题目给一点提示，不要改写成别的任务，也不要直接给完整答案。\n题干：${activeQuestion.value.stem}`
      : '请只给我当前步骤的一点提示，不要直接给完整答案。'
    const res = await api.aiTaskChat({
      courseLineId: task.value.course_line_id,
      moduleId: task.value.module_id,
      taskId: task.value.id,
      studentId: studentId.value,
      question: prompt,
    })
    messages.value.push({ role: 'assistant', content: res.answer })
    await scrollToBottom()
  } catch (error: any) {
    messages.value.push({ role: 'assistant', content: `**提示生成失败**\n\n${errorMessage(error)}` })
    await scrollToBottom()
  } finally {
    hintLoading.value = false
  }
}

function showQuestionIntro() {
  if (!activeQuestion.value) return
  messages.value = [
    {
      role: 'assistant',
      content: buildQuestionIntro(activeQuestion.value),
    },
  ]
}

async function startQuestionGuidance() {
  if (!activeQuestion.value || guidedSessionId.value || guidedLoading.value) return
  await startGuidedSession('请从读题与定位资料开始，带我分步完成这道题。')
}

function buildQuestionIntro(question: Question): string {
  const optionText = question.options?.length
    ? `\n\n选项：\n${question.options.map((item) => `- ${item.key}. ${item.text}`).join('\n')}`
    : ''
  const action = ['single_choice', 'multi_choice', 'true_false'].includes(question.type)
    ? '请先阅读题干，在右侧“我的答案：”后填写选项字母。需要解释时点“提示”，我会只围绕这道题分步讲解。'
    : '请先阅读题干，在右侧写出你的答案或代码片段。需要提示时点“提示”，我会只围绕这道题分步讲解。'

  return `## 当前题目\n${question.stem}${optionText}\n\n## 你现在要完成的小任务\n${action}`
}

async function startGuidedSession(studentInput: string) {
  if (!task.value) return

  guidedLoading.value = true
  streamingAssistantVisible.value = false
  guidedThinkingText.value = 'AI 正在准备引导...'
  let assistantIndex = -1
  const ensureAssistantMessage = () => {
    if (assistantIndex < 0) {
      messages.value.push({ role: 'assistant', content: '' })
      assistantIndex = messages.value.length - 1
    }
    streamingAssistantVisible.value = true
  }
  try {
    await api.streamGuidedStart(
      {
        courseLineId: task.value.course_line_id,
        moduleId: task.value.module_id,
        taskId: task.value.id,
        studentId: studentId.value,
        studentInput,
        questionId: activeQuestion.value?.id,
        codeDraft: codeInput.value,
      },
      {
        onStatus: (data) => {
          guidedThinkingText.value = data?.message || 'AI 正在准备引导...'
        },
        onMetadata: applyGuidedMetadata,
        onDelta: async (text) => {
          ensureAssistantMessage()
          messages.value[assistantIndex].content += text
          await scrollToBottom()
        },
        onDone: (res) => finalizeGuidedResponse(res, assistantIndex),
        onError: (data) => {
          ensureAssistantMessage()
          messages.value[assistantIndex].content = `**智能体启动失败**\n\n${data.message || '未知错误'}`
        },
      },
    )
  } catch (error: any) {
    messages.value.push({ role: 'assistant', content: `**智能体启动失败**\n\n${errorMessage(error)}` })
  } finally {
    guidedLoading.value = false
    streamingAssistantVisible.value = false
  }
  await scrollToBottom()
}

async function sendGuidedMessage(message: string) {
  if (!guidedSessionId.value) {
    await startGuidedSession(message)
    return
  }

  guidedLoading.value = true
  streamingAssistantVisible.value = false
  guidedThinkingText.value = 'AI 正在准备回应...'
  let assistantIndex = -1
  const ensureAssistantMessage = () => {
    if (assistantIndex < 0) {
      messages.value.push({ role: 'assistant', content: '' })
      assistantIndex = messages.value.length - 1
    }
    streamingAssistantVisible.value = true
  }
  try {
    await api.streamGuidedMessage(
      {
        sessionId: guidedSessionId.value,
        studentId: studentId.value,
        message,
        codeDraft: codeInput.value,
      },
      {
        onStatus: (data) => {
          guidedThinkingText.value = data?.message || 'AI 正在准备回应...'
        },
        onMetadata: applyGuidedMetadata,
        onDelta: async (text) => {
          ensureAssistantMessage()
          messages.value[assistantIndex].content += text
          await scrollToBottom()
        },
        onDone: (res) => finalizeGuidedResponse(res, assistantIndex),
        onError: (data) => {
          ensureAssistantMessage()
          messages.value[assistantIndex].content = `**智能体回复失败**\n\n${data.message || '未知错误'}`
        },
      },
    )
  } catch (error: any) {
    messages.value.push({ role: 'assistant', content: `**智能体回复失败**\n\n${errorMessage(error)}` })
  } finally {
    guidedLoading.value = false
    streamingAssistantVisible.value = false
  }
  await scrollToBottom()
}

function applyGuidedResponse(res: GuidedResponse) {
  applyGuidedMetadata(res)
  messages.value.push({ role: 'assistant', content: res.message })
}

function applyGuidedMetadata(res: Partial<GuidedResponse>) {
  if (res.sessionId) guidedSessionId.value = res.sessionId
  guidedIntent.value = res.intent || guidedIntent.value
  guidedStatus.value = res.status || guidedStatus.value
  guidedSteps.value = res.steps || guidedSteps.value
  guidedCurrentStep.value = Math.max(0, res.currentStep ?? guidedCurrentStep.value)
  guidedTotalSteps.value = res.totalSteps || guidedSteps.value.length
  guidedCitations.value = res.citations || guidedCitations.value
}

function finalizeGuidedResponse(res: GuidedResponse, assistantIndex: number) {
  guidedSessionId.value = res.sessionId
  applyGuidedMetadata(res)
  if (assistantIndex >= 0) {
    messages.value[assistantIndex].content = res.message || messages.value[assistantIndex].content
  } else {
    messages.value.push({ role: 'assistant', content: res.message })
  }
}

async function submitCheck() {
  if (!task.value || !submissionInput.value.trim()) return

  checkLoading.value = true
  try {
    if (activeQuestion.value) {
      const submittedInput = submissionInput.value
      if (shouldUseAiQuestionCheck(activeQuestion.value)) {
        checkResult.value = await api.aiCheck({
          courseLineId: task.value.course_line_id,
          moduleId: task.value.module_id,
          taskId: task.value.id,
          studentId: studentId.value,
          artifactType: task.value.required_artifact_type,
          studentInput: submittedInput,
          questionId: activeQuestion.value.id,
          chatHistory: messages.value,
        })
        messages.value.push({ role: 'student', content: `提交答案：\n\n${formatSubmittedAnswer(activeQuestion.value, submittedInput)}` })
        messages.value.push({ role: 'assistant', content: checkResult.value.reply })
        await scrollToBottom()
        return
      }
      const localResult = checkPublishedQuestion(activeQuestion.value, submittedInput)
      checkResult.value = localResult
      messages.value.push({ role: 'student', content: `提交答案：\n\n${formatSubmittedAnswer(activeQuestion.value, submittedInput)}` })
      messages.value.push({ role: 'assistant', content: localResult.reply })
      await api.recordLocalCheck({
        courseLineId: task.value.course_line_id,
        moduleId: task.value.module_id,
        taskId: task.value.id,
        studentId: studentId.value,
        artifactType: task.value.required_artifact_type,
        studentInput: submittedInput,
        questionId: activeQuestion.value.id,
        result: localResult,
      })
      await scrollToBottom()
      return
    }

    checkResult.value = await api.aiCheck({
      courseLineId: task.value.course_line_id,
      moduleId: task.value.module_id,
      taskId: task.value.id,
      studentId: studentId.value,
      artifactType: task.value.required_artifact_type,
      studentInput: submissionInput.value,
      chatHistory: messages.value,
    })
    messages.value.push({ role: 'student', content: `提交验收：\n\n${submissionInput.value}` })
    messages.value.push({ role: 'assistant', content: checkResult.value.reply })
    await scrollToBottom()
  } catch (error: any) {
    messages.value.push({ role: 'assistant', content: `**验收失败**\n\n${errorMessage(error)}` })
    await scrollToBottom()
  } finally {
    checkLoading.value = false
  }
}
function checkPublishedQuestion(question: Question, rawInput: string): AICheckResult {
  const studentAnswer = normalizeAnswer(extractAnswer(rawInput), question.type)
  const correctAnswer = normalizeAnswer(question.answer, question.type)
  const isObjective = ['single_choice', 'multi_choice', 'true_false'].includes(question.type)
  const subjective = isObjective ? null : evaluateSubjectiveQuestion(question, rawInput)
  const passed = isObjective ? studentAnswer === correctAnswer : Boolean(subjective?.passed)
  const options = questionOptions(question)
  const studentText = options.find((item) => normalizeAnswer(item.key, question.type) === studentAnswer)?.text
  const correctText = options.find((item) => normalizeAnswer(item.key, question.type) === correctAnswer)?.text
  const reply = passed
    ? [
        `这道${qTypeLabel(question.type)}回答正确。`,
        `题干：${question.stem}`,
        `你的答案：${isObjective ? studentAnswer : summarizeSubmission(rawInput)}${studentText ? `（${studentText}）` : ''}`,
        question.explanation ? `解析：${question.explanation}` : '',
      ].filter(Boolean).join('\n')
    : [
        `这道${qTypeLabel(question.type)}还需要修改。`,
        `题干：${question.stem}`,
        `你的答案：${isObjective ? (studentAnswer || '未填写') : summarizeSubmission(rawInput)}${studentText ? `（${studentText}）` : ''}`,
        isObjective ? `正确答案：${correctAnswer}${correctText ? `（${correctText}）` : ''}` : '',
        subjective?.missing.length ? `缺少：${subjective.missing.join('、')}` : '',
        question.explanation ? `解析：${question.explanation}` : '',
      ].filter(Boolean).join('\n')

  return {
    passed,
    score: isObjective ? (passed ? 100 : 0) : subjective?.score || 0,
    level: passed ? 'passed' : 'needs_revision',
    reply,
    strengths: isObjective
      ? (passed ? [`已选出正确答案：${correctAnswer}`] : [])
      : (subjective?.strengths || []),
    problems: passed
      ? []
      : [
          {
            type: isObjective ? '题目答案不匹配' : '提交内容不完整',
            message: isObjective ? '本次提交按当前发布题目判分，不再按任务实践 rubric 扣分。' : '当前答案没有满足题干里的关键要求，不能按正确处理。',
            suggestion: isObjective && question.options?.length
              ? `请从 ${question.options.map((item) => item.key).join(' / ')} 中选择正确选项。`
              : subjective?.suggestion || '请根据题干补全必要字段、结构或说明。',
          },
        ],
    nextActions: passed
      ? ['可以继续下一道题，或点击提示让智能体解释本题涉及的知识点。']
      : ['回到左侧题干和智能体解析，确认关键知识点后重新填写答案。'],
    evidence: [],
    rubricScores: [],
    nextTaskUnlocked: false,
  }
}

interface SubjectiveCheck {
  passed: boolean
  score: number
  strengths: string[]
  missing: string[]
  suggestion: string
}

function evaluateSubjectiveQuestion(question: Question, rawInput: string): SubjectiveCheck {
  const answer = extractAnswer(rawInput)
  const lower = answer.toLowerCase()
  const stem = question.stem.toLowerCase()

  if (!answer.trim()) {
    return {
      passed: false,
      score: 0,
      strengths: [],
      missing: ['未填写答案'],
      suggestion: '请先在右侧写出答案，再提交验收。',
    }
  }

  if (stem.includes('建表 sql') || stem.includes('create table') || stem.includes('nb_expert')) {
    return evaluateCreateTableSql(answer)
  }

  if (question.type === 'code_fill') {
    return evaluateCodeFillQuestion(question, answer)
  }

  const codeCheck = evaluateCodeSyntax(question, answer)
  const expectedTokens = extractExpectedTokens(question.answer)
  const hitTokens = expectedTokens.filter((token) => lower.includes(token.toLowerCase()))
  let score = expectedTokens.length
    ? Math.round((hitTokens.length / expectedTokens.length) * 100)
    : Math.min(80, Math.max(20, Math.round(answer.length / 2)))
  if (codeCheck.errors.length) {
    score = Math.min(score, 45)
  }
  return {
    passed: codeCheck.errors.length === 0 && score >= 80 && answer.trim().length >= 6,
    score,
    strengths: [
      ...(codeCheck.language ? [`${codeCheck.language} 结构检查通过`] : []),
      ...(hitTokens.length ? [`命中关键要点：${hitTokens.slice(0, 4).join('、')}`] : []),
    ],
    missing: [
      ...codeCheck.errors,
      ...expectedTokens.filter((token) => !hitTokens.includes(token)).slice(0, 5),
    ],
    suggestion: codeCheck.errors.length
      ? '请先把代码块补成语法结构完整的代码，再提交验收。'
      : '请对照标准答案补充题干要求的关键内容。解析只用于讲解，不会作为必须填写的答案。',
  }
}

interface CodeSyntaxCheck {
  language: string
  errors: string[]
}

interface FillRequirement {
  label: string
  value: string
  kind: 'xml-tag' | 'token'
  tag?: string
}

function evaluateCodeFillQuestion(question: Question, answer: string): SubjectiveCheck {
  const codeCheck = evaluateCodeSyntax(question, answer)
  const requirements = extractCodeFillRequirements(question.answer)
  const hits = requirements.filter((item) => matchesFillRequirement(answer, item))
  const missing = requirements.filter((item) => !matchesFillRequirement(answer, item)).map((item) => item.label)
  const score = requirements.length
    ? Math.round((hits.length / requirements.length) * 100)
    : (answer.trim().length >= 6 ? 80 : 20)
  const finalScore = codeCheck.errors.length ? Math.min(score, 45) : score

  return {
    passed: codeCheck.errors.length === 0 && finalScore >= 80,
    score: finalScore,
    strengths: [
      ...(codeCheck.language ? [`${codeCheck.language} 结构检查通过`] : []),
      ...(hits.length ? [`命中答案结构：${hits.slice(0, 4).map((item) => item.label).join('、')}`] : []),
    ],
    missing: [...codeCheck.errors, ...missing.slice(0, 6)],
    suggestion: codeCheck.errors.length
      ? '请先把代码片段补成结构完整的代码，再提交验收。'
      : '请补齐标准答案中的标签、注解、方法名、字段或关键代码片段；不需要照抄解析里的中文说明。',
  }
}

function extractCodeFillRequirements(standardAnswer: string): FillRequirement[] {
  const plain = stripCodeFence(standardAnswer)
  const requirements: FillRequirement[] = []
  const xmlMatches = Array.from(plain.matchAll(/<([A-Za-z][\w.-]*)>([\s\S]*?)<\/\1>/g))
  for (const match of xmlMatches) {
    const tag = match[1]
    const value = match[2].trim()
    requirements.push({
      kind: 'xml-tag',
      tag,
      value,
      label: value ? `<${tag}>${value}</${tag}>` : `<${tag}>`,
    })
  }
  if (requirements.length) return dedupeFillRequirements(requirements)

  const quoted = Array.from(plain.matchAll(/["'`]([^"'`]{2,})["'`]/g)).map((match) => match[1].trim())
  const identifiers = plain.match(/@?[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*/g) || []
  const codeTokens = [...quoted, ...identifiers]
    .map((token) => token.replace(/^@/, '').trim())
    .filter((token) => isMeaningfulCodeToken(token))
  for (const token of codeTokens) {
    requirements.push({ kind: 'token', value: token, label: token })
  }
  return dedupeFillRequirements(requirements).slice(0, 10)
}

function dedupeFillRequirements(items: FillRequirement[]): FillRequirement[] {
  const seen = new Set<string>()
  return items.filter((item) => {
    const key = `${item.kind}:${item.tag || ''}:${item.value.toLowerCase()}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

function isMeaningfulCodeToken(token: string): boolean {
  const lower = token.toLowerCase()
  if (token.length < 2) return false
  if (/^\d+$/.test(token)) return false
  return ![
    'public', 'private', 'protected', 'class', 'interface', 'return', 'new', 'void', 'string',
    'integer', 'long', 'boolean', 'true', 'false', 'null', 'this', 'super', 'import', 'package',
    'static', 'final', 'extends', 'implements', 'if', 'else', 'for', 'while',
  ].includes(lower)
}

function matchesFillRequirement(answer: string, requirement: FillRequirement): boolean {
  if (requirement.kind === 'xml-tag' && requirement.tag) {
    const tagPattern = new RegExp(`<${escapeRegExp(requirement.tag)}\\b[^>]*>([\\s\\S]*?)<\\/${escapeRegExp(requirement.tag)}>`, 'i')
    const match = answer.match(tagPattern)
    if (!match) return false
    const actual = normalizeComparableCode(match[1])
    const expected = normalizeComparableCode(requirement.value)
    if (!expected) return true
    if (requirement.tag.toLowerCase() === 'version' && /^\d+(?:\.\d+){1,3}(?:[-.\w]*)?$/.test(actual)) return true
    return actual === expected
  }
  return normalizeComparableCode(answer).includes(normalizeComparableCode(requirement.value))
}

function normalizeComparableCode(value: string): string {
  return stripCodeFence(value)
    .replace(/\s+/g, '')
    .replace(/["'`]/g, '')
    .toLowerCase()
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function evaluateCodeSyntax(question: Question, answer: string): CodeSyntaxCheck {
  const language = detectCodeLanguage(question, answer)
  if (!language) return { language: '', errors: [] }

  const code = stripCodeFence(answer).trim()
  const errors: string[] = []
  errors.push(...validateBalancedCode(code))

  if (language === 'SQL') errors.push(...validateGenericSql(code))
  if (language === 'Java') errors.push(...validateJavaLikeCode(code))
  if (language === 'XML') errors.push(...validateXmlLikeCode(code))
  if (language === 'Vue/HTML') errors.push(...validateHtmlLikeCode(code))

  return { language, errors: Array.from(new Set(errors)) }
}

function detectCodeLanguage(question: Question, answer: string): string {
  const text = `${question.stem}\n${question.answer}\n${answer}`.toLowerCase()
  if (/\b(sql|select|insert|update|delete|create\s+table|mapper\.xml)\b/.test(text)) return text.includes('mapper.xml') || text.includes('<mapper') ? 'XML' : 'SQL'
  if (/<\?xml|<mapper|<\/mapper>|<select\s|<insert\s|<update\s|<delete\s/.test(text)) return 'XML'
  if (/<template|<\/template>|<el-|v-model|@click/.test(text)) return 'Vue/HTML'
  if (/@(get|post|put|delete)mapping|public\s+|class\s+|interface\s+|return\s+|new\s+|import\s+java|@autowired/.test(text)) return 'Java'
  if (question.type === 'code_fill') return '代码'
  return ''
}

function stripCodeFence(value: string): string {
  return value
    .replace(/^```[a-zA-Z0-9_-]*\s*/i, '')
    .replace(/```\s*$/i, '')
    .trim()
}

function validateBalancedCode(code: string): string[] {
  const errors: string[] = []
  const pairs: Record<string, string> = { ')': '(', ']': '[', '}': '{' }
  const stack: string[] = []
  let quote = ''
  let escaped = false

  for (const char of code) {
    if (quote) {
      if (escaped) {
        escaped = false
      } else if (char === '\\') {
        escaped = true
      } else if (char === quote) {
        quote = ''
      }
      continue
    }
    if (char === '"' || char === "'" || char === '`') {
      quote = char
      continue
    }
    if (char === '(' || char === '[' || char === '{') stack.push(char)
    if (char === ')' || char === ']' || char === '}') {
      if (stack.pop() !== pairs[char]) errors.push(`括号不匹配：${char}`)
    }
  }
  if (quote) errors.push('字符串引号没有闭合')
  if (stack.length) errors.push(`括号没有闭合：${stack.join(' ')}`)
  return errors
}

function validateGenericSql(code: string): string[] {
  const lower = code.toLowerCase()
  const errors: string[] = []
  if (!/;\s*$/.test(code)) errors.push('SQL 语句末尾需要分号 ;')
  if (/,\s*(from|where|set|values|\)|;)/i.test(code)) errors.push('SQL 中存在多余逗号或缺少字段')
  if (/\bselect\b/.test(lower) && !/\bfrom\b/.test(lower)) errors.push('SELECT 语句缺少 FROM')
  if (/\binsert\b/.test(lower) && !/\binto\b/.test(lower)) errors.push('INSERT 语句缺少 INTO')
  if (/\bupdate\b/.test(lower) && !/\bset\b/.test(lower)) errors.push('UPDATE 语句缺少 SET')
  if (/\bdelete\b/.test(lower) && !/\bfrom\b/.test(lower)) errors.push('DELETE 语句缺少 FROM')
  return errors
}

function validateJavaLikeCode(code: string): string[] {
  const errors: string[] = []
  const trimmed = code.trim()
  if (/@(Get|Post|Put|Delete)Mapping/.test(trimmed) && !/\{[\s\S]*\}/.test(trimmed)) {
    errors.push('Controller 方法缺少方法体大括号')
  }
  if (/\breturn\b/.test(trimmed) && !/;\s*(\/\/.*)?$/m.test(trimmed)) {
    errors.push('return 语句通常需要以分号结尾')
  }
  if (/public\s+(class|interface|enum)\b/.test(trimmed) && !/\{[\s\S]*\}/.test(trimmed)) {
    errors.push('Java 类/接口缺少完整的大括号结构')
  }
  if (/=\s*;/.test(trimmed)) errors.push('Java 赋值语句缺少右侧表达式')
  return errors
}

function validateXmlLikeCode(code: string): string[] {
  const errors: string[] = []
  if (typeof DOMParser !== 'undefined') {
    const parsed = new DOMParser().parseFromString(code, 'application/xml')
    if (parsed.querySelector('parsererror')) {
      errors.push('XML 标签没有正确闭合或嵌套')
    }
  }
  if (/<mapper\b/.test(code) && !/<\/mapper>/.test(code)) errors.push('Mapper XML 缺少 </mapper>')
  return errors
}

function validateHtmlLikeCode(code: string): string[] {
  const errors: string[] = []
  const tags = Array.from(code.matchAll(/<\/?([a-zA-Z][\w-]*)(?:\s[^>]*)?>/g))
  const stack: string[] = []
  const voidTags = new Set(['input', 'img', 'br', 'hr', 'meta', 'link'])
  for (const match of tags) {
    const full = match[0]
    const tag = match[1]
    if (voidTags.has(tag) || full.endsWith('/>')) continue
    if (full.startsWith('</')) {
      if (stack.pop() !== tag) errors.push(`HTML/Vue 标签闭合不匹配：${tag}`)
    } else {
      stack.push(tag)
    }
  }
  if (stack.length) errors.push(`HTML/Vue 标签未闭合：${stack.slice(-3).join('、')}`)
  return errors
}

function evaluateCreateTableSql(answer: string): SubjectiveCheck {
  const lower = answer.toLowerCase()
  const strengths: string[] = []
  const missing: string[] = []
  let score = 0

  const fieldCount = countSqlFields(answer)
  const indexCount = countSqlIndexes(answer)
  const hasCreateTable = /create\s+table\s+`?nb_expert`?/i.test(answer)
  const hasTableName = /\bnb_expert\b/i.test(answer)
  const syntaxErrors = validateCreateTableSyntax(answer)

  if (hasCreateTable) {
    score += 15
    strengths.push('包含 CREATE TABLE nb_expert')
  } else if (/create\s+table/.test(lower)) {
    score += 8
    missing.push('CREATE TABLE nb_expert 语句')
  } else {
    missing.push('CREATE TABLE nb_expert 语句')
  }

  if (hasTableName) {
    score += 10
    strengths.push('表名为 nb_expert')
  } else {
    missing.push('表名 nb_expert')
  }

  if (fieldCount >= 8) {
    score += 25
    strengths.push(`包含 ${fieldCount} 个字段`)
  } else {
    score += Math.min(20, fieldCount * 2)
    missing.push(`至少 8 个字段（当前识别到 ${fieldCount} 个）`)
  }

  if (indexCount >= 2) {
    score += 20
    strengths.push(`包含 ${indexCount} 个索引`)
  } else {
    score += indexCount * 8
    missing.push(`至少 2 个索引（当前识别到 ${indexCount} 个）`)
  }

  const requiredChecks = [
    { label: 'VARCHAR(50) 主键', ok: /varchar\s*\(\s*50\s*\)/.test(lower) && /primary\s+key/.test(lower) },
    { label: 'LONGTEXT 字段', ok: lower.includes('longtext') },
    { label: '状态字段', ok: /\bstatus\b/.test(lower) },
    { label: '公共时间字段', ok: /create_?time|update_?time/.test(lower) },
  ]
  for (const item of requiredChecks) {
    if (item.ok) {
      score += 7
      strengths.push(item.label)
    } else {
      missing.push(item.label)
    }
  }

  score = Math.min(100, score)
  if (syntaxErrors.length) {
    missing.unshift(...syntaxErrors)
    score = Math.min(score, 45)
  }
  return {
    passed: syntaxErrors.length === 0 && hasCreateTable && hasTableName && score >= 80 && fieldCount >= 8 && indexCount >= 2,
    score,
    strengths,
    missing,
    suggestion: '请补完整 CREATE TABLE nb_expert，至少 8 个字段、2 个索引，并包含主键、简介 LONGTEXT、状态和创建/更新时间等公共字段。',
  }
}

function validateCreateTableSyntax(answer: string): string[] {
  const sql = stripSqlCodeFence(answer).trim()
  const errors: string[] = []

  if (!/^create\s+table\s+`?nb_expert`?\s*\(/i.test(sql)) {
    errors.push('SQL 必须以 CREATE TABLE nb_expert ( 开头')
  }
  if (!/;\s*$/.test(sql)) {
    errors.push('建表语句末尾需要分号 ;')
  }
  if (!hasBalancedParentheses(sql)) {
    errors.push('括号不匹配，请检查字段列表的 ( 和 )')
  }

  const openIndex = sql.search(/\(/)
  const closeIndex = findMatchingCreateTableClose(sql, openIndex)
  if (openIndex < 0 || closeIndex < 0) {
    errors.push('没有找到完整的字段定义括号体')
    return Array.from(new Set(errors))
  }

  const before = sql.slice(0, openIndex)
  const after = sql.slice(closeIndex + 1).trim()
  if (!/create\s+table\s+`?nb_expert`?\s*$/i.test(before)) {
    errors.push('CREATE TABLE 与表名位置不正确')
  }
  if (after && !/^engine\s*=|^default\s+charset|^comment\s*=|^charset\s*=|^collate\s*=|^;/i.test(after)) {
    errors.push('字段定义括号结束后只能跟 ENGINE/CHARSET/COMMENT 等表选项')
  }

  const definitions = splitSqlDefinitions(sql.slice(openIndex + 1, closeIndex))
  if (!definitions.length) {
    errors.push('字段定义不能为空')
  }
  const invalidDefinitions = definitions.filter((item) => !isValidCreateTableDefinition(item))
  if (invalidDefinitions.length) {
    errors.push(`存在不完整或非法的字段/索引定义：${invalidDefinitions.slice(0, 3).join('；')}`)
  }

  const rawBody = sql.slice(openIndex + 1, closeIndex).trim()
  if (/,\s*$/.test(rawBody)) {
    errors.push('最后一个字段或索引定义后面不要保留多余逗号')
  }

  return Array.from(new Set(errors))
}

function stripSqlCodeFence(value: string): string {
  return value
    .replace(/^```(?:sql)?\s*/i, '')
    .replace(/```\s*$/i, '')
    .trim()
}

function hasBalancedParentheses(value: string): boolean {
  let depth = 0
  for (const char of value) {
    if (char === '(') depth += 1
    if (char === ')') depth -= 1
    if (depth < 0) return false
  }
  return depth === 0
}

function findMatchingCreateTableClose(sql: string, openIndex: number): number {
  if (openIndex < 0) return -1
  let depth = 0
  for (let index = openIndex; index < sql.length; index += 1) {
    const char = sql[index]
    if (char === '(') depth += 1
    if (char === ')') {
      depth -= 1
      if (depth === 0) return index
    }
  }
  return -1
}

function splitSqlDefinitions(body: string): string[] {
  const parts: string[] = []
  let current = ''
  let depth = 0
  for (const char of body) {
    if (char === '(') depth += 1
    if (char === ')') depth -= 1
    if (char === ',' && depth === 0) {
      if (current.trim()) parts.push(current.trim())
      current = ''
      continue
    }
    current += char
  }
  if (current.trim()) parts.push(current.trim())
  return parts
}

function isValidCreateTableDefinition(definition: string): boolean {
  const normalized = definition.trim().replace(/`/g, '').toLowerCase()
  if (!normalized) return false
  if (/^(primary\s+key|index|key|unique\s+key|unique\s+index|constraint|foreign\s+key)\b/.test(normalized)) {
    return /\(.+\)/.test(normalized)
  }
  if (/^(engine|charset|default|comment)\b/.test(normalized)) return false
  return /^[a-z_][a-z0-9_]*\s+(varchar|char|longtext|text|int|bigint|tinyint|decimal|datetime|timestamp|date|blob)\b/.test(normalized)
}

function countSqlFields(answer: string): number {
  const body = answer.match(/\(([\s\S]*)\)/)?.[1] || answer
  return body
    .split(/\n|,/)
    .map((line) => line.trim().replace(/`/g, '').toLowerCase())
    .filter((line) => line && !/^(primary|key|index|unique|constraint|foreign|comment|engine)\b/.test(line))
    .filter((line) => /^[a-z_][a-z0-9_]*\s+[a-z]/.test(line)).length
}

function countSqlIndexes(answer: string): number {
  const lower = answer.toLowerCase()
  const inline = (lower.match(/\b(key|index|unique\s+key|unique\s+index)\s+[`a-z_]/g) || []).length
  const create = (lower.match(/create\s+(unique\s+)?index\s+/g) || []).length
  const primary = /primary\s+key/.test(lower) ? 1 : 0
  return inline + create + primary
}

function extractExpectedTokens(text: string): string[] {
  const tokens = text.match(/[A-Za-z_][A-Za-z0-9_]{2,}|[\u4e00-\u9fff]{2,}/g) || []
  return Array.from(new Set(tokens)).filter((token) => !['需要', '学生', '理解', '掌握', '题目', '解析'].includes(token)).slice(0, 8)
}

function summarizeSubmission(rawInput: string): string {
  const answer = extractAnswer(rawInput).trim()
  if (!answer) return '未填写'
  return answer.length > 80 ? `${answer.slice(0, 80)}...` : answer
}

function extractAnswer(rawInput: string): string {
  const markerMatch = rawInput.match(/(?:我的答案|答案|answer)\s*[:：]\s*([\s\S]*)/i)
  return (markerMatch?.[1] || rawInput).trim()
}

function normalizeAnswer(value: string, type: string): string {
  if (type === 'true_false') {
    const lower = value.trim().toLowerCase()
    if (['true', 't', 'yes', 'y', '1', '正确', '对', '是'].includes(lower)) return 'T'
    if (['false', 'f', 'no', 'n', '0', '错误', '错', '否'].includes(lower)) return 'F'
  }
  const cleaned = value
    .replace(/[`"'，。；;、\s]/g, '')
    .replace(/[（）()]/g, '')
    .trim()
    .toUpperCase()

  if (type === 'multi_choice') {
    return Array.from(new Set(cleaned.split('').filter(Boolean))).sort().join('')
  }
  return cleaned.slice(0, 1)
}

function isObjectiveQuestion(question: Question): boolean {
  return ['single_choice', 'multi_choice', 'true_false'].includes(question.type)
}

function shouldUseAiQuestionCheck(question: Question): boolean {
  return ['short_answer', 'code_fill'].includes(question.type)
}

function codeFillPreview(question: Question): string {
  const underline = '__________'
  return question.stem
    .replace(/```[\w-]*\n?/g, '')
    .replace(/```/g, '')
    .replace(/<!--\s*TODO[\s\S]*?-->/gi, underline)
    .replace(/\/\*\s*TODO[\s\S]*?\*\//gi, underline)
    .replace(/\/\/\s*TODO[^\n]*/gi, underline)
    .replace(/#\s*TODO[^\n]*/gi, underline)
    .replace(/TODO[:：]?[^\n]*/gi, underline)
    .replace(/_{3,}/g, underline)
    .trim()
}

function formatSubmittedAnswer(question: Question, value: string): string {
  if (!isObjectiveQuestion(question)) return value
  const optionText = questionOptions(question)
    ?.filter((item) => value.includes(item.key))
    .map((item) => `${item.key}. ${item.text}`)
    .join('\n')
  return optionText ? `${value}\n${optionText}` : value
}

function questionOptions(question: Question) {
  if (question.options?.length) return question.options
  if (question.type === 'true_false') {
    return [
      { key: 'T', text: '正确' },
      { key: 'F', text: '错误' },
    ]
  }
  return []
}

async function loadActiveQuestion(taskId: string, questionId: string) {
  const res = await api.publishedQuestions(taskId)
  taskQuestions.value = res.questions
  activeQuestion.value = res.questions.find((item) => item.id === questionId) || null
  if (!activeQuestion.value) return

  resetAnswerForQuestion(activeQuestion.value)
  prepareLocalGuidedSteps(activeQuestion.value)
}

function resetAnswerForQuestion(question: Question) {
  selectedAnswerKeys.value = []
  if (isObjectiveQuestion(question)) {
    codeInput.value = ''
    return
  }
  if (!codeInput.value.trim()) {
    codeInput.value = question.type === 'code_fill'
      ? '// 在这里补全代码\n'
      : ''
  }
}

function toggleOptionAnswer(key: string) {
  if (!activeQuestion.value) return
  if (activeQuestion.value.type === 'multi_choice') {
    const values = new Set(selectedAnswerKeys.value)
    if (values.has(key)) values.delete(key)
    else values.add(key)
    selectedAnswerKeys.value = Array.from(values).sort()
    return
  }
  selectedAnswerKeys.value = [key]
}

function prepareLocalGuidedSteps(question: Question) {
  guidedSteps.value = [
    { title: '读题定位', goal: '先确认题型、题干要求和需要引用的项目知识点。', knowledge_points: [] },
    { title: '分析答案', goal: isObjectiveQuestion(question) ? '逐项判断选项，排除错误答案。' : '拆解标准答案需要覆盖的关键点。', knowledge_points: [] },
    { title: '提交验收', goal: '完成作答后提交验收，通过后进入下一题或返回关卡路线。', knowledge_points: [] },
  ]
  guidedCurrentStep.value = 0
  guidedTotalSteps.value = guidedSteps.value.length
  guidedStatus.value = 'waiting'
}
async function goNextQuestionOrRoadmap() {
  if (!task.value) return
  if (nextQuestion.value) {
    await switchActiveQuestion(nextQuestion.value)
    return
  }
  const nextTaskId = await resolveNextTaskId()
  if (nextTaskId) {
    await router.push({ name: 'task-workspace', params: { taskId: nextTaskId } })
    return
  }
  await router.push({ path: '/student', query: { course: task.value.course_line_id } })
}

async function goPreviousQuestion() {
  if (!previousQuestion.value) return
  await switchActiveQuestion(previousQuestion.value)
}

async function switchActiveQuestion(question: Question) {
  if (!task.value) return
  checkResult.value = null
  activeQuestion.value = question
  guidedSessionId.value = ''
  guidedIntent.value = ''
  guidedStatus.value = ''
  guidedSteps.value = []
  guidedCurrentStep.value = 0
  guidedTotalSteps.value = 0
  guidedCitations.value = []
  resetAnswerForQuestion(question)
  prepareLocalGuidedSteps(question)
  showQuestionIntro()
  await router.replace({ name: 'task-workspace', params: { taskId: task.value.id }, query: { questionId: question.id } })
  await loadLatestSubmission(task.value.id, question.id)
  await scrollToBottom()
}

async function resolveNextTaskId(): Promise<string | null> {
  if (!task.value) return null
  const map = await api.learningMap(task.value.course_line_id, studentId.value)
  const index = map.tasks.findIndex((item) => item.id === task.value?.id)
  return index >= 0 ? map.tasks[index + 1]?.id || null : null
}

function clearActiveQuestion() {
  activeQuestion.value = null
  selectedAnswerKeys.value = []
  guidedSessionId.value = ''
  guidedIntent.value = ''
  guidedStatus.value = ''
  guidedSteps.value = []
  guidedCurrentStep.value = 0
  guidedTotalSteps.value = 0
  guidedCitations.value = []

  const nextQuery = { ...route.query }
  delete nextQuery.questionId
  router.replace({ query: nextQuery })
}

function qTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    single_choice: '单选题',
    multi_choice: '多选题',
    true_false: '判断题',
    short_answer: '简答题',
    code_fill: '代码填空',
  }
  return labels[type] || type
}

function taskTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    analysis: '资料分析',
    coding: '代码练习',
    lesson_practice: '章节练习',
    project_practice: '项目实训',
    quiz: '题目练习',
  }
  return labels[type] || type.replace(/_/g, ' ')
}

function artifactTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    text: '文字答案',
    code: '代码',
    code_or_text: '代码或文字',
    java_snippet: 'Java 代码片段',
    sql: 'SQL 脚本',
    markdown: '说明文档',
  }
  return labels[type] || type.replace(/_/g, ' ')
}

function citationKindLabel(kind: string): string {
  const labels: Record<string, string> = {
    'task-upload': '任务资料',
    'course-material': '课程资料',
    'course-standard': '课程标准',
    'project-document': '项目文档',
    'database-schema': '库表结构',
    'requirement-spec': '需求规格',
    upload: '上传资料',
    web: '网页',
    'web-search': '外部网页',
  }
  return labels[kind] || kind
}

function isUrl(value: string): boolean {
  return /^https?:\/\//i.test(value)
}

function shortSource(source: string): string {
  if (!source) return '未知来源'
  if (isUrl(source)) {
    try {
      return new URL(source).hostname
    } catch {
      return source
    }
  }
  return source.length > 34 ? `${source.slice(0, 31)}...` : source
}

function errorMessage(error: any): string {
  return error?.response?.data?.detail || error?.message || '未知错误'
}
</script>

<style scoped>
.workspace-page {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  color: #172033;
}

.loading-state,
.empty-state {
  min-height: 360px;
  display: grid;
  place-items: center;
  gap: 10px;
  padding: 32px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #ffffff;
  color: #526071;
  text-align: center;
}

.empty-state {
  align-content: center;
}

.empty-state strong {
  color: #172033;
}

.empty-state p {
  margin: 0;
  max-width: 520px;
  line-height: 1.6;
}

.spin-icon {
  animation: spin 0.75s linear infinite;
}

.task-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #ffffff;
}

.task-copy {
  min-width: 0;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.task-meta span,
.artifact-pill,
.status-pill,
.question-type,
.session-status,
.source-kind {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.2;
  white-space: nowrap;
}

.task-meta span {
  background: #eef6f2;
  color: #1f6f50;
}

.task-header h1 {
  margin: 0 0 8px;
  font-size: 24px;
  line-height: 1.25;
  color: #111827;
}

.task-header p {
  max-width: 760px;
  margin: 0;
  color: #5f6b7a;
  font-size: 14px;
  line-height: 1.7;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
  flex-shrink: 0;
}

.icon-action,
.send-button,
.close-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: 8px;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.18s ease, border-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}

.icon-action {
  gap: 7px;
  min-height: 38px;
  padding: 0 13px;
  font-size: 13px;
}

.icon-action.secondary {
  background: #ffffff;
  border-color: #d7dde6;
  color: #334155;
}

.icon-action.primary {
  background: #2563eb;
  border-color: #2563eb;
  color: #ffffff;
}

.icon-action:not(:disabled):hover,
.send-button:not(:disabled):hover,
.close-button:not(:disabled):hover {
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.12);
}

.icon-action.secondary:not(:disabled):hover {
  border-color: #2563eb;
  color: #1d4ed8;
}

.icon-action:disabled,
.send-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
  box-shadow: none;
}

.workspace-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
  gap: 16px;
  align-items: stretch;
}

.dialogue-panel,
.answer-panel,
.result-section {
  min-width: 0;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #ffffff;
}

.dialogue-panel,
.answer-panel {
  display: flex;
  flex-direction: column;
  min-height: 650px;
  overflow: hidden;
}

.question-strip {
  padding: 14px 16px;
  border-bottom: 1px solid #dfe8f5;
  background: #f5f9ff;
}

.question-strip-head,
.panel-heading,
.stepper-top,
.editor-footer,
.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.status-pill {
  background: #dbeafe;
  color: #1d4ed8;
}

.question-type {
  background: #edfdf4;
  color: #15803d;
}

.close-button {
  width: 30px;
  height: 30px;
  margin-left: auto;
  background: #ffffff;
  border-color: #d7dde6;
  color: #64748b;
}

.question-stem {
  margin: 10px 0 0;
  color: #1f2937;
  font-weight: 650;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.option-list {
  display: grid;
  gap: 6px;
  margin-top: 10px;
  color: #334155;
  font-size: 13px;
  line-height: 1.5;
}

.panel-heading {
  padding: 14px 16px;
  border-bottom: 1px solid #edf0f4;
}

.panel-heading h2 {
  margin: 3px 0 0;
  color: #111827;
  font-size: 18px;
  line-height: 1.3;
}

.panel-kicker {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #526071;
  font-size: 12px;
  font-weight: 700;
}

.session-status {
  background: #f0fdf4;
  color: #15803d;
}

.guided-stepper {
  margin: 12px 16px 0;
  padding: 12px;
  border: 1px solid #d9e5f6;
  border-radius: 8px;
  background: #f8fbff;
}

.stepper-top strong {
  min-width: 0;
  color: #1f2937;
  font-size: 14px;
  overflow-wrap: anywhere;
}

.stepper-top span {
  flex-shrink: 0;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.stepper-track {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(30px, 1fr));
  gap: 6px;
  margin-top: 10px;
}

.step-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 30px;
  height: 28px;
  border-radius: 8px;
  background: #e8edf5;
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.step-dot.active {
  background: #2563eb;
  color: #ffffff;
}

.step-dot.done {
  background: #d1fae5;
  color: #047857;
}

.guided-stepper p {
  margin: 10px 0 0;
  color: #475569;
  font-size: 13px;
  line-height: 1.6;
}

.guided-stepper .stepper-tip {
  color: #64748b;
  font-size: 12px;
}

.citation-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 16px 0;
}

.citation-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  max-width: 100%;
  padding: 5px 8px;
  border: 1px solid #e3e8ef;
  border-radius: 8px;
  background: #ffffff;
  color: #475569;
  font-size: 12px;
}

.citation-item a,
.citation-item span:last-child {
  color: #1d4ed8;
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.source-kind {
  min-height: 20px;
  padding: 1px 6px;
  background: #f1f5f9;
  color: #475569;
  font-size: 11px;
}

.chat-messages {
  flex: 1;
  min-height: 320px;
  max-height: 58vh;
  overflow-y: auto;
  padding: 16px;
}

.empty-chat {
  min-height: 220px;
  display: grid;
  place-items: center;
  gap: 8px;
  color: #94a3b8;
  font-size: 13px;
}

.message-row {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 9px;
  margin-bottom: 14px;
}

.message-row.student {
  grid-template-columns: minmax(0, 1fr) 34px;
}

.message-row.student .message-avatar {
  grid-column: 2;
  grid-row: 1;
  background: #e0f2fe;
  color: #0369a1;
}

.message-row.student .message-bubble {
  grid-column: 1;
  justify-self: end;
  background: #eff6ff;
  border-color: #bfdbfe;
}

.message-row.system {
  display: flex;
  justify-content: center;
  margin: 4px 0 14px;
}

.system-bubble {
  max-width: 80%;
  padding: 5px 10px;
  border-color: transparent;
  border-radius: 999px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 12px;
  line-height: 1.4;
  text-align: center;
}

.message-avatar {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #ecfdf5;
  color: #047857;
  font-size: 12px;
  font-weight: 800;
}

.message-bubble {
  width: fit-content;
  max-width: 100%;
  padding: 11px 12px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #ffffff;
  color: #1f2937;
  line-height: 1.65;
  overflow-wrap: anywhere;
}

.message-bubble.pending {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #526071;
}

.message-content {
  font-size: 14px;
}

.message-content :deep(h3),
.message-content :deep(h4) {
  margin: 8px 0 4px;
  font-size: 14px;
  line-height: 1.4;
  color: #111827;
}

.message-content :deep(pre) {
  margin: 10px 0;
  padding: 12px;
  border-radius: 8px;
  background: #111827;
  color: #e5e7eb;
  overflow-x: auto;
}

.message-content :deep(code) {
  padding: 1px 5px;
  border-radius: 5px;
  background: #eef2f7;
  color: #0f172a;
  font-family: Consolas, 'JetBrains Mono', monospace;
  font-size: 0.92em;
}

.message-content :deep(pre code) {
  padding: 0;
  background: transparent;
  color: inherit;
}

.understood-actions {
  display: flex;
  justify-content: flex-start;
  padding: 0 12px 12px;
  background: #f8fafc;
}

.understood-button {
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 12px;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 800;
  cursor: pointer;
}

.understood-button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.chat-input {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 42px;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #edf0f4;
  background: #f8fafc;
}

.chat-input textarea {
  width: 100%;
  min-height: 44px;
  max-height: 128px;
  resize: vertical;
  border: 1px solid #d7dde6;
  border-radius: 8px;
  padding: 10px 12px;
  color: #1f2937;
  background: #ffffff;
  font: inherit;
  line-height: 1.5;
}

.chat-input textarea:focus,
.code-editor:focus,
.icon-action:focus-visible,
.send-button:focus-visible,
.close-button:focus-visible {
  outline: 3px solid rgba(37, 99, 235, 0.22);
  outline-offset: 2px;
}

.send-button {
  width: 42px;
  height: 42px;
  align-self: end;
  background: #2563eb;
  color: #ffffff;
}

.answer-panel {
  padding-bottom: 12px;
}

.artifact-pill {
  background: #f1f5f9;
  color: #475569;
}

.answer-context {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  align-self: flex-start;
  margin: 12px 16px 0;
  padding: 7px 10px;
  border-radius: 8px;
  background: #f8fafc;
  color: #475569;
  font-size: 13px;
  font-weight: 700;
}

.question-answer-options {
  display: grid;
  gap: 8px;
  margin: 12px 16px 0;
}

.answer-option {
  display: grid;
  grid-template-columns: 18px 28px minmax(0, 1fr);
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid #d7dde6;
  border-radius: 8px;
  background: #ffffff;
  color: #334155;
  cursor: pointer;
}

.answer-option.selected {
  border-color: #2563eb;
  background: #eff6ff;
  color: #1d4ed8;
}

.answer-option span {
  overflow-wrap: anywhere;
  line-height: 1.45;
}

.selected-answer-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 12px 16px 0;
  padding: 12px 14px;
  border: 1px solid rgba(37, 99, 235, 0.16);
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.06);
  color: #1e3a8a;
  font-size: 13px;
}

.selected-answer-summary span {
  font-weight: 800;
  letter-spacing: 0;
}

.code-fill-preview {
  margin: 12px 16px 0;
  padding: 12px;
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 8px;
  background: #f8fafc;
}

.code-fill-preview-title {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #0f172a;
  font-size: 13px;
}

.code-fill-preview pre {
  margin: 10px 0 0;
  max-height: 220px;
  overflow: auto;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  color: #1e293b;
  font-family: Consolas, 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.65;
}

.editor-shell {
  flex: 1;
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  min-height: 320px;
  max-height: 58vh;
  margin: 12px 16px 0;
  border: 1px solid #d7dde6;
  border-radius: 8px;
  overflow: auto;
  background: #0f172a;
}

.editor-gutter {
  display: grid;
  align-content: start;
  gap: 0;
  padding: 12px 8px;
  border-right: 1px solid rgba(148, 163, 184, 0.24);
  color: #64748b;
  font-family: Consolas, 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.7;
  text-align: right;
  user-select: none;
}

.code-editor {
  width: 100%;
  min-height: 100%;
  height: max-content;
  resize: vertical;
  border: 0;
  padding: 12px 14px;
  background: #0f172a;
  color: #dbeafe;
  caret-color: #93c5fd;
  font-family: Consolas, 'JetBrains Mono', monospace;
  font-size: 14px;
  line-height: 1.7;
}

.editor-footer {
  padding: 10px 16px 0;
  color: #64748b;
  font-size: 12px;
}

.result-section {
  padding: 16px;
}

.result-header {
  margin-bottom: 14px;
}

.result-header h2 {
  margin: 0;
  font-size: 18px;
}

.result-badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.result-badge.passed {
  background: #dcfce7;
  color: #15803d;
}

.result-badge.needs_revision,
.result-badge.blocked {
  background: #fef3c7;
  color: #b45309;
}

.score-row {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr);
  gap: 14px;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  background: #f8fafc;
}

.score-row p {
  margin: 0;
  color: #334155;
  line-height: 1.65;
}

.score-ring {
  width: 76px;
  height: 76px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: #e0f2fe;
  color: #075985;
}

.score-ring strong {
  margin-bottom: -18px;
  font-size: 24px;
}

.score-ring span {
  font-size: 12px;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.result-actions,
.question-nav-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.question-nav-actions {
  justify-content: space-between;
  gap: 12px;
}

.question-nav-actions .icon-action.primary {
  margin-left: auto;
}

.result-block {
  min-width: 0;
  padding: 12px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #ffffff;
}

.result-block h3 {
  margin: 0 0 8px;
  font-size: 14px;
}

.result-block ul {
  display: grid;
  gap: 7px;
  margin: 0;
  padding-left: 18px;
  color: #475569;
  line-height: 1.55;
}

.result-block li {
  overflow-wrap: anywhere;
}

.result-block li strong {
  margin-right: 6px;
  color: #111827;
}

.result-block li em {
  display: block;
  margin-top: 3px;
  color: #2563eb;
  font-style: normal;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1080px) {
  .workspace-grid,
  .result-grid {
    grid-template-columns: 1fr;
  }

  .dialogue-panel,
  .answer-panel {
    min-height: 560px;
  }
}

@media (max-width: 680px) {
  .task-header {
    align-items: stretch;
    flex-direction: column;
  }

  .header-actions {
    justify-content: stretch;
  }

  .icon-action {
    flex: 1;
  }

  .question-strip-head,
  .panel-heading,
  .stepper-top,
  .editor-footer,
  .result-header,
  .score-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .chat-messages {
    max-height: none;
  }

  .message-row,
  .message-row.student {
    grid-template-columns: 30px minmax(0, 1fr);
  }

  .message-row.student .message-avatar,
  .message-row.student .message-bubble {
    grid-column: auto;
  }

  .message-avatar {
    width: 30px;
    height: 30px;
  }

  .editor-shell {
    grid-template-columns: 34px minmax(0, 1fr);
  }

  .code-editor {
    font-size: 13px;
  }
}
</style>
