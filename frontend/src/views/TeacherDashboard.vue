<template>
  <main class="teacher-layout">
    <section class="teacher-hero">
      <div>
        <p class="eyebrow">Teaching Command Center</p>
        <h2>真实课程知识库与 AI 交互看板</h2>
        <p>只展示本项目已经入库的课程 Markdown、农博项目文档、需求规格、职业标准和真实交互记录。</p>
      </div>
      <div class="hero-actions">
        <el-tag :type="health?.deepseek_live ? 'success' : 'warning'">
          {{ health?.deepseek_live ? 'DeepSeek Live' : '真实调用未开启' }}
        </el-tag>
        <el-button type="primary" :icon="DatabaseZap" :loading="ingesting" @click="ingest">初始化知识库</el-button>
      </div>
    </section>

    <section class="metric-grid">
      <div v-for="metric in metrics" :key="metric.label" class="panel metric">
        <component :is="metric.icon" :size="22" />
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
      </div>
    </section>

    <section class="evidence-grid">
      <div class="panel evidence-panel">
        <div class="panel-title">
          <div>
            <p class="eyebrow">Indexed Sources</p>
            <h3>知识库真实来源</h3>
          </div>
          <ShieldCheck :size="19" />
        </div>
        <div class="source-list">
          <article v-for="source in courseSources" :key="source.title">
            <component :is="source.icon" :size="19" />
            <div>
              <strong>{{ source.title }}</strong>
              <p>{{ source.scope }}</p>
            </div>
          </article>
        </div>
      </div>

      <div class="panel runtime-panel">
        <div class="panel-title">
          <div>
            <p class="eyebrow">Runtime</p>
            <h3>系统状态</h3>
          </div>
          <ServerCog :size="19" />
        </div>
        <dl>
          <div>
            <dt>RAG 后端</dt>
            <dd>{{ health?.rag_backend || 'loading' }}</dd>
          </div>
          <div>
            <dt>知识片段</dt>
            <dd>{{ health?.rag_config?.chunks ?? '--' }}</dd>
          </div>
          <div>
            <dt>课程覆盖</dt>
            <dd>{{ analytics?.summary.kbCoverage ?? 0 }}%</dd>
          </div>
          <div>
            <dt>DeepSeek Key</dt>
            <dd>{{ health?.deepseek_configured ? '已配置' : '未配置' }}</dd>
          </div>
          <div>
            <dt>模型调用</dt>
            <dd>{{ health?.deepseek_live ? '真实请求' : '未开启' }}</dd>
          </div>
          <div>
            <dt>模型</dt>
            <dd>{{ health?.model }}</dd>
          </div>
        </dl>
      </div>
    </section>

    <section class="panel skill-panel">
      <div class="panel-title">
        <div>
          <p class="eyebrow">Agent Skills</p>
          <h3>本地 AI 工具能力</h3>
        </div>
        <Bot :size="19" />
      </div>
      <div class="skill-list">
        <article v-for="skill in skills" :key="skill.name">
          <b>{{ skill.output_type }}</b>
          <div>
            <strong>{{ skill.title }}</strong>
            <p>{{ skill.description }}</p>
            <code>{{ skill.name }}</code>
          </div>
        </article>
      </div>
    </section>

    <section class="dashboard-grid">
      <div class="panel chart-panel wide">
        <div class="panel-title">
          <div>
            <p class="eyebrow">Learning Records</p>
            <h3>真实章节交互分布</h3>
          </div>
          <Activity :size="19" />
        </div>
        <div v-if="analytics?.lessonProgress?.length" ref="progressChart" class="chart"></div>
        <div v-else class="empty-state">暂无学生交互记录，完成一次真实问答或练习后会生成分布。</div>
      </div>

      <div class="panel chart-panel">
        <div class="panel-title">
          <div>
            <p class="eyebrow">Weak Points</p>
            <h3>低分练习章节</h3>
          </div>
          <Radar :size="19" />
        </div>
        <div v-if="analytics?.weakPoints?.length" ref="weakChart" class="chart"></div>
        <div v-else class="empty-state">暂无低分练习记录，不生成虚构薄弱点。</div>
      </div>

      <div class="panel hot-panel">
        <div class="panel-title">
          <div>
            <p class="eyebrow">Question Heat</p>
            <h3>真实热点词</h3>
          </div>
          <MessageSquareText :size="19" />
        </div>
        <div v-if="analytics?.hotQuestions?.length" class="hot-list">
          <div v-for="item in analytics.hotQuestions" :key="item.keyword">
            <span>{{ item.keyword }}</span>
            <el-progress :percentage="Math.min(item.count * 12, 100)" :show-text="false" />
            <strong>{{ item.count }}</strong>
          </div>
        </div>
        <div v-else class="empty-state compact">暂无真实提问记录。</div>
      </div>

      <div class="panel coverage-panel">
        <div class="panel-title">
          <div>
            <p class="eyebrow">Knowledge Base</p>
            <h3>来源类型占比</h3>
          </div>
          <FileSearch :size="19" />
        </div>
        <div v-if="analytics?.knowledgeCoverage?.length" class="coverage-list">
          <div v-for="item in analytics.knowledgeCoverage" :key="item.name">
            <span>{{ sourceKindLabel(item.name) }} · {{ item.chunks }} 片段</span>
            <el-progress :percentage="item.covered" :stroke-width="8" />
          </div>
        </div>
        <div v-else class="empty-state compact">知识库尚未初始化。</div>
      </div>

      <div class="panel interaction-panel wide">
        <div class="panel-title">
          <div>
            <p class="eyebrow">Recent Activity</p>
            <h3>最近真实交互</h3>
          </div>
          <ClipboardCheck :size="19" />
        </div>
        <div v-if="analytics?.recentInteractions?.length" class="interaction-list">
          <article v-for="item in analytics.recentInteractions" :key="`${item.createdAt}-${item.question}`">
            <b>{{ item.kind }}</b>
            <div>
              <strong>{{ item.lessonId || item.courseId }}</strong>
              <p>{{ item.question }}</p>
              <small>{{ item.createdAt }}</small>
            </div>
            <span v-if="item.score !== null && item.score !== undefined">{{ item.score }}</span>
          </article>
        </div>
        <div v-else class="empty-state">暂无交互记录。学生端成功问答或提交练习后，这里才会出现数据。</div>
      </div>

      <div class="panel intervention-panel">
        <div class="panel-title">
          <div>
            <p class="eyebrow">Teacher Actions</p>
            <h3>干预建议</h3>
          </div>
          <ClipboardCheck :size="19" />
        </div>
        <div v-if="analytics?.interventions?.length" class="intervention-list">
          <article v-for="item in analytics.interventions" :key="item.title" :class="item.level">
            <b>{{ item.level }}</b>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.action }}</p>
            </div>
          </article>
        </div>
        <div v-else class="empty-state compact">暂无真实依据，不生成干预建议。</div>
      </div>
    </section>

    <!-- ========== 题库管理 ========== -->
    <section class="panel question-bank-panel">
      <div class="panel-title">
        <div>
          <p class="eyebrow">Question Bank</p>
          <h3>题库管理</h3>
          <small>{{ questionFilterCourse === 'nongbo-admin-project' ? '农博项目' : '12讲基础' }} · {{ questionTotal }} 题</small>
        </div>
        <div style="display:flex;gap:8px">
          <select v-model="questionFilterCourse" @change="loadQuestions" style="border:1px solid #d6e0ed;border-radius:6px;padding:6px 10px">
            <option value="springboot-course-12">12讲基础知识</option>
            <option value="nongbo-admin-project">农博项目</option>
          </select>
          <el-button type="primary" :icon="Plus" size="small" @click="openAddQuestion">新建题目</el-button>
        </div>
      </div>

      <!-- 题目列表 -->
      <div class="question-table-wrap">
        <table class="question-table" v-if="questionList.length">
          <thead>
            <tr>
              <th style="width:60px">类型</th>
              <th style="width:120px">章节</th>
              <th>题干</th>
              <th style="width:70px">难度</th>
              <th style="width:100px">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in questionList" :key="q.id">
              <td><el-tag size="small" :type="qTypeTag(q.type)">{{ qTypeLabel(q.type) }}</el-tag></td>
              <td>{{ lessonLabel(q.lesson_id) }}</td>
              <td class="stem-cell">{{ q.stem }}</td>
              <td><span :class="`diff-${q.difficulty}`">{{ q.difficulty === 'easy' ? '简单' : q.difficulty === 'medium' ? '中等' : '困难' }}</span></td>
              <td>
                <button v-if="q.id.startsWith('teacher-')" class="btn-sm" @click="editQuestion(q)">编辑</button>
                <button v-if="q.id.startsWith('teacher-')" class="btn-sm danger" @click="removeQuestion(q.id)">删除</button>
                <span v-else class="seed-badge">种子</span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state">该课程暂无题目。点击"新建题目"添加。</div>
      </div>

      <!-- 新建/编辑题目对话框 -->
      <div v-if="showQuestionForm" class="modal-overlay" @click.self="showQuestionForm = false">
        <div class="modal-card">
          <h3>{{ editingQuestion ? '编辑题目' : '新建题目' }}</h3>
          <label>章节
            <select v-model="questionForm.lesson_id">
              <option v-for="l in questionLessons" :key="l.id" :value="l.id">{{ l.title }}</option>
            </select>
          </label>
          <label>类型
            <select v-model="questionForm.type">
              <option value="single_choice">单选题</option>
              <option value="multi_choice">多选题</option>
              <option value="true_false">判断题</option>
              <option value="short_answer">简答题</option>
              <option value="code_fill">代码填空</option>
            </select>
          </label>
          <label>难度
            <select v-model="questionForm.difficulty">
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </label>
          <label>题干<textarea v-model="questionForm.stem" rows="3" style="width:100%;border:1px solid #d6e0ed;border-radius:6px;padding:8px" /></label>
          <label v-if="needsOptions(questionForm.type)">
            选项（一行一个，格式：A. 选项文本）
            <textarea v-model="optionsText" rows="4" :placeholder="'A. Result<T> 统一返回\nB. 直接返回 Entity\nC. 返回 String\nD. 返回 Map'" style="width:100%;border:1px solid #d6e0ed;border-radius:6px;padding:8px;font-family:monospace" />
          </label>
          <label>正确答案<textarea v-model="questionForm.answer" rows="2" style="width:100%;border:1px solid #d6e0ed;border-radius:6px;padding:8px" :placeholder="needsOptions(questionForm.type) ? '如: A 或 AB' : '简述评分要点或填入正确代码'" /></label>
          <label>解析（可选）<textarea v-model="questionForm.explanation" rows="2" style="width:100%;border:1px solid #d6e0ed;border-radius:6px;padding:8px" /></label>
          <div style="display:flex;gap:10px;margin-top:14px;justify-content:flex-end">
            <el-button @click="showQuestionForm = false">取消</el-button>
            <el-button type="primary" @click="saveQuestion" :loading="savingQuestion">
              {{ editingQuestion ? '保存修改' : '创建题目' }}
            </el-button>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { BarChart, RadarChart } from 'echarts/charts'
