<template>
  <div class="feedback-center">
    <section class="page-header">
      <div>
        <p class="eyebrow">Feedback</p>
        <h2>反馈中心</h2>
        <p>向学生发送学习反馈和改进建议，查看历史反馈记录。</p>
      </div>
    </section>

    <!-- AI 分析结果（从学生管理页跳转来时显示） -->
    <section v-if="prefilledAnalysis" class="analysis-preview panel">
      <div class="panel-title">
        <h3>AI 分析报告</h3>
        <span class="analysis-student">{{ prefilledStudentName }}</span>
      </div>
      <div class="analysis-body">
        <div v-if="prefilledAnalysis.summary" class="analysis-summary">
          <strong>总结：</strong>{{ prefilledAnalysis.summary }}
        </div>
        <div class="analysis-grid">
          <div v-if="prefilledAnalysis.strengths?.length" class="analysis-col">
            <h4 class="col-title strengths-title">优势</h4>
            <ul>
              <li v-for="(s, i) in prefilledAnalysis.strengths" :key="i">{{ s }}</li>
            </ul>
          </div>
          <div v-if="prefilledAnalysis.weaknesses?.length" class="analysis-col">
            <h4 class="col-title weaknesses-title">不足</h4>
            <ul>
              <li v-for="(w, i) in prefilledAnalysis.weaknesses" :key="i">{{ w }}</li>
            </ul>
          </div>
        </div>
        <div v-if="prefilledAnalysis.improvementPlan?.length" class="analysis-plan">
          <h4 class="col-title plan-title">改进计划</h4>
          <ul>
            <li v-for="(p, i) in prefilledAnalysis.improvementPlan" :key="i">{{ p }}</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- 发送反馈 -->
    <section class="feedback-form panel">
      <div class="panel-title">
        <h3>{{ prefilledAnalysis ? '补充反馈并发送' : '发送反馈' }}</h3>
      </div>
      <div class="form-body">
        <div class="form-field">
          <label>选择学生</label>
          <select v-model="selectedStudent">
            <option value="" disabled>请选择学生</option>
            <option v-for="s in students" :key="s.id" :value="s.id">
              {{ s.name }} ({{ s.student_no }})
            </option>
          </select>
        </div>
        <div class="form-field">
          <label>{{ prefilledAnalysis ? '补充说明（可选）' : '反馈内容' }}</label>
          <textarea v-model="feedbackContent" rows="4" :placeholder="prefilledAnalysis ? '可补充额外说明...' : '输入反馈内容...'"></textarea>
        </div>
        <button
          class="submit-btn"
          :disabled="!selectedStudent || sending"
          @click="handleSendFeedback"
        >
          {{ sending ? '发送中...' : '发送反馈' }}
        </button>
      </div>
    </section>

    <!-- 历史反馈 -->
    <section class="feedback-history panel">
      <div class="panel-title">
        <h3>反馈历史</h3>
        <button class="refresh-btn-sm" @click="loadFeedbackHistory">刷新</button>
      </div>

      <div v-if="loadingHistory" class="empty-state">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <div v-else-if="!feedbackHistory.length" class="empty-state">
        <p>暂无反馈记录。</p>
      </div>

      <div v-else class="history-list">
        <article v-for="fb in feedbackHistory" :key="fb.id" class="history-item">
          <div class="history-header">
            <span class="history-student">{{ fb.student_name || fb.student_id }}</span>
            <small class="history-no">{{ fb.student_no }}</small>
            <small class="history-time">{{ formatTime(fb.created_at) }}</small>
          </div>
          <p class="history-content">{{ fb.content }}</p>
          <div v-if="fb.analysis" class="history-analysis">
            <span v-if="fb.analysis.summary" class="history-summary">{{ fb.analysis.summary }}</span>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api'
import { useSessionStore } from '../stores/session'

const route = useRoute()
const session = useSessionStore()
const students = computed(() => session.students)
const selectedStudent = ref('')
const feedbackContent = ref('')
const sending = ref(false)
const feedbackHistory = ref<any[]>([])
const loadingHistory = ref(false)

// 从学生管理页跳转来的 AI 分析结果
const prefilledStudentId = computed(() => route.query.studentId as string || '')
const prefilledAnalysis = computed(() => {
  if (!route.query.summary) return null
  return {
    summary: route.query.summary as string || '',
    strengths: safeJsonParse(route.query.strengths as string),
    weaknesses: safeJsonParse(route.query.weaknesses as string),
    improvementPlan: safeJsonParse(route.query.improvementPlan as string),
  }
})
const prefilledStudentName = computed(() => {
  if (!prefilledStudentId.value) return ''
  const student = students.value.find(s => s.id === prefilledStudentId.value)
  return student ? student.name : prefilledStudentId.value
})

