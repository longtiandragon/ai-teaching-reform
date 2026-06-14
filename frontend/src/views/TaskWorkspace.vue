<template>
  <div class="workspace-scene">
    <div class="grain-overlay" aria-hidden="true"></div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <span>正在加载任务...</span>
    </div>

    <template v-else-if="task">
      <!-- 头部：任务信息 + 操作 -->
      <header class="task-header">
        <div class="header-left">
          <span class="eyebrow-tag">
            <span class="tag-dot"></span>
            {{ task.type }}
          </span>
          <h1 class="task-title">{{ task.title }}</h1>
          <p class="task-goal">{{ task.goal }}</p>
        </div>
        <div class="header-actions">
          <button type="button" class="action-btn secondary" @click="getHint" :disabled="hintLoading">
            <span v-if="hintLoading" class="btn-spinner"></span>
            <span v-else class="btn-icon-inner">?</span>
            <span>提示</span>
          </button>
          <button type="button" class="action-btn dark" @click="submitCheck" :disabled="checkLoading || !codeInput.trim()">
            <span v-if="checkLoading" class="btn-spinner"></span>
            <span v-else class="btn-icon-inner">→</span>
            <span>提交验收</span>
          </button>
        </div>
      </header>

      <!-- 主体：对话 + 代码 双栏 -->
      <div class="workspace-grid">
        <!-- 左侧：AI 对话 -->
        <section class="chat-panel">
          <!-- 正在回答的题目状态栏 -->
          <div v-if="activeQuestion" class="question-status-bar">
            <div class="qsb-header">
              <span class="qsb-badge">当前正在回答</span>
              <span class="qsb-type">{{ qTypeLabel(activeQuestion.type) }}</span>
              <button class="qsb-close" @click="clearActiveQuestion" title="关闭题目">✕</button>
            </div>
            <p class="qsb-stem">{{ activeQuestion.stem }}</p>
            <div v-if="activeQuestion.options?.length" class="qsb-options">
              <span v-for="opt in activeQuestion.options" :key="opt.key" class="qsb-opt">
                {{ opt.key }}. {{ opt.text }}
              </span>
            </div>
          </div>

          <div class="panel-header">
            <span class="eyebrow-tag small">
              <span class="tag-dot"></span>
              AI 助教
            </span>
          </div>

          <div class="chat-messages" ref="chatContainer">
            <div v-for="(msg, i) in messages" :key="i" :class="['message', msg.role]">
              <div class="message-avatar" v-if="msg.role === 'assistant'">
                <span>AI</span>
              </div>
              <div class="message-bubble">
                <div class="message-content" v-html="renderMarkdown(msg.content)"></div>
              </div>
            </div>

          </div>

          <div class="chat-input">
            <textarea
              v-model="userInput"
              placeholder="输入你的问题... (Ctrl+Enter 发送)"
              rows="2"
              @keydown.enter.ctrl="sendMessage"
            ></textarea>
            <button class="send-btn" @click="sendMessage" :disabled="!userInput.trim()">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 8h12M10 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
          </div>
        </section>

        <!-- 右侧：代码编辑 -->
        <section class="code-panel">
          <div class="panel-header">
            <span class="eyebrow-tag small">
              <span class="tag-dot"></span>
              代码编辑
            </span>
            <span class="artifact-badge">{{ task.required_artifact_type }}</span>
          </div>
          <div class="code-editor-wrap">
            <div class="editor-gutter">
              <span v-for="n in 20" :key="n">{{ n }}</span>
            </div>
            <textarea
              v-model="codeInput"
              class="code-editor"
              placeholder="// 在此输入你的代码、SQL 或文字..."
              spellcheck="false"
            ></textarea>
          </div>
        </section>
      </div>

      <!-- 评分面板 -->
      <section v-if="checkResult" class="result-section">
        <div class="result-header">
          <h3>验收结果</h3>
          <span :class="['result-badge', checkResult.level]">
            {{ checkResult.passed ? '✓ 通过' : '✕ 需修改' }}
          </span>
        </div>

        <div class="result-body">
          <div class="result-score-row">
            <div class="score-circle">
              <strong>{{ checkResult.score }}</strong>
              <small>/ 100</small>
            </div>
            <p class="result-reply">{{ checkResult.reply }}</p>
          </div>

          <div class="result-details" v-if="checkResult.strengths.length || checkResult.problems.length || checkResult.nextActions.length">
            <div class="detail-section" v-if="checkResult.strengths.length">
              <h4>亮点</h4>
              <ul>
                <li v-for="(s, i) in checkResult.strengths" :key="i">{{ s }}</li>
              </ul>
            </div>
            <div class="detail-section" v-if="checkResult.problems.length">
              <h4>问题</h4>
              <ul>
                <li v-for="(p, i) in checkResult.problems" :key="i">
                  <strong>{{ p.type }}:</strong> {{ p.message }}
                  <em v-if="p.suggestion"> → {{ p.suggestion }}</em>
                </li>
              </ul>
            </div>
            <div class="detail-section" v-if="checkResult.nextActions.length">
              <h4>下一步</h4>
              <ul>
                <li v-for="(a, i) in checkResult.nextActions" :key="i">{{ a }}</li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, type LearningTaskDetail, type AICheckResult, type Question } from '../api'