import { GridComponent, RadarComponent, TooltipComponent } from 'echarts/components'
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  Activity,
  Bot,
  ClipboardCheck,
  DatabaseZap,
  FileSearch,
  MessageSquareText,
  Radar,
  ServerCog,
  ShieldCheck,
  Target,
  Users,
  BookOpen,
  FileText,
  TableProperties,
  Plus,
} from 'lucide-vue-next'
import { ElMessage, ElButton } from 'element-plus'
import { api, type Question, type QuestionCreatePayload, type QuestionOption } from '../api'

echarts.use([BarChart, RadarChart, GridComponent, RadarComponent, TooltipComponent, CanvasRenderer])

const analytics = ref<any>(null)
const health = ref<any>(null)
const skills = ref<any[]>([])
const ingesting = ref(false)
const progressChart = ref<HTMLElement | null>(null)
const weakChart = ref<HTMLElement | null>(null)
let progressInstance: echarts.ECharts | null = null
let weakInstance: echarts.ECharts | null = null

const metrics = computed(() => [
  { label: '今日交互', value: analytics.value?.summary.activeToday ?? 0, icon: Users },
  { label: 'AI 提问', value: analytics.value?.summary.aiQuestions ?? 0, icon: Bot },
  { label: '知识片段', value: analytics.value?.summary.kbChunks ?? health.value?.rag_config?.chunks ?? 0, icon: FileSearch },
  { label: '课程覆盖', value: `${analytics.value?.summary.kbCoverage ?? 0}%`, icon: Target },
])
const courseSources = [
  { title: 'SpringBoot 12 讲 Markdown', scope: 'docs/course-materials 下的 12 篇课程整理稿', icon: BookOpen },
  { title: '农博后台真实项目', scope: '需求、接口、数据库、最终 SpringBoot/Vue 源码', icon: ClipboardCheck },
  { title: 'JavaWeb 职业技能标准', scope: '301.JavaWeb应用开发职业技能等级标准.pdf 摘要', icon: FileText },
  { title: '农宝需求规格说明书', scope: '农宝系统_需求规格说明书 v4.0.docx 后台相关内容', icon: TableProperties },
]