function safeJsonParse(str: string | null): string[] {
  if (!str) return []
  try { return JSON.parse(str) } catch { return [] }
}

onMounted(async () => {
  if (!session.users.length) await session.load()
  // 如果从学生管理页跳转来，自动选中学生
  if (prefilledStudentId.value) {
    selectedStudent.value = prefilledStudentId.value
  }
  await loadFeedbackHistory()
})

async function handleSendFeedback() {
  if (!session.currentUser?.id || !selectedStudent.value) return
  sending.value = true
  try {
    let content = feedbackContent.value.trim()
    // 如果有 AI 分析结果，将分析报告作为反馈内容
    if (prefilledAnalysis.value) {
      const parts = []
      if (prefilledAnalysis.value.summary) parts.push(`总结：${prefilledAnalysis.value.summary}`)
      if (prefilledAnalysis.value.strengths?.length) parts.push(`优势：${prefilledAnalysis.value.strengths.join('；')}`)
      if (prefilledAnalysis.value.weaknesses?.length) parts.push(`不足：${prefilledAnalysis.value.weaknesses.join('；')}`)
      if (prefilledAnalysis.value.improvementPlan?.length) parts.push(`改进计划：${prefilledAnalysis.value.improvementPlan.join('；')}`)
      const analysisText = parts.join('\n')
      content = content ? `${analysisText}\n\n教师补充：${content}` : analysisText
    }
    if (!content) {
      ElMessage.warning('请输入反馈内容')
      return
    }
    await api.sendFeedback(
      session.currentUser.id,
      selectedStudent.value,
      content,
      prefilledAnalysis.value || undefined,
    )
    ElMessage.success('反馈已发送')
    feedbackContent.value = ''
    selectedStudent.value = ''
    await loadFeedbackHistory()
  } catch (err: any) {
    ElMessage.error('发送失败：' + (err?.message || '未知错误'))
  } finally {
    sending.value = false
  }
}

async function loadFeedbackHistory() {
  loadingHistory.value = true
  try {
    const res = await api.getAllFeedback()
    feedbackHistory.value = res.feedback || []
  } catch {
    feedbackHistory.value = []
  } finally {
    loadingHistory.value = false
  }
}

function formatTime(value: string) {
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}
</script>

<style scoped>
.feedback-center {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header h2 {
  margin: 0 0 4px;
  font-size: 22px;
}

.page-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.panel {
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.panel-title h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary);
}

/* AI 分析预览 */
.analysis-preview {
  border-color: rgba(255, 157, 118, 0.2);
}

.analysis-student {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-primary);
}

.analysis-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.analysis-summary {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 10px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.analysis-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.analysis-col ul {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-primary);
}

.analysis-plan {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.analysis-plan ul {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-primary);
}

.col-title {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
}

.strengths-title { color: #059669; }
.weaknesses-title { color: #D97706; }
.plan-title { color: var(--accent-secondary, #C4A1FF); }

/* 表单 */
.form-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-field select,
.form-field textarea {
  padding: 10px 12px;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  font-size: 14px;
  background: var(--bg-card);
  color: var(--text-primary);
  outline: none;
  resize: vertical;
  font-family: inherit;
}

.form-field select:focus,
.form-field textarea:focus {
  border-color: var(--accent-primary);
}

.submit-btn {
  align-self: flex-end;
  padding: 10px 20px;
  border: none;
  border-radius: 100px;
  background: var(--accent-primary);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn-sm {
  padding: 5px 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 100px;
  background: transparent;
  font-size: 12px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.refresh-btn-sm:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* 历史记录 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 36px 20px;
  color: var(--text-secondary);
  font-size: 14px;
}

.loading-spinner {
  width: 22px;
  height: 22px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.history-list {
  padding: 12px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.015);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.history-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.history-student {
  font-weight: 700;
  font-size: 14px;
  color: var(--text-primary);
}

.history-no {
  font-size: 12px;
  color: var(--text-secondary);
}

.history-time {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-secondary);
}

.history-content {
  margin: 0;
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.6;
  white-space: pre-line;
}

.history-analysis {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.history-summary {
  font-size: 12px;
  color: var(--text-secondary);
  font-style: italic;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
