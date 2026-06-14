<template>
  <div class="records-scene">
    <div class="grain-overlay" aria-hidden="true"></div>

    <!-- 头部 -->
    <header class="records-header">
      <div class="header-left">
        <span class="eyebrow-tag">
          <span class="tag-dot"></span>
          Learning Records
        </span>
        <h1 class="header-title">{{ session.currentUser?.name || '学生' }}的学习档案</h1>
        <p class="header-sub">{{ session.currentUser?.class_name || '未分班' }} · 查看关卡进度、自检结果和提交反馈。</p>
      </div>
      <button type="button" class="refresh-btn" @click="loadRecords">
        <span class="btn-text">刷新记录</span>
        <span class="btn-icon">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M1.5 7a5.5 5.5 0 019.86-3.36M12.5 7a5.5 5.5 0 01-9.86 3.36" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" />
            <path d="M11.5 1.5v3h-3M2.5 12.5v-3h3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </span>
      </button>
    </header>

    <!-- 指标卡片 -->
    <section class="metrics-row">
      <div class="metric-card" v-for="(m, i) in metrics" :key="i">
        <span class="metric-label">{{ m.label }}</span>
        <strong class="metric-value">{{ m.value }}</strong>
      </div>
    </section>

    <!-- 记录列表 -->
    <section class="records-section">
      <div class="section-header">
        <div>
          <span class="eyebrow-tag small">Timeline</span>
          <h3>最近提交</h3>
        </div>
        <span class="count-badge">{{ records.length }} 条记录</span>
      </div>

      <div v-if="loading" class="empty-state">
        <div class="loading-spinner"></div>
        <span>正在读取学习记录...</span>
      </div>

      <div v-else-if="!records.length" class="empty-state">
        <p>还没有学习记录。完成一次自检或提交检查后，这里会显示结果。</p>
      </div>

      <div v-else class="record-list">
        <article
          v-for="(record, i) in records"
          :key="record.id"
          class="record-item"
          :style="{ animationDelay: (0.3 + i * 0.06) + 's' }"
        >
          <div class="record-kind" :class="record.kind">
            {{ record.kind === 'self_check' ? '自检' : '提交' }}
          </div>

          <div class="record-content">
            <h4>{{ lessonLabel(record.lesson_id) }}</h4>
            <p>{{ record.kind === 'self_check' ? `${record.correct}/${record.total} 题正确` : shortText(record.feedback || record.notes || '') }}</p>
            <small>{{ formatTime(record.created_at) }}</small>
          </div>

          <div class="record-score" v-if="record.score !== null && record.score !== undefined">
            <strong>{{ record.score }}</strong>
            <small>分</small>
          </div>

          <RouterLink
            :to="{ name: 'task-workspace', params: { taskId: record.lesson_id } }"
            class="record-link"
          >
            查看
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M2 6h8M7 3l3 3-3 3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </RouterLink>
        </article>
      </div>
    </section>

    <!-- 教师反馈 -->
    <section class="feedback-section">
      <div class="section-header">
        <div>
          <span class="eyebrow-tag small">Feedback</span>
          <h3>教师反馈</h3>
        </div>
        <span class="count-badge">{{ feedbackList.length }} 条反馈</span>
      </div>

      <div v-if="loadingFeedback" class="empty-state">
        <div class="loading-spinner"></div>
        <span>正在读取教师反馈...</span>
      </div>

      <div v-else-if="!feedbackList.length" class="empty-state">
        <p>暂无教师反馈。教师通过 AI 分析后发送的反馈会显示在这里。</p>
      </div>

      <div v-else class="feedback-list">
        <article
          v-for="(fb, i) in feedbackList"
          :key="fb.id"
          class="feedback-item"
          :style="{ animationDelay: (0.3 + i * 0.06) + 's' }"
        >
          <div class="feedback-header">
            <strong class="feedback-teacher">{{ fb.teacher_name || '教师' }}</strong>
            <small class="feedback-time">{{ formatTime(fb.created_at) }}</small>
          </div>
          <p class="feedback-content">{{ fb.content }}</p>

          <div v-if="fb.analysis" class="feedback-analysis">
            <div v-if="fb.analysis.strengths?.length" class="analysis-tag-group">
              <span class="analysis-label good">优势</span>
              <span v-for="(s, j) in fb.analysis.strengths" :key="j" class="analysis-tag good">{{ s }}</span>
            </div>
            <div v-if="fb.analysis.weaknesses?.length" class="analysis-tag-group">
              <span class="analysis-label warn">薄弱</span>
              <span v-for="(w, j) in fb.analysis.weaknesses" :key="j" class="analysis-tag warn">{{ w }}</span>
            </div>
            <div v-if="fb.analysis.improvementPlan?.length" class="analysis-plan">
              <span class="analysis-label plan">改进建议</span>
              <ul>
                <li v-for="(p, j) in fb.analysis.improvementPlan" :key="j">{{ p }}</li>
              </ul>
            </div>
            <p v-if="fb.analysis.summary" class="analysis-summary-text">{{ fb.analysis.summary }}</p>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { api, type LearningRecord } from '../api'