onMounted(load)
onBeforeUnmount(() => {
  progressInstance?.dispose()
  weakInstance?.dispose()
})

async function load() {
  try {
    ;[health.value, analytics.value, skills.value] = await Promise.all([api.health(), api.analytics(), api.skills()])
    await nextTick()
    renderCharts()
  } catch {
    ElMessage.error('教师端数据加载失败，请确认后端服务已启动。')
  }
}

async function ingest() {
  ingesting.value = true
  try {
    const result = await api.ingest()
    ElMessage.success(`知识库已就绪：${result.chunks} 个片段`)
    await load()
  } finally {
    ingesting.value = false
  }
}

function renderCharts() {
  progressInstance?.dispose()
  weakInstance?.dispose()
  progressInstance = null
  weakInstance = null

  if (progressChart.value && analytics.value?.lessonProgress?.length) {
    progressInstance = echarts.init(progressChart.value)
    progressInstance.setOption({
      tooltip: {},
      grid: { left: 38, right: 18, top: 28, bottom: 72 },
      xAxis: {
        type: 'category',
        data: analytics.value.lessonProgress.map((item: any) => item.lesson),
        axisLabel: { interval: 0, rotate: 24 },
      },
      yAxis: { type: 'value', max: 100 },
      series: [
        {
          type: 'bar',
          data: analytics.value.lessonProgress.map((item: any) => item.completed),
          itemStyle: { color: '#2c7be5', borderRadius: [5, 5, 0, 0] },
        },
      ],
    })
  }
  if (weakChart.value && analytics.value?.weakPoints?.length) {
    weakInstance = echarts.init(weakChart.value)
    weakInstance.setOption({
      tooltip: {},
      radar: {
        indicator: analytics.value.weakPoints.map((item: any) => ({ name: item.name, max: 100 })),
        radius: 96,
      },
      series: [
        {
          type: 'radar',
          data: [{ value: analytics.value.weakPoints.map((item: any) => item.value), name: '低分记录' }],
          areaStyle: { color: 'rgba(230, 126, 34, 0.2)' },
          lineStyle: { color: '#e67e22' },
          itemStyle: { color: '#e67e22' },
        },
      ],
    })
  }
}

