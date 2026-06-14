<template>
  <div class="student-management">
    <section class="page-header">
      <div>
        <p class="eyebrow">Students</p>
        <h2>学生管理</h2>
        <p>查看学生学习情况、薄弱环节和改进建议。</p>
      </div>
    </section>

    <section class="student-list panel">
      <div class="panel-title">
        <h3>学生列表</h3>
        <span class="muted">{{ students.length }} 名学生</span>
      </div>
      <div class="student-table">
        <div v-for="student in students" :key="student.id" class="student-row">
          <div class="student-info">
            <strong>{{ student.name }}</strong>
            <small>{{ student.student_no }} · {{ student.class_name }}</small>
          </div>
          <button class="detail-btn" @click="viewStudent(student.id)">
            查看详情
          </button>
        </div>
      </div>
    </section>

    <!-- ========== 学生进度表 ========== -->
    <section class="panel student-progress-panel">
      <div class="panel-title">
        <div>
          <p class="eyebrow">Student Progress</p>
          <h3>班级学生进度</h3>
        </div>
        <Users :size="19" />
      </div>
      <div class="student-table-wrap">
        <table class="progress-table" v-if="analytics?.studentProgress?.length">
          <thead>
            <tr>
              <th>学生</th>
              <th>课程</th>
              <th>完成</th>
              <th>平均分</th>
              <th>最近关卡</th>
              <th>最近活动</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in analytics.studentProgress" :key="student.studentId">
              <td>
                <strong>{{ student.studentName }}</strong>
                <small>{{ student.studentNo }}</small>
              </td>
              <td>{{ courseName(student.courseId) }}</td>
              <td>
                <el-progress :percentage="student.completionRate" :stroke-width="7" />
                <small>{{ student.completed }}/{{ student.total }}</small>
              </td>
              <td>{{ student.averageScore || '--' }}</td>
              <td>{{ lessonLabel(student.lastLessonId) || '未开始' }}</td>
              <td>{{ student.lastActiveAt ? formatTime(student.lastActiveAt) : '暂无' }}</td>
              <td>
                <button class="btn-sm ai-btn" @click="analyzeStudent(student)" :disabled="analyzingStudentId === student.studentId">
                  {{ analyzingStudentId === student.studentId ? '分析中...' : 'AI 分析' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state">暂无学生学习记录。学生完成自检后这里会出现进度。</div>
      </div>
    </section>

    <!-- ========== AI 分析结果弹窗 ========== -->
    <div v-if="showAnalysisModal" class="modal-overlay" @click.self="showAnalysisModal = false">
      <div class="modal-card analysis-modal">
        <div class="modal-header">
          <h3>AI 学习分析报告</h3>
          <button class="close-btn" @click="showAnalysisModal = false">&times;</button>
        </div>

        <div v-if="analysisLoading" class="analysis-loading">
          <div class="loading-spinner"></div>
          <span>正在分析学生学习数据...</span>
        </div>

        <div v-else-if="analysisResult" class="analysis-content">
          <div class="analysis-summary">
            <strong>{{ analysisResult.studentName }}</strong>
            <p>{{ analysisResult.summary }}</p>
          </div>

          <div class="analysis-section">
            <h4 class="section-label strengths-label">学习优势</h4>
            <ul v-if="analysisResult.strengths?.length">
              <li v-for="(s, i) in analysisResult.strengths" :key="i">{{ s }}</li>
            </ul>
            <p v-else class="no-data">暂无数据</p>
          </div>

          <div class="analysis-section">
            <h4 class="section-label weaknesses-label">薄弱环节</h4>
            <ul v-if="analysisResult.weaknesses?.length">
              <li v-for="(w, i) in analysisResult.weaknesses" :key="i">{{ w }}</li>
            </ul>
            <p v-else class="no-data">暂无数据</p>
          </div>

          <div class="analysis-section">
            <h4 class="section-label plan-label">改进计划</h4>
            <ul v-if="analysisResult.improvementPlan?.length">
              <li v-for="(p, i) in analysisResult.improvementPlan" :key="i">{{ p }}</li>
            </ul>
            <p v-else class="no-data">暂无数据</p>
          </div>

          <div class="analysis-section">
            <h4 class="section-label tasks-label">推荐任务</h4>
            <ul v-if="analysisResult.recommendedTasks?.length">
              <li v-for="(t, i) in analysisResult.recommendedTasks" :key="i">{{ t }}</li>
            </ul>
            <p v-else class="no-data">暂无数据</p>
          </div>

          <div class="analysis-actions">
            <button class="send-feedback-btn" @click="goToFeedback">
              发送反馈给学生 →
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== 班级 AI 分析 ========== -->
    <section class="panel class-analysis-panel">
      <div class="panel-title">
        <div>
          <p class="eyebrow">AI Class Analysis</p>
          <h3>班级 AI 分析</h3>
        </div>
        <Bot :size="19" />
      </div>
      <div class="class-analysis-body">
        <div class="class-select-row">
          <select v-model="selectedClassForAnalysis" class="class-select">
            <option value="" disabled>选择班级</option>
            <option v-for="cls in analytics?.classes || []" :key="cls.id" :value="cls.id">
              {{ cls.name }}
            </option>
          </select>
          <button class="analyze-class-btn" @click="analyzeClass" :disabled="!selectedClassForAnalysis || analyzingClass">
            {{ analyzingClass ? '分析中...' : 'AI 分析班级' }}
          </button>
        </div>

        <div v-if="classAnalysisResult" class="class-analysis-result">
          <div class="analysis-summary">
            <p>{{ classAnalysisResult.summary }}</p>
          </div>

          <div class="analysis-section">
            <h4 class="section-label weaknesses-label">全班共同薄弱点</h4>
            <ul v-if="classAnalysisResult.commonWeaknesses?.length">
              <li v-for="(w, i) in classAnalysisResult.commonWeaknesses" :key="i">{{ w }}</li>
            </ul>
          </div>

          <div class="analysis-section" v-if="classAnalysisResult.topStudents?.length">
            <h4 class="section-label strengths-label">优秀学生</h4>
            <div class="student-chip-list">
              <span v-for="s in classAnalysisResult.topStudents" :key="s.id" class="student-chip good">
                {{ s.name }} ({{ s.score }}分)
              </span>
            </div>
          </div>

          <div class="analysis-section" v-if="classAnalysisResult.strugglingStudents?.length">
            <h4 class="section-label weaknesses-label">需要关注的学生</h4>
            <div v-for="s in classAnalysisResult.strugglingStudents" :key="s.id" class="struggling-item">
              <strong>{{ s.name }}</strong>
              <ul>
                <li v-for="(issue, i) in s.issues" :key="i">{{ issue }}</li>
              </ul>
            </div>
          </div>

          <div class="analysis-section">
            <h4 class="section-label plan-label">教学建议</h4>
            <ul v-if="classAnalysisResult.recommendations?.length">
              <li v-for="(r, i) in classAnalysisResult.recommendations" :key="i">{{ r }}</li>
            </ul>
          </div>
        </div>

        <div v-else-if="!analyzingClass" class="empty-state compact">
          选择班级后点击"AI 分析班级"，系统将自动分析全班学习数据。
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'
import { Users, Bot } from 'lucide-vue-next'
import { ElMessage, ElProgress } from 'element-plus'
import { api } from '../api'

const router = useRouter()
const session = useSessionStore()
const students = computed(() => session.students)
const analytics = ref<any>(null)

// AI 分析相关
const analyzingStudentId = ref<string | null>(null)
const showAnalysisModal = ref(false)
const analysisLoading = ref(false)
const analysisResult = ref<any>(null)
const analysisStudentId = ref<string>('')
const selectedClassForAnalysis = ref('')
const analyzingClass = ref(false)
const classAnalysisResult = ref<any>(null)

onMounted(async () => {
  try {
    analytics.value = await api.analytics()
  } catch { /* ignore */ }
})

function viewStudent(id: string) {
  const student = students.value.find((s: any) => s.id === id)
  if (student) {
    analyzeStudent({ studentId: id, studentName: student.name, studentNo: student.student_no })
  }
}

function courseName(courseId: string) {
  return courseId === 'nongbo-admin-project' ? '农宝项目课' : 'SpringBoot 12 讲'
}

function formatTime(value: string) {
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

function lessonLabel(lid: string) {
  const map: Record<string, string> = {
    'springboot-03-maven-basic': '01-Maven',
    'springboot-04-springboot-web-basic': '02-DI/IoC',
    'springboot-05-mysql-sql': '03-MySQL',
    'springboot-06-jdbc-mybatis': '04-JDBC',
    'springboot-07-dept-management': '05-CRUD',
    'springboot-08-emp-query': '06-分页',
    'springboot-09-emp-save-upload-transaction': '07-事务',
    'springboot-10-emp-update-exception-report': '08-异常',
    'springboot-11-project-practice': '09-实战',
    'springboot-12-login-auth': '10-认证',
    'springboot-13-aop-log': '11-AOP',
    'springboot-14-springboot-principle': '12-原理',
    'nongbo-login-auth': '农宝-认证',
    'nongbo-produce-crud': '农宝-CRUD',
    'nongbo-ad-credit': '农宝-广告信贷',
    'nongbo-course-expert': '农宝-课程专家',
    'nongbo-market-service': '农宝-市场服务',
    'nongbo-full-integration': '农宝-整合',
  }
  return map[lid] || lid.replace('springboot-', '').replace('nongbo-', '')
}

// ---------- AI 分析 ----------
async function analyzeStudent(student: any) {
  analyzingStudentId.value = student.studentId
  showAnalysisModal.value = true
  analysisLoading.value = true
  analysisResult.value = null
  analysisStudentId.value = student.studentId
  try {
    const result = await api.analyzeStudent(student.studentId)
    analysisResult.value = result
  } catch (err: any) {
    ElMessage.error('AI 分析失败：' + (err?.message || '未知错误'))
    analysisResult.value = {
      studentName: student.studentName,
      strengths: [],
      weaknesses: ['分析请求失败'],
      improvementPlan: ['请检查 AI 配置后重试'],
      recommendedTasks: [],
      summary: '分析失败',
    }
  } finally {
    analysisLoading.value = false
    analyzingStudentId.value = null
  }
}

function goToFeedback() {
  if (!analysisStudentId.value || !analysisResult.value) return
  // 跳转到反馈中心，携带分析结果
  router.push({
    path: '/teacher/feedback',
    query: {
      studentId: analysisStudentId.value,
      summary: analysisResult.value.summary || '',
      strengths: JSON.stringify(analysisResult.value.strengths || []),
      weaknesses: JSON.stringify(analysisResult.value.weaknesses || []),
      improvementPlan: JSON.stringify(analysisResult.value.improvementPlan || []),
    },
  })
  showAnalysisModal.value = false
}

async function analyzeClass() {
  if (!selectedClassForAnalysis.value) return
  analyzingClass.value = true
  classAnalysisResult.value = null
  try {
    const result = await api.analyzeClass(selectedClassForAnalysis.value)
    classAnalysisResult.value = result
  } catch (err: any) {
    ElMessage.error('班级分析失败：' + (err?.message || '未知错误'))
  } finally {
    analyzingClass.value = false
  }
}
</script>

<style scoped>
.student-management {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
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

.student-table {
  padding: 12px 20px;
}

.student-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0,0,0,0.04);
}

.student-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.student-info strong {
  font-size: 14px;
}

.student-info small {
  color: var(--text-secondary);
  font-size: 12px;
}

.detail-btn {
  padding: 6px 12px;
  border: 1px solid var(--bg-secondary);
  border-radius: 6px;
  background: transparent;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
}

.detail-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* ---------- 学生进度表 ---------- */
.student-progress-panel {
  margin-top: 4px;
}

.student-table-wrap {
  overflow: auto;
}

.progress-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 860px;
}

.progress-table th,
.progress-table td {
  border-top: 1px solid rgba(0,0,0,0.04);
  padding: 12px 14px;
  color: var(--text-primary);
  font-size: 13px;
  text-align: left;
}

.progress-table th {
  color: var(--text-secondary);
  background: var(--bg-secondary);
  font-size: 12px;
  font-weight: 700;
}

.progress-table td strong,
.progress-table td small {
  display: block;
}

.progress-table td small {
  margin-top: 4px;
  color: var(--text-secondary);
}

.btn-sm {
  border: 1px solid rgba(0,0,0,0.08);
  background: var(--bg-card);
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 6px;
  color: var(--text-primary);
  transition: all 0.2s;
}

.btn-sm:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* ---------- AI 分析按钮 ---------- */
.ai-btn {
  border: 1px solid var(--accent-primary);
  color: var(--accent-primary);
  background: var(--bg-card);
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}
.ai-btn:hover:not(:disabled) { background: var(--accent-primary); color: #fff; }
.ai-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* ---------- AI 分析弹窗 ---------- */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0,0,0,0.35);
  display: grid;
  place-items: center;
}