import { useCourseStore } from '../stores/course'
import { useSessionStore } from '../stores/session'

const store = useCourseStore()
const session = useSessionStore()
const records = ref<LearningRecord[]>([])
const loading = ref(false)
const feedbackList = ref<any[]>([])
const loadingFeedback = ref(false)

const completedLessons = computed(() => new Set(records.value.map((r) => r.lesson_id)))
const averageScore = computed(() => {
  const scores = records.value.map((r) => r.score).filter((s): s is number => typeof s === 'number')
  return scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0
})

const metrics = computed(() => [
  { label: '完成关卡', value: completedLessons.value.size },
  { label: '记录次数', value: records.value.length },
  { label: '平均得分', value: averageScore.value || '--' },
])

onMounted(async () => {
  if (!session.currentUser) await session.load()
  await store.load()
  await loadRecords()
  await loadFeedback()
})

watch(() => session.currentUser?.id, () => {
  loadRecords()
  loadFeedback()
})

async function loadRecords() {
  if (!session.currentUser?.id) return
  loading.value = true
  try {
    const res = await api.studentRecords(session.currentUser.id)
    records.value = res.records
  } finally {
    loading.value = false
  }
}

async function loadFeedback() {
  if (!session.currentUser?.id) return
  loadingFeedback.value = true
  try {
    const res = await api.getStudentFeedback(session.currentUser.id)
    feedbackList.value = res.feedback || []
  } catch {
    feedbackList.value = []
  } finally {
    loadingFeedback.value = false
  }
}

function lessonLabel(lessonId: string) {
  for (const course of store.courses) {
    const lesson = course.lessons.find((l) => l.id === lessonId)
    if (lesson) return lesson.title
  }
  return lessonId
}

function shortText(text: string) {
  return text.replace(/\s+/g, ' ').slice(0, 120) || '已提交实现说明'
}

function formatTime(value: string) {
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

.records-scene {
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

/* ─── 头部 ─── */
.records-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 40px;
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
  font-size: clamp(28px, 3.5vw, 42px);
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
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 10px 10px 18px;
  border: none;
  border-radius: 100px;
  background: #0F172A;
  color: #FFFBEB;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
  flex-shrink: 0;
}

.refresh-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.2);
}

.refresh-btn:active {
  transform: scale(0.98);
}

.btn-text {
  font-size: 13px;
  font-weight: 600;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 251, 235, 0.12);
}

/* ─── 指标卡片 ─── */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 40px;
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.2s forwards;
}

.metric-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 22px;
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.015);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.metric-label {
  font-size: 12px;
  font-weight: 600;
  color: #A8A29E;
  letter-spacing: 0.02em;
}

.metric-value {
  font-family: 'Playfair Display', serif;
  font-size: 32px;
  font-weight: 700;
  color: #0F172A;
  letter-spacing: -0.02em;
}

/* ─── 记录列表 ─── */
.records-section {
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.35s forwards;
}

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