function sourceKindLabel(kind: string) {
  const labels: Record<string, string> = {
    lesson: '章节摘要',
    practice: '练习任务',
    'course-material': '课程 Markdown',
    'project-document': '项目文档',
    'database-schema': '数据库结构',
    standard: '职业标准',
    'requirement-spec': '需求规格',
    upload: '上传资料',
  }
  return labels[kind] || kind
}

// ---------- 题库管理 ----------
const questionFilterCourse = ref('springboot-course-12')
const questionList = ref<Question[]>([])
const questionTotal = ref(0)
const showQuestionForm = ref(false)
const savingQuestion = ref(false)
const editingQuestion = ref<Question | null>(null)
const optionsText = ref('')

const questionForm = ref<QuestionCreatePayload>({
  course_id: 'springboot-course-12',
  lesson_id: '',
  type: 'single_choice',
  stem: '',
  options: null,
  answer: '',
  explanation: '',
  difficulty: 'medium',
  tags: [],
})

const questionLessons = ref<{ id: string; title: string }[]>([])

onMounted(async () => {
  await loadQuestions()
})

async function loadQuestions() {
  try {
    const res = await api.questions(questionFilterCourse.value)
    questionList.value = res.questions
    questionTotal.value = res.total
    // 收集唯一章节
    const seen = new Map<string, string>()
    for (const q of res.questions) {
      if (!seen.has(q.lesson_id)) seen.set(q.lesson_id, lessonLabel(q.lesson_id))
    }
    questionLessons.value = Array.from(seen.entries()).map(([id, title]) => ({ id, title }))
    if (questionLessons.value.length && !questionForm.value.lesson_id) {
      questionForm.value.lesson_id = questionLessons.value[0].id
    }
  } catch { /* ignore */ }
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
    'nongbo-login-auth': '农博-认证',
    'nongbo-produce-crud': '农博-CRUD',
    'nongbo-ad-credit': '农博-广告信贷',
    'nongbo-course-expert': '农博-课程专家',
    'nongbo-market-service': '农博-市场服务',
    'nongbo-full-integration': '农博-整合',
  }
  return map[lid] || lid.replace('springboot-', '').replace('nongbo-', '')
}

