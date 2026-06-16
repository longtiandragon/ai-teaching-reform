<template>
  <div class="error-book-scene">
    <div class="grain-overlay" aria-hidden="true"></div>

    <!-- 头部 -->
    <header class="eb-header">
      <div>
        <span class="eyebrow-tag">
          <span class="tag-dot"></span>
          Error Book
        </span>
        <h1 class="eb-title">AI 错题本</h1>
        <p class="eb-sub">自动收集的错题和手动标记的难题，AI 帮你分析薄弱点。</p>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <span class="stat-label">总错题</span>
          <strong class="stat-value">{{ stats.total }}</strong>
        </div>
        <div class="stat-item">
          <span class="stat-label">待攻克</span>
          <strong class="stat-value accent">{{ stats.open }}</strong>
        </div>
        <div class="stat-item">
          <span class="stat-label">已掌握</span>
          <strong class="stat-value green">{{ stats.mastered }}</strong>
        </div>
      </div>
    </header>

    <!-- 知识点薄弱分析 -->
    <section v-if="knowledgeKeys.length" class="knowledge-panel">
      <h3>薄弱知识点</h3>
      <div class="knowledge-bars">
        <div v-for="k in knowledgeKeys" :key="k" class="knowledge-bar">
          <span class="bar-label">{{ k }}</span>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: Math.min(stats.byKnowledge[k] * 20, 100) + '%' }"></div>
          </div>
          <span class="bar-count">{{ stats.byKnowledge[k] }}</span>
        </div>
      </div>
    </section>

    <!-- 筛选 + 操作 -->
    <section class="toolbar">
      <div class="filter-group">
        <button
          v-for="f in filters"
          :key="f.value"
          :class="['filter-btn', { active: activeFilter === f.value }]"
          @click="activeFilter = f.value; loadEntries()"
        >
          {{ f.label }}
          <span v-if="f.count !== undefined" class="filter-count">{{ f.count }}</span>
        </button>
      </div>
      <button class="add-btn" @click="showAddForm = true">
        <Plus :size="14" />
        手动添加
      </button>
    </section>

    <!-- 错题列表 -->
    <section class="entries-list">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <div v-else-if="!entries.length" class="empty-state">
        <BookOpen :size="40" />
        <p>{{ activeFilter === 'open' ? '暂无待攻克的错题，继续加油！' : '暂无错题记录。' }}</p>
      </div>

      <article
        v-for="(entry, i) in entries"
        :key="entry.id"
        class="error-card"
        :style="{ animationDelay: (0.05 + i * 0.04) + 's' }"
      >
        <div class="card-header">
          <div class="card-tags">
            <span :class="['source-tag', entry.source_type]">{{ sourceLabel(entry.source_type) }}</span>
            <span v-if="entry.knowledge_points" class="kp-tag">{{ entry.knowledge_points.split(',')[0].trim() }}</span>
          </div>
          <div class="card-actions">
            <button v-if="entry.status === 'open'" class="action-btn" @click="markMastered(entry.id)" title="标记已掌握">
              <Check :size="14" />
            </button>
            <button class="action-btn" @click="deleteEntry(entry.id)" title="删除">
              <Trash2 :size="14" />
            </button>
          </div>
        </div>

        <div class="card-body">
          <div class="question-section">
            <h4>题目</h4>
            <pre class="code-block">{{ entry.question }}</pre>
          </div>

          <div v-if="entry.student_answer" class="answer-section">
            <h4>你的答案</h4>
            <pre class="code-block student-answer">{{ entry.student_answer }}</pre>
          </div>

          <div v-if="entry.error_analysis" class="analysis-section">
            <h4>错误分析</h4>
            <p>{{ entry.error_analysis }}</p>
          </div>

          <!-- AI 分析结果 -->
          <div v-if="entry.ai_analysis" class="ai-analysis">
            <div v-if="parseAnalysis(entry.ai_analysis).errorAnalysis" class="analysis-item">
              <strong>错误原因</strong>
              <p>{{ parseAnalysis(entry.ai_analysis).errorAnalysis }}</p>
            </div>
            <div v-if="parseAnalysis(entry.ai_analysis).correctApproach" class="analysis-item">
              <strong>正确思路</strong>
              <p>{{ parseAnalysis(entry.ai_analysis).correctApproach }}</p>
            </div>
            <div v-if="parseAnalysis(entry.ai_analysis).tips" class="analysis-item">
              <strong>改进建议</strong>
              <p>{{ parseAnalysis(entry.ai_analysis).tips }}</p>
            </div>
          </div>

          <!-- 变体练习 -->
          <div v-if="entry.variant_question" class="variant-section">
            <h4>变体练习</h4>
            <pre class="code-block variant">{{ entry.variant_question }}</pre>
            <button class="toggle-answer-btn" @click="toggleVariant(entry.id)">
              {{ showVariant[entry.id] ? '隐藏答案' : '查看答案' }}
            </button>
            <pre v-if="showVariant[entry.id]" class="code-block variant-answer">{{ entry.variant_answer }}</pre>
          </div>
        </div>

        <div class="card-footer">
          <button
            v-if="!entry.ai_analysis"
            class="footer-btn"
            @click="analyzeEntry(entry.id)"
            :disabled="analyzingId === entry.id"
          >
            <Sparkles :size="14" />
            {{ analyzingId === entry.id ? '分析中...' : 'AI 分析' }}
          </button>
          <button
            v-if="!entry.variant_question"
            class="footer-btn"
            @click="generateVariant(entry.id)"
            :disabled="generatingId === entry.id"
          >
            <RefreshCw :size="14" />
            {{ generatingId === entry.id ? '生成中...' : '生成变体题' }}
          </button>
          <span class="entry-time">{{ formatDate(entry.created_at) }}</span>
        </div>
      </article>
    </section>

    <!-- 手动添加弹窗 -->
    <div v-if="showAddForm" class="modal-overlay" @click.self="showAddForm = false">
      <div class="modal-card">
        <h3>手动添加错题</h3>
        <div class="form-field">
          <label>题目内容 *</label>
          <textarea v-model="newEntry.question" rows="3" placeholder="输入题目内容..."></textarea>
        </div>
        <div class="form-field">
          <label>你的答案</label>
          <textarea v-model="newEntry.studentAnswer" rows="2" placeholder="输入你的答案..."></textarea>
        </div>
        <div class="form-field">
          <label>正确答案</label>
          <textarea v-model="newEntry.correctAnswer" rows="2" placeholder="输入正确答案..."></textarea>
        </div>
        <div class="form-field">
          <label>知识点（逗号分隔）</label>
          <input v-model="newEntry.knowledgePoints" placeholder="如：Maven, 依赖管理" />
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showAddForm = false">取消</button>
          <button class="submit-btn" @click="addEntry" :disabled="!newEntry.question.trim()">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Check, Trash2, Sparkles, RefreshCw, BookOpen } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { api } from '../api'