import { useSessionStore } from '../stores/session'

const route = useRoute()
const router = useRouter()
const session = useSessionStore()

const loading = ref(true)
const task = ref<LearningTaskDetail | null>(null)
const codeInput = ref('')
const userInput = ref('')
const messages = ref<Array<{ role: string; content: string }>>([])
const chatContainer = ref<HTMLElement | null>(null)

const checkLoading = ref(false)
const hintLoading = ref(false)
const checkResult = ref<AICheckResult | null>(null)

// Published question state
const activeQuestion = ref<Question | null>(null)

onMounted(async () => {
  const taskId = route.params.taskId as string
  if (taskId) {
    task.value = await api.learningTask(taskId)
  }
  // Load active question from query param
  const questionId = route.query.questionId as string | undefined
  if (questionId && taskId) {
    await loadActiveQuestion(taskId, questionId)
  }
  loading.value = false
})

function renderMarkdown(text: string): string {
  return text
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="lang-$1">$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

async function sendMessage() {
  if (!userInput.value.trim() || !task.value) return
  const question = userInput.value.trim()
  messages.value.push({ role: 'student', content: question })
  userInput.value = ''
  await scrollToBottom()

  try {
    const res = await api.aiTaskChat({
      courseLineId: task.value.course_line_id,
      moduleId: task.value.module_id,
      taskId: task.value.id,
      studentId: session.currentUser?.id,
      question,
    })
    messages.value.push({ role: 'assistant', content: res.answer })
  } catch (e: any) {
    messages.value.push({ role: 'assistant', content: `错误: ${e.message}` })
  }
  await scrollToBottom()
}

async function getHint() {
  if (!task.value) return
  hintLoading.value = true
  try {
    const res = await api.aiTaskChat({
      courseLineId: task.value.course_line_id,
      moduleId: task.value.module_id,
      taskId: task.value.id,
      studentId: session.currentUser?.id,
      question: '请给我一个提示',
    })
    messages.value.push({ role: 'assistant', content: res.answer })
    await scrollToBottom()
  } finally {
    hintLoading.value = false
  }
}

async function submitCheck() {
  if (!task.value || !codeInput.value.trim()) return
  checkLoading.value = true
  try {
    checkResult.value = await api.aiCheck({
      courseLineId: task.value.course_line_id,
      moduleId: task.value.module_id,
      taskId: task.value.id,
      studentId: session.currentUser?.id || '',
      studentInput: codeInput.value,
    })
  } finally {
    checkLoading.value = false
  }
}

// ---------- Published Question ----------
async function loadActiveQuestion(taskId: string, questionId: string) {
  try {
    const res = await api.publishedQuestions(taskId)
    activeQuestion.value = res.questions.find(q => q.id === questionId) || null
    // Pre-fill code input with question context if available
    if (activeQuestion.value) {
      const q = activeQuestion.value
      const typeLabel = qTypeLabel(q.type)
      const optionsText = q.options?.map(o => `${o.key}. ${o.text}`).join('\n') || ''
      const hint = `【${typeLabel}】${q.stem}${optionsText ? '\n' + optionsText : ''}\n\n请作答：`
      // Add as first assistant message to guide the student
      messages.value.push({ role: 'assistant', content: `你正在回答一道发布题目：\n\n**${q.stem}**${optionsText ? '\n\n' + optionsText : ''}\n\n请在右侧代码编辑区写出你的答案，然后点击"提交验收"进行检查。` })
    }
  } catch { /* ignore */ }
}

function clearActiveQuestion() {
  activeQuestion.value = null
  // Remove questionId from URL without reload
  router.replace({ query: { ...route.query, questionId: undefined } })
}

function qTypeLabel(type: string): string {
  const m: Record<string, string> = { single_choice: '单选题', multi_choice: '多选题', true_false: '判断题', short_answer: '简答题', code_fill: '代码填空' }
  return m[type] || type
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

.workspace-scene {
  display: flex;
  flex-direction: column;
  gap: 24px;
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

/* ─── 加载状态 ─── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 80px 24px;
  color: #A8A29E;
  font-size: 14px;
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-top-color: #D97706;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* ─── 头部 ─── */
.task-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.05s forwards;
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
  margin-bottom: 12px;
}

.eyebrow-tag.small {
  padding: 3px 10px 3px 8px;
  font-size: 10px;
  margin-bottom: 8px;
}

.tag-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #D97706;
}

.task-title {
  margin: 0 0 8px;
  font-family: 'Playfair Display', serif;
  font-size: clamp(24px, 3vw, 36px);
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: #0F172A;
}

.task-goal {
  margin: 0;
  font-size: 14px;
  color: #78716C;
  line-height: 1.6;
  max-width: 560px;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
  font-family: inherit;
}

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.action-btn.secondary {
  background: rgba(0, 0, 0, 0.03);
  color: #78716C;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.action-btn.secondary:not(:disabled):hover {
  border-color: rgba(217, 119, 6, 0.2);
  color: #D97706;
}

.action-btn.primary {
  background: rgba(217, 119, 6, 0.08);
  color: #D97706;
}

.action-btn.primary:not(:disabled):hover {
  background: rgba(217, 119, 6, 0.14);
}

.action-btn.dark {
  background: #0F172A;
  color: #FFFBEB;
}

.action-btn.dark:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.2);
}