function qTypeTag(t: string) { return t === 'code_fill' ? '' : t === 'short_answer' ? 'success' : '' }
function qTypeLabel(t: string) {
  const m: Record<string, string> = { single_choice: '单选', multi_choice: '多选', true_false: '判断', short_answer: '简答', code_fill: '填空' }
  return m[t] || t
}

function needsOptions(t: string) { return ['single_choice', 'multi_choice', 'true_false'].includes(t) }

function openAddQuestion() {
  editingQuestion.value = null
  questionForm.value = {
    course_id: questionFilterCourse.value,
    lesson_id: questionLessons.value[0]?.id || '',
    type: 'single_choice',
    stem: '',
    options: null,
    answer: '',
    explanation: '',
    difficulty: 'medium',
    tags: [],
  }
  optionsText.value = ''
  showQuestionForm.value = true
}

function editQuestion(q: Question) {
  editingQuestion.value = q
  questionForm.value = {
    course_id: q.course_id,
    lesson_id: q.lesson_id,
    type: q.type,
    stem: q.stem,
    options: q.options ? [...q.options] : null,
    answer: q.answer,
    explanation: q.explanation,
    difficulty: q.difficulty,
    tags: [...q.tags],
  }
  optionsText.value = q.options ? q.options.map(o => `${o.key}. ${o.text}`).join('\n') : ''
  showQuestionForm.value = true
}