.modal-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 26px 30px;
  width: min(600px, 92vw);
  max-height: 85vh;
  overflow: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.18);
}

.analysis-modal {
  width: min(680px, 92vw);
  max-height: 85vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  border: none;
  background: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0 4px;
}

.close-btn:hover {
  color: var(--text-primary);
}

.analysis-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 0;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(0,0,0,0.06);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.analysis-summary {
  padding: 14px 16px;
  border-radius: 8px;
  background: rgba(255,157,118,0.08);
  border: 1px solid rgba(255,157,118,0.15);
}

.analysis-summary strong {
  display: block;
  margin-bottom: 6px;
  font-size: 16px;
  color: var(--text-primary);
}

.analysis-summary p {
  margin: 0;
  color: var(--text-primary);
  line-height: 1.6;
}

.analysis-section { padding: 0; }
.section-label { margin: 0 0 8px; font-size: 13px; font-weight: 700; letter-spacing: 0.02em; }
.strengths-label { color: #20a579; }
.weaknesses-label { color: #e03131; }
.plan-label { color: var(--accent-primary); }
.tasks-label { color: #d46b08; }

.analysis-section ul { margin: 0; padding-left: 18px; }
.analysis-section li { margin-bottom: 6px; font-size: 13px; color: var(--text-primary); line-height: 1.55; }
.no-data { color: var(--text-secondary); font-size: 13px; font-style: italic; }

.analysis-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
  padding-top: 14px;
  border-top: 1px solid rgba(0,0,0,0.04);
}

.feedback-textarea {
  width: 100%;
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 13px;
  resize: vertical;
  font-family: inherit;
  background: var(--bg-card);
  color: var(--text-primary);
}

.feedback-textarea:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.send-feedback-btn {
  align-self: flex-end;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: var(--accent-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.send-feedback-btn:hover:not(:disabled) {
  opacity: 0.85;
}

.send-feedback-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ---------- 班级 AI 分析 ---------- */
.class-analysis-panel {
  margin-top: 16px;
}

.class-analysis-body {
  padding: 16px 20px 20px;
}

.class-select-row {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.class-select {
  flex: 1;
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  background: var(--bg-card);
  color: var(--text-primary);
}

.analyze-class-btn {
  padding: 8px 18px;
  border: none;
  border-radius: 8px;
  background: var(--accent-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.analyze-class-btn:hover:not(:disabled) {
  opacity: 0.85;
}

.analyze-class-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.class-analysis-result {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.student-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.student-chip {
  padding: 5px 12px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 600;
}

.student-chip.good {
  background: rgba(32, 165, 121, 0.1);
  color: #20a579;
}

.struggling-item {
  padding: 10px 14px;
  border-radius: 8px;
  background: rgba(224,49,49,0.04);
  border: 1px solid rgba(224,49,49,0.1);
  margin-bottom: 8px;
}

.struggling-item strong {
  display: block;
  margin-bottom: 4px;
  font-size: 13px;
  color: var(--text-primary);
}

.struggling-item ul {
  margin: 0;
  padding-left: 16px;
}

.struggling-item li {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 3px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 40px;
  color: var(--text-secondary);
  text-align: center;
}

.empty-state.compact {
  padding: 24px;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