.btn-icon-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  font-size: 12px;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.artifact-badge {
  padding: 4px 10px;
  border-radius: 100px;
  background: rgba(0, 0, 0, 0.03);
  color: #A8A29E;
  font-size: 11px;
  font-weight: 500;
}

/* ─── 双栏布局 ─── */
.workspace-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  min-height: 420px;
  opacity: 0;
  transform: translateY(10px);
  animation: fadeUp 0.6s cubic-bezier(0.32, 0.72, 0, 1) 0.2s forwards;
}

/* ─── 对话面板 ─── */
.chat-panel {
  display: flex;
  flex-direction: column;
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.01);
  border: 1px solid rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

/* ─── 题目状态栏 ─── */
.question-status-bar {
  padding: 14px 18px;
  background: linear-gradient(135deg, rgba(217, 119, 6, 0.06), rgba(245, 158, 11, 0.04));
  border-bottom: 1px solid rgba(217, 119, 6, 0.12);
}

.qsb-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.qsb-badge {
  padding: 2px 10px;
  border-radius: 100px;
  background: #D97706;
  color: #FFFBEB;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.qsb-type {
  font-size: 11px;
  color: #D97706;
  font-weight: 600;
}

.qsb-close {
  margin-left: auto;
  background: none;
  border: none;
  cursor: pointer;
  color: #A8A29E;
  font-size: 14px;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.2s;
}

.qsb-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #0F172A;
}

.qsb-stem {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 600;
  color: #0F172A;
  line-height: 1.5;
}

