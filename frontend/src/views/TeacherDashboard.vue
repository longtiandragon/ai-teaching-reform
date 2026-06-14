<template>
  <main class="teacher-layout">
    <!-- 顶部：标题 + 操作 -->
    <section class="teacher-hero">
      <div>
        <h2>班级学习管理</h2>
        <p>查看班级进度、学生提交、自检结果和需要重点关注的学习环节。</p>
      </div>
      <div class="hero-actions">
        <el-tag :type="health?.deepseek_live ? 'success' : 'warning'" size="small">
          {{ health?.deepseek_live ? 'AI 可用' : 'AI 未连接' }}
        </el-tag>
        <el-button type="primary" :loading="ingesting" @click="ingest" size="small">
          <DatabaseZap :size="14" />
          {{ ingesting ? '初始化中...' : '初始化知识库' }}
        </el-button>
      </div>
    </section>

    <!-- 指标卡片 -->
    <section class="metric-row">
      <div v-for="metric in metrics" :key="metric.label" class="metric-card">
        <div class="metric-icon">
          <component :is="metric.icon" :size="18" />
        </div>
        <div class="metric-text">
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
        </div>
      </div>
    </section>

    <!-- 班级卡片 -->
    <section class="class-row">
      <article v-for="item in analytics?.classes || []" :key="item.id" class="class-card">
        <div class="class-info">
          <h3>{{ item.name }}</h3>
          <span>{{ item.students }} 名学生 · {{ item.records }} 条记录</span>
        </div>
        <div class="class-stats">
          <strong>{{ item.completionRate }}%</strong>
          <el-progress :percentage="item.completionRate" :stroke-width="6" :show-text="false" />
          <small>平均分 {{ item.averageScore || '--' }}</small>
        </div>
      </article>
    </section>

    <!-- 数据面板：12 列网格 -->
    <section class="dashboard-grid">
      <!-- 章节分布图：8 列 -->
      <div class="panel chart-panel col-8">
        <div class="panel-head">
          <h3>章节学习分布</h3>
          <Activity :size="16" />
        </div>
        <div v-if="analytics?.lessonProgress?.length" ref="progressChart" class="chart"></div>
        <div v-else class="empty-state">暂无学生学习记录，完成一次自检或提交后会生成分布。</div>
      </div>

      <!-- 薄弱点雷达：4 列 -->
      <div class="panel chart-panel col-4">
        <div class="panel-head">
          <h3>低分练习</h3>
          <Radar :size="16" />
        </div>
        <div v-if="analytics?.weakPoints?.length" ref="weakChart" class="chart"></div>
        <div v-else class="empty-state compact">暂无低分练习记录。</div>
      </div>

      <!-- 提问热点：6 列 -->
      <div class="panel col-6">
        <div class="panel-head">
          <h3>提问热点</h3>
          <MessageSquareText :size="16" />
        </div>
        <div v-if="analytics?.hotQuestions?.length" class="hot-list">
          <div v-for="item in analytics.hotQuestions" :key="item.keyword">
            <span class="hot-keyword">{{ item.keyword }}</span>
            <el-progress :percentage="Math.min(item.count * 12, 100)" :show-text="false" :stroke-width="6" />
            <span class="hot-count">{{ item.count }}</span>
          </div>
        </div>
        <div v-else class="empty-state compact">暂无提问记录。</div>
      </div>

      <!-- 来源占比：6 列 -->
      <div class="panel col-6">
        <div class="panel-head">
          <h3>知识库来源</h3>
          <FileSearch :size="16" />
        </div>
        <div v-if="analytics?.knowledgeCoverage?.length" class="coverage-list">
          <div v-for="item in analytics.knowledgeCoverage" :key="item.name">
            <div class="coverage-header">
              <span>{{ sourceKindLabel(item.name) }}</span>
              <span class="coverage-chunks">{{ item.chunks }} 片段</span>
            </div>
            <el-progress :percentage="item.covered" :stroke-width="6" :show-text="false" />
          </div>
        </div>
        <div v-else class="empty-state compact">知识库尚未初始化。</div>
      </div>

      <!-- 干预建议：4 列 -->
      <div class="panel col-4">
        <div class="panel-head">
          <h3>干预建议</h3>
          <ClipboardCheck :size="16" />
        </div>
        <div v-if="analytics?.interventions?.length" class="intervention-list">
          <article v-for="item in analytics.interventions" :key="item.title" :class="['intervention-item', item.level]">
            <span class="intervention-level">{{ item.level }}</span>
            <strong>{{ item.title }}</strong>
            <p>{{ item.action }}</p>
          </article>
        </div>
        <div v-else class="empty-state compact">暂无需要干预的学生。</div>
      </div>

      <!-- 最近动态：8 列 -->
      <div class="panel col-8">
        <div class="panel-head">
          <h3>最近学习动态</h3>
          <ClipboardCheck :size="16" />
        </div>
        <div v-if="analytics?.recentInteractions?.length" class="interaction-list">
          <article v-for="item in analytics.recentInteractions" :key="`${item.createdAt}-${item.question}`" class="interaction-item">
            <span class="interaction-kind">{{ item.kind }}</span>
            <div class="interaction-content">
              <strong>{{ item.lessonId || item.courseId }}</strong>
              <p>{{ item.question }}</p>
              <small>{{ item.createdAt }}</small>
            </div>
            <span v-if="item.score !== null && item.score !== undefined" class="interaction-score">{{ item.score }}</span>
          </article>
        </div>
        <div v-else class="empty-state">暂无交互记录。学生端成功问答或提交练习后，这里才会出现数据。</div>
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
  Target,
  Users,
} from 'lucide-vue-next'
import { ElMessage, ElButton } from 'element-plus'
import { api } from '../api'