async function saveQuestion() {
  savingQuestion.value = true
  try {
    // 解析选项文本
    if (needsOptions(questionForm.value.type) && optionsText.value.trim()) {
      const opts: QuestionOption[] = []
      const lines = optionsText.value.trim().split('\n').filter(l => l.trim())
      for (const line of lines) {
        const m = /^([A-D])\.\s*(.+)/.exec(line.trim())
        if (m) opts.push({ key: m[1], text: m[2] })
      }
      questionForm.value.options = opts.length ? opts : null
    } else {
      questionForm.value.options = null
    }

    if (editingQuestion.value) {
      await api.updateQuestion(editingQuestion.value.id, questionForm.value)
      ElMessage.success('题目已更新')
    } else {
      await api.createQuestion(questionForm.value)
      ElMessage.success('题目已创建')
    }
    showQuestionForm.value = false
    await loadQuestions()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingQuestion.value = false
  }
}

async function removeQuestion(id: string) {
  try {
    await api.deleteQuestion(id)
    ElMessage.success('已删除')
    await loadQuestions()
  } catch {
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.teacher-layout {
  padding: 20px 28px 30px;
}

.teacher-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 20px 0 18px;
}

.teacher-hero h2 {
  margin-bottom: 8px;
  font-size: 28px;
}

.teacher-hero p:last-child {
  margin-bottom: 0;
  color: #5f6f86;
  line-height: 1.65;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.metric {
  padding: 18px;
  display: grid;
  gap: 8px;
  background: linear-gradient(180deg, #fff, #f8fbff);
}

.metric svg {
  color: #2c7be5;
}

.metric span {
  color: #61728a;
}

.metric strong {
  font-size: 30px;
}

.evidence-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.55fr);
  gap: 16px;
  margin-top: 16px;
}

.source-list {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  padding: 16px 20px 20px;
}

.source-list article {
  display: grid;
  gap: 10px;
  padding: 14px;
  border-radius: 8px;
  background: #f7fafc;
  border: 1px solid #e3ebf5;
}

.source-list svg {
  color: #20a579;
}

.source-list strong {
  display: block;
  margin-bottom: 6px;
}

.source-list p {
  margin: 0;
  color: #61728a;
  font-size: 13px;
  line-height: 1.55;
}

.runtime-panel dl {
  margin: 0;
  padding: 18px 20px;
  display: grid;
  gap: 14px;
}

.runtime-panel dl div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid rgba(39, 58, 87, 0.08);
  padding-bottom: 12px;
}

.runtime-panel dt {
  color: #65758b;
}

.runtime-panel dd {
  margin: 0;
  font-weight: 800;
  color: #24354f;
  text-align: right;
}

.skill-panel {
  margin-top: 16px;
}

.skill-list {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  padding: 16px 20px 20px;
}

.skill-list article {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 12px;
  padding: 14px;
  border-radius: 8px;
  background: #fbfcfe;
  border: 1px solid #e3ebf5;
}

.skill-list b {
  display: grid;
  place-items: center;
  height: 28px;
  border-radius: 6px;
  background: #10233f;
  color: #fff;
  font-size: 10px;
  text-transform: uppercase;
}

.skill-list strong {
  display: block;
  margin-bottom: 5px;
}

.skill-list p {
  margin: 0 0 8px;
  color: #61728a;
  font-size: 13px;
  line-height: 1.5;
}

.skill-list code {
  color: #1d5fbf;
  font-size: 12px;
  font-weight: 800;
  white-space: normal;
  word-break: break-word;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 0.9fr) minmax(310px, 0.7fr);
  gap: 16px;
  margin-top: 16px;
}

.wide {
  grid-column: span 2;
}

.chart {
  height: 330px;
}

.empty-state {
  display: grid;
  place-items: center;
  min-height: 220px;
  padding: 24px;
  color: #65758b;
  text-align: center;
  line-height: 1.6;
}

.empty-state.compact {
  min-height: 160px;
}

.hot-list,
.coverage-list,
.intervention-list,
.interaction-list {
  padding: 16px 20px 20px;
  display: grid;
  gap: 14px;
}