.qsb-options {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.qsb-opt {
  font-size: 12px;
  color: #78716C;
  line-height: 1.4;
  padding-left: 8px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 12px;
}

.chat-messages {
  flex: 1;
  padding: 0 20px 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 420px;
}

.message {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.message.student {
  flex-direction: row-reverse;
}

.message-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 10px;
  background: rgba(217, 119, 6, 0.1);
  color: #D97706;
  font-size: 10px;
  font-weight: 700;
  flex-shrink: 0;
}

.message-bubble {
  max-width: 85%;
  padding: 12px 16px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.65;
}

.message.student .message-bubble {
  background: #0F172A;
  color: #FFFBEB;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-bubble {
  background: rgba(0, 0, 0, 0.025);
  color: #0F172A;
  border-bottom-left-radius: 4px;
}

.message-content :deep(pre) {
  background: rgba(0, 0, 0, 0.04);
  padding: 12px 14px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  margin: 10px 0;
  line-height: 1.5;
}

.message.student .message-content :deep(pre) {
  background: rgba(255, 251, 235, 0.1);
}

.message-content :deep(code) {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  padding: 1px 4px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.04);
}

.message.student .message-content :deep(code) {
  background: rgba(255, 251, 235, 0.12);
}

.message-content :deep(strong) {
  font-weight: 700;
}

.typing-dots {
  display: flex;
  gap: 4px;
  margin-bottom: 6px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #D97706;
  animation: bounce 1.2s infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

.chat-input {
  display: flex;
  gap: 10px;
  padding: 14px 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.chat-input textarea {
  flex: 1;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 13px;
  font-family: inherit;
  resize: none;
  outline: none;
  background: transparent;
  color: #0F172A;
  transition: border-color 0.3s;
}

.chat-input textarea:focus {
  border-color: #D97706;
}

.send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: #0F172A;
  color: #FFFBEB;
  cursor: pointer;
  align-self: flex-end;
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.send-btn:not(:disabled):hover {
  transform: translateY(-1px);
}

.send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* ─── 代码面板 ─── */
.code-panel {
  display: flex;
  flex-direction: column;
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.01);
  border: 1px solid rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.code-editor-wrap {
  flex: 1;
  display: flex;
  min-height: 380px;
}

.editor-gutter {
  display: flex;
  flex-direction: column;
  padding: 14px 0 14px 14px;
  color: #D4D4D4;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  line-height: 1.65;
  user-select: none;
  text-align: right;
  min-width: 36px;
}

.editor-gutter span {
  padding-right: 10px;
}

.code-editor {
  flex: 1;
  border: none;
  padding: 14px 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.65;
  resize: none;
  outline: none;
  background: transparent;
  color: #0F172A;
}

/* ─── 评分面板 ─── */
.result-section {
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.01);
  border: 1px solid rgba(0, 0, 0, 0.04);
  overflow: hidden;
  opacity: 0;
  transform: translateY(10px);
  animation: fadeUp 0.6s cubic-bezier(0.32, 0.72, 0, 1) 0.05s forwards;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.result-header h3 {
  margin: 0;
  font-family: 'Playfair Display', serif;
  font-size: 18px;
  font-weight: 600;
  color: #0F172A;
}

.result-badge {
  padding: 5px 14px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 700;
}

.result-badge.passed {
  background: rgba(125, 211, 168, 0.15);
  color: #059669;
}

.result-badge.needs_revision {
  background: rgba(217, 119, 6, 0.1);
  color: #D97706;
}

.result-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-score-row {
  display: flex;
  align-items: center;
  gap: 24px;
}

.score-circle {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: rgba(217, 119, 6, 0.06);
  flex-shrink: 0;
}

.score-circle strong {
  font-family: 'Playfair Display', serif;
  font-size: 28px;
  font-weight: 700;
  color: #D97706;
  line-height: 1;
}

.score-circle small {
  font-size: 11px;
  color: #A8A29E;
}

.result-reply {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: #0F172A;
}

.result-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.detail-section h4 {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 700;
  color: #78716C;
  letter-spacing: 0.02em;
}

.detail-section ul {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  line-height: 1.8;
  color: #0F172A;
}

.detail-section em {
  color: #D97706;
  font-style: normal;
}

/* ─── 动画 ─── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}

/* ─── 响应式 ─── */
@media (max-width: 900px) {
  .task-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .workspace-grid {
    grid-template-columns: 1fr;
  }

  .result-score-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