echarts.use([BarChart, RadarChart, GridComponent, RadarComponent, TooltipComponent, CanvasRenderer])

const analytics = ref<any>(null)
const health = ref<any>(null)
const ingesting = ref(false)
const progressChart = ref<HTMLElement | null>(null)
const weakChart = ref<HTMLElement | null>(null)
let progressInstance: echarts.ECharts | null = null
let weakInstance: echarts.ECharts | null = null

const metrics = computed(() => [
  { label: '学生人数', value: analytics.value?.summary.students ?? 0, icon: Users },
  { label: '今日活跃', value: analytics.value?.summary.activeToday ?? 0, icon: Bot },
  { label: '整体完成率', value: `${analytics.value?.summary.completionRate ?? 0}%`, icon: Target },
  { label: '需干预', value: analytics.value?.summary.interventionTasks ?? 0, icon: ClipboardCheck },
])
onMounted(load)
onBeforeUnmount(() => {
  progressInstance?.dispose()
  weakInstance?.dispose()
})

async function load() {
  try {
    ;[health.value, analytics.value] = await Promise.all([api.health(), api.analytics()])
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


</script>

<style scoped>
.teacher-layout {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ─── Hero ─── */
.teacher-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.teacher-hero h2 {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.teacher-hero p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* ─── 指标卡片 ─── */
.metric-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  border-radius: 14px;
  background: var(--bg-card);
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.metric-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.metric-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(255, 157, 118, 0.1);
  color: var(--accent-primary);
  flex-shrink: 0;
}

.metric-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-text span {
  font-size: 12px;
  color: var(--text-secondary);
}

.metric-text strong {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

/* ─── 班级卡片 ─── */
.class-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}

.class-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 14px;
  background: var(--bg-card);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.class-info h3 {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.class-info span {
  font-size: 12px;
  color: var(--text-secondary);
}

.class-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  min-width: 80px;
}

.class-stats strong {
  font-size: 22px;
  font-weight: 700;
  color: var(--accent-primary);
  line-height: 1;
}

.class-stats small {
  font-size: 11px;
  color: var(--text-secondary);
}

/* ─── 12 列网格 ─── */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 14px;
}

.col-4 { grid-column: span 4; }
.col-6 { grid-column: span 6; }
.col-8 { grid-column: span 8; }

/* ─── 面板通用 ─── */
.panel {
  border-radius: 14px;
  background: var(--bg-card);
  border: 1px solid rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.panel-head h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.panel-head svg {
  color: var(--text-secondary);
}

/* ─── 图表 ─── */
.chart {
  height: 280px;
  padding: 12px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 180px;
  padding: 20px;
  color: var(--text-secondary);
  font-size: 13px;
  text-align: center;
  line-height: 1.6;
}

.empty-state.compact {
  min-height: 140px;
}

/* ─── 提问热点 ─── */
.hot-list {
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hot-list div {
  display: grid;
  grid-template-columns: 1fr auto 32px;
  gap: 10px;
  align-items: center;
}

.hot-keyword {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.hot-count {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent-primary);
  text-align: right;
}

/* ─── 来源占比 ─── */
.coverage-list {
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.coverage-list div {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.coverage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.coverage-header span:first-child {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.coverage-chunks {
  font-size: 11px;
  color: var(--text-secondary);
}

/* ─── 干预建议 ─── */
.intervention-list {
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.intervention-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.015);
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.intervention-level {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--accent-warning, #FFD166);
}

.intervention-item.critical .intervention-level {
  color: var(--accent-danger, #FF8B8B);
}

.intervention-item strong {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.intervention-item p {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* ─── 最近动态 ─── */
.interaction-list {
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 360px;
  overflow-y: auto;
}

.interaction-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.015);
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.interaction-kind {
  padding: 3px 8px;
  border-radius: 6px;
  background: var(--accent-primary);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  white-space: nowrap;
}

.interaction-content strong {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.interaction-content p {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.interaction-content small {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  color: var(--text-secondary);
}

.interaction-score {
  font-size: 18px;
  font-weight: 700;
  color: var(--accent-primary);
}

/* ─── 响应式 ─── */
@media (max-width: 1100px) {
  .dashboard-grid {
    grid-template-columns: repeat(6, 1fr);
  }
  .col-8 { grid-column: span 6; }
  .col-4 { grid-column: span 3; }
  .col-6 { grid-column: span 6; }
}

@media (max-width: 760px) {
  .teacher-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .metric-row {
    grid-template-columns: 1fr 1fr;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .col-4, .col-6, .col-8 {
    grid-column: span 1;
  }
}
</style>