import { useSessionStore } from '../stores/session'

const session = useSessionStore()
const loading = ref(false)
const entries = ref<any[]>([])
const stats = ref<any>({ total: 0, open: 0, mastered: 0, byKnowledge: {}, bySource: {} })
const activeFilter = ref('all')
const showAddForm = ref(false)
const analyzingId = ref<number | null>(null)
const generatingId = ref<number | null>(null)
const showVariant = ref<Record<number, boolean>>({})

const newEntry = ref({
  question: '',
  studentAnswer: '',
  correctAnswer: '',
  knowledgePoints: '',
})

const filters = computed(() => [
  { label: '全部', value: 'all', count: stats.value.total },
  { label: '待攻克', value: 'open', count: stats.value.open },
  { label: '已掌握', value: 'mastered', count: stats.value.mastered },
])

const knowledgeKeys = computed(() => {
  return Object.keys(stats.value.byKnowledge || {}).slice(0, 8)
})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  await Promise.all([loadEntries(), loadStats()])
}

async function loadEntries() {
  loading.value = true
  try {
    const sid = session.currentUser?.id
    if (!sid) return
    const status = activeFilter.value === 'all' ? undefined : activeFilter.value
    const res = await api.errorBook(sid, status)
    entries.value = res.entries
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  const sid = session.currentUser?.id
  if (!sid) return
  stats.value = await api.errorBookStats(sid)
}

async function addEntry() {
  if (!newEntry.value.question.trim() || !session.currentUser) return
  await api.addErrorEntry({
    studentId: session.currentUser.id,
    sourceType: 'manual',
    question: newEntry.value.question,
    studentAnswer: newEntry.value.studentAnswer,
    correctAnswer: newEntry.value.correctAnswer,
    knowledgePoints: newEntry.value.knowledgePoints,
  })
  ElMessage.success('已添加到错题本')
  showAddForm.value = false
  newEntry.value = { question: '', studentAnswer: '', correctAnswer: '', knowledgePoints: '' }
  await loadData()
}

async function markMastered(id: number) {
  await api.updateErrorEntry(id, { status: 'mastered' })
  ElMessage.success('已标记为已掌握')
  await loadData()
}

async function deleteEntry(id: number) {
  await api.deleteErrorEntry(id)
  ElMessage.success('已删除')
  await loadData()
}

async function analyzeEntry(id: number) {
  analyzingId.value = id
  try {
    const res = await api.analyzeError(id)
    if (res.ok) {
      ElMessage.success('AI 分析完成')
      await loadEntries()
    } else {
      ElMessage.error('分析失败: ' + (res.error || '未知错误'))
    }
  } finally {
    analyzingId.value = null
  }
}

async function generateVariant(id: number) {
  generatingId.value = id
  try {
    const res = await api.generateVariant(id)
    if (res.ok) {
      ElMessage.success('变体题已生成')
      await loadEntries()
    } else {
      ElMessage.error('生成失败: ' + (res.error || '未知错误'))
    }
  } finally {
    generatingId.value = null
  }
}

function toggleVariant(id: number) {
  showVariant.value[id] = !showVariant.value[id]
}

function sourceLabel(type: string) {
  const map: Record<string, string> = {
    ai_check: 'AI 验收',
    self_check: '自检',
    practice: '练习',
    manual: '手动',
  }
  return map[type] || type
}

function parseAnalysis(json: string | null): any {
  if (!json) return {}
  try { return JSON.parse(json) } catch { return {} }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

.error-book-scene {
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

/* ─── 头部 ─── */
.eb-header {
  display: flex;
  align-items: flex-start;
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

.tag-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #D97706;
}

.eb-title {
  margin: 0 0 6px;
  font-family: 'Playfair Display', serif;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0F172A;
}

.eb-sub {
  margin: 0;
  font-size: 14px;
  color: #78716C;
}

.header-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 18px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.015);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.stat-label {
  font-size: 11px;
  color: #A8A29E;
  font-weight: 500;
}

.stat-value {
  font-family: 'Playfair Display', serif;
  font-size: 24px;
  font-weight: 700;
  color: #0F172A;
  line-height: 1;
}

.stat-value.accent { color: #D97706; }
.stat-value.green { color: #059669; }

/* ─── 知识点分析 ─── */
.knowledge-panel {
  padding: 18px 22px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.012);
  border: 1px solid rgba(0, 0, 0, 0.04);
  opacity: 0;
  transform: translateY(10px);
  animation: fadeUp 0.6s cubic-bezier(0.32, 0.72, 0, 1) 0.1s forwards;
}

.knowledge-panel h3 {
  margin: 0 0 14px;
  font-family: 'Playfair Display', serif;
  font-size: 16px;
  font-weight: 600;
  color: #0F172A;
}

.knowledge-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.knowledge-bar {
  display: grid;
  grid-template-columns: 120px 1fr 32px;
  gap: 10px;
  align-items: center;
}

.bar-label {
  font-size: 12px;
  font-weight: 500;
  color: #0F172A;
  text-align: right;
}

.bar-track {
  height: 8px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, #D97706, #FFD166);
  transition: width 0.6s cubic-bezier(0.32, 0.72, 0, 1);
}

.bar-count {
  font-size: 12px;
  font-weight: 700;
  color: #D97706;
  text-align: right;
}

/* ─── 工具栏 ─── */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  opacity: 0;
  transform: translateY(10px);
  animation: fadeUp 0.6s cubic-bezier(0.32, 0.72, 0, 1) 0.15s forwards;
}

.filter-group {
  display: flex;
  gap: 6px;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 100px;
  background: transparent;
  font-size: 13px;
  font-weight: 500;
  color: #78716C;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.filter-btn:hover {
  border-color: rgba(217, 119, 6, 0.2);
}

.filter-btn.active {
  background: #D97706;
  border-color: #D97706;
  color: #FFFBEB;
}

.filter-count {
  font-size: 11px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 100px;
  background: rgba(0, 0, 0, 0.06);
}

.filter-btn.active .filter-count {
  background: rgba(255, 255, 255, 0.2);
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 100px;
  background: #0F172A;
  color: #FFFBEB;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.add-btn:hover {
  transform: translateY(-1px);
}

/* ─── 错题列表 ─── */
.entries-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.error-card {
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.012);
  border: 1px solid rgba(0, 0, 0, 0.04);
  overflow: hidden;
  opacity: 0;
  transform: translateY(8px);
  animation: fadeUp 0.5s cubic-bezier(0.32, 0.72, 0, 1) forwards;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.card-tags {
  display: flex;
  gap: 6px;
}

.source-tag {
  padding: 3px 10px;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 600;
}

.source-tag.ai_check { background: rgba(217, 119, 6, 0.1); color: #D97706; }
.source-tag.self_check { background: rgba(125, 211, 168, 0.12); color: #059669; }
.source-tag.practice { background: rgba(196, 161, 255, 0.12); color: #7C3AED; }
.source-tag.manual { background: rgba(0, 0, 0, 0.04); color: #78716C; }

.kp-tag {
  padding: 3px 10px;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 500;
  background: rgba(0, 0, 0, 0.03);
  color: #78716C;
}

.card-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #A8A29E;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.04);
  color: #0F172A;
}

.card-body {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-section h4,
.answer-section h4,
.analysis-section h4,
.variant-section h4 {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 600;
  color: #A8A29E;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.code-block {
  margin: 0;
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.03);
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #0F172A;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: auto;
}

.code-block.student-answer {
  border-left: 3px solid #D97706;
}

.code-block.variant {
  border-left: 3px solid #7C3AED;
}

.code-block.variant-answer {
  border-left: 3px solid #059669;
  margin-top: 8px;
}

.analysis-section p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #0F172A;
}

.ai-analysis {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px;
  border-radius: 12px;
  background: rgba(217, 119, 6, 0.04);
  border: 1px solid rgba(217, 119, 6, 0.1);
}

.analysis-item strong {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #D97706;
  margin-bottom: 4px;
}

.analysis-item p {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #0F172A;
}

.toggle-answer-btn {
  margin-top: 8px;
  padding: 6px 14px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 100px;
  background: transparent;
  font-size: 12px;
  font-weight: 500;
  color: #78716C;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-answer-btn:hover {
  border-color: #059669;
  color: #059669;
}

.card-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.footer-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 100px;
  background: transparent;
  font-size: 12px;
  font-weight: 500;
  color: #78716C;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.footer-btn:not(:disabled):hover {
  border-color: #D97706;
  color: #D97706;
}

.footer-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.entry-time {
  margin-left: auto;
  font-size: 11px;
  color: #A8A29E;
}

/* ─── 弹窗 ─── */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.35);
  display: grid;
  place-items: center;
  padding: 24px;
}

.modal-card {
  background: #FFFDFB;
  border-radius: 18px;
  padding: 28px;
  width: min(500px, 92vw);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.15);
}

.modal-card h3 {
  margin: 0 0 20px;
  font-family: 'Playfair Display', serif;
  font-size: 20px;
  font-weight: 600;
  color: #0F172A;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}

.form-field label {
  font-size: 12px;
  font-weight: 600;
  color: #78716C;
}

.form-field textarea,
.form-field input {
  padding: 10px 14px;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  font-size: 14px;
  font-family: inherit;
  background: transparent;
  color: #0F172A;
  outline: none;
  resize: vertical;
  transition: border-color 0.3s;
}

.form-field textarea:focus,
.form-field input:focus {
  border-color: #D97706;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn {
  padding: 10px 20px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 100px;
  background: transparent;
  font-size: 14px;
  color: #78716C;
  cursor: pointer;
}

.submit-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 100px;
  background: #D97706;
  color: #FFFBEB;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ─── 空状态 ─── */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 24px;
  color: #A8A29E;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-top-color: #D97706;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* ─── 动画 ─── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .eb-header {
    flex-direction: column;
  }
  .header-stats {
    width: 100%;
  }
  .stat-item {
    flex: 1;
  }
  .knowledge-bar {
    grid-template-columns: 80px 1fr 28px;
  }
}
</style>