.count-badge {
  padding: 5px 12px;
  border-radius: 100px;
  background: rgba(217, 119, 6, 0.08);
  color: #D97706;
  font-size: 12px;
  font-weight: 600;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 24px;
  color: #A8A29E;
  font-size: 14px;
}

.empty-state p {
  margin: 0;
  text-align: center;
  line-height: 1.6;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-top-color: #D97706;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.record-item {
  display: grid;
  grid-template-columns: 56px 1fr auto auto;
  gap: 16px;
  align-items: center;
  padding: 18px 20px;
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.01);
  border: 1px solid rgba(0, 0, 0, 0.03);
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
  opacity: 0;
  transform: translateY(8px);
  animation: fadeUp 0.6s cubic-bezier(0.32, 0.72, 0, 1) forwards;
}

.record-item:hover {
  border-color: rgba(217, 119, 6, 0.12);
  background: rgba(217, 119, 6, 0.02);
  transform: translateY(-1px);
}

.record-kind {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.record-kind.self_check {
  background: rgba(125, 211, 168, 0.12);
  color: #059669;
}

.record-kind.ai_practice {
  background: rgba(217, 119, 6, 0.1);
  color: #D97706;
}

.record-content h4 {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 600;
  color: #0F172A;
}

.record-content p {
  margin: 0 0 4px;
  font-size: 12px;
  color: #78716C;
  line-height: 1.5;
}

.record-content small {
  font-size: 11px;
  color: #A8A29E;
}

.record-score {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.record-score strong {
  font-family: 'Playfair Display', serif;
  font-size: 24px;
  font-weight: 700;
  color: #D97706;
}

.record-score small {
  font-size: 12px;
  color: #A8A29E;
}

.record-link {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 100px;
  background: rgba(0, 0, 0, 0.03);
  color: #78716C;
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.record-link:hover {
  background: rgba(217, 119, 6, 0.08);
  color: #D97706;
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
@media (max-width: 768px) {
  .records-scene {
    padding: 24px 20px 48px;
  }

  .records-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .metrics-row {
    grid-template-columns: 1fr;
  }

  .record-item {
    grid-template-columns: 56px 1fr;
    gap: 12px;
  }

  .record-score {
    grid-column: 2;
  }

  .record-link {
    grid-column: 2;
    justify-self: start;
  }
}

/* ─── 教师反馈 ─── */
.feedback-section {
  margin-top: 48px;
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.5s forwards;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feedback-item {
  padding: 20px 22px;
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.01);
  border: 1px solid rgba(0, 0, 0, 0.04);
  opacity: 0;
  transform: translateY(8px);
  animation: fadeUp 0.6s cubic-bezier(0.32, 0.72, 0, 1) forwards;
}

.feedback-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.feedback-teacher {
  font-size: 14px;
  font-weight: 600;
  color: #0F172A;
}

.feedback-time {
  font-size: 11px;
  color: #A8A29E;
}

.feedback-content {
  margin: 0 0 12px;
  font-size: 14px;
  color: #44403C;
  line-height: 1.65;
}

.feedback-analysis {
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.015);
  border: 1px solid rgba(0, 0, 0, 0.03);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.analysis-tag-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.analysis-label {
  padding: 2px 8px;
  border-radius: 100px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.analysis-label.good { background: rgba(5, 150, 105, 0.1); color: #059669; }
.analysis-label.warn { background: rgba(217, 119, 6, 0.1); color: #D97706; }
.analysis-label.plan { background: rgba(59, 130, 246, 0.1); color: #3B82F6; }

.analysis-tag {
  padding: 3px 10px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 500;
}

.analysis-tag.good { background: rgba(5, 150, 105, 0.06); color: #059669; }
.analysis-tag.warn { background: rgba(217, 119, 6, 0.06); color: #D97706; }

.analysis-plan ul {
  margin: 4px 0 0;
  padding-left: 16px;
}

.analysis-plan li {
  font-size: 12px;
  color: #57534E;
  line-height: 1.6;
  margin-bottom: 3px;
}

.analysis-summary-text {
  margin: 0;
  font-size: 12px;
  color: #A8A29E;
  font-style: italic;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .feedback-item {
    padding: 16px;
  }
}
</style>