.hot-list div {
  display: grid;
  grid-template-columns: 90px minmax(0, 1fr) 32px;
  gap: 10px;
  align-items: center;
}

.coverage-list div {
  display: grid;
  gap: 7px;
}

.coverage-list span,
.hot-list span {
  color: #3d4f68;
  font-weight: 700;
}

.interaction-list article,
.intervention-list article {
  display: grid;
  grid-template-columns: 68px minmax(0, 1fr) 42px;
  gap: 12px;
  padding: 14px;
  border-radius: 8px;
  background: #f6f9fd;
  border: 1px solid #e4edf8;
}

.intervention-list article {
  grid-template-columns: 56px minmax(0, 1fr);
}

.interaction-list b,
.intervention-list b {
  display: grid;
  place-items: center;
  height: 28px;
  border-radius: 6px;
  background: #10233f;
  color: #fff;
  font-size: 11px;
  text-transform: uppercase;
}

.interaction-list strong,
.intervention-list strong {
  display: block;
  margin-bottom: 5px;
}

.interaction-list p,
.intervention-list p {
  margin: 0;
  color: #63738a;
  line-height: 1.45;
}

.interaction-list small {
  display: block;
  margin-top: 6px;
  color: #8794a7;
}

.interaction-list span {
  justify-self: end;
  color: #d46b08;
  font-weight: 900;
}

@media (max-width: 1180px) {
  .metric-grid,
  .evidence-grid,
  .dashboard-grid {
    grid-template-columns: 1fr 1fr;
  }

  .wide {
    grid-column: span 2;
  }

  .source-list,
  .skill-list {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 760px) {
  .teacher-layout {
    padding: 16px;
  }

  .teacher-hero,
  .hero-actions {
    align-items: flex-start;
    flex-direction: column;
  }

  .metric-grid,
  .evidence-grid,
  .dashboard-grid,
  .source-list,
  .skill-list {
    grid-template-columns: 1fr;
  }

  .wide {
    grid-column: auto;
  }
}

/* ---------- 题库管理 ---------- */
.question-bank-panel {
  margin-top: 18px;
}
.question-bank-panel small {
  color: #65758b; font-size: 13px;
}
.question-table-wrap { max-height: 400px; overflow: auto; }
.question-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.question-table th { background: #f6f9fd; padding: 10px 12px; text-align: left; font-weight: 700; color: #3d4f68; position: sticky; top: 0; }
.question-table td { padding: 10px 12px; border-bottom: 1px solid #e3ebf5; vertical-align: top; }
.stem-cell { max-width: 360px; white-space: normal; line-height: 1.5; }
.diff-easy { color: #20a579; }
.diff-medium { color: #d46b08; }
.diff-hard { color: #e03131; }
.seed-badge { color: #2c7be5; font-size: 12px; font-weight: 700; }
.btn-sm { border: 1px solid #d6e0ed; background: #fff; border-radius: 5px; padding: 4px 10px; cursor: pointer; font-size: 12px; margin-right: 6px; }
.btn-sm:hover { border-color: #2c7be5; color: #2c7be5; }
.btn-sm.danger { color: #e03131; }
.btn-sm.danger:hover { border-color: #e03131; background: #fff3f0; }
.modal-overlay { position: fixed; inset: 0; z-index: 100; background: rgba(0,0,0,0.35); display: grid; place-items: center; }
.modal-card { background: #fff; border-radius: 10px; padding: 26px 30px; width: min(600px, 92vw); max-height: 85vh; overflow: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.18); }
.modal-card h3 { margin-bottom: 16px; }
.modal-card label { display: block; margin-bottom: 12px; color: #30415f; font-weight: 700; font-size: 13px; }
.modal-card select { width: 100%; border: 1px solid #d6e0ed; border-radius: 6px; padding: 7px 10px; margin-top: 4px; }
</style>
