<template>
  <main class="records-page">
    <section class="records-hero panel">
      <div>
        <p class="eyebrow">My Learning Records</p>
        <h2>{{ session.currentUser?.name || '学生' }}的学习记录</h2>
        <p>{{ session.currentUser?.class_name || '未分班' }} · 查看你的关卡进度、自检结果和提交反馈。</p>
      </div>
      <button type="button" class="refresh-btn" @click="loadRecords">刷新记录</button>
    </section>

    <section class="record-metrics">
      <article class="panel">
        <span>完成关卡</span>
        <strong>{{ completedLessons.size }}</strong>
      </article>
      <article class="panel">
        <span>记录次数</span>
        <strong>{{ records.length }}</strong>
      </article>
      <article class="panel">
        <span>平均得分</span>
        <strong>{{ averageScore || '--' }}</strong>
      </article>
    </section>

    <section class="panel record-list-panel">
      <div class="panel-title">
        <div>
          <p class="eyebrow">Timeline</p>
          <h3>最近提交</h3>
        </div>
      </div>

      <div v-if="loading" class="empty-state">正在读取学习记录...</div>
      <div v-else-if="!records.length" class="empty-state">还没有学习记录。完成一次自检或提交检查后，这里会显示结果。</div>
      <article v-for="record in records" v-else :key="record.id" class="record-item">
        <div class="record-kind" :class="record.kind">{{ record.kind === 'self_check' ? '自检' : '提交' }}</div>
        <div>
          <h4>{{ lessonLabel(record.lesson_id) }}</h4>
          <p>{{ record.kind === 'self_check' ? `${record.correct}/${record.total} 题正确` : shortText(record.feedback || record.notes || '') }}</p>
          <small>{{ formatTime(record.created_at) }}</small>
        </div>
        <strong v-if="record.score !== null && record.score !== undefined">{{ record.score }} 分</strong>
        <RouterLink :to="{ name: 'student-learn', params: { lessonId: record.lesson_id }, query: { course: record.course_id } }">查看关卡</RouterLink>
      </article>
    </section>
  </main>
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

const completedLessons = computed(() => new Set(records.value.map((record) => record.lesson_id)))
const averageScore = computed(() => {
  const scores = records.value.map((record) => record.score).filter((score): score is number => typeof score === 'number')
  return scores.length ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : 0
})

onMounted(async () => {
  if (!session.currentUser) await session.load()
  await store.load()
  await loadRecords()
})

watch(() => session.currentUser?.id, () => loadRecords())

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

function lessonLabel(lessonId: string) {
  for (const course of store.courses) {
    const lesson = course.lessons.find((item) => item.id === lessonId)
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
.records-page {
  display: grid;
  gap: 14px;
  min-height: calc(100vh - 82px);
  padding: 18px;
  background: #edf3f8;
}

.records-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 22px;
}

.records-hero h2 {
  margin: 0;
  color: #17243a;
  font-size: 24px;
}

.records-hero p:last-child {
  margin: 8px 0 0;
  color: #5d6f87;
}

.refresh-btn {
  border: 1px solid #2d7be8;
  border-radius: 7px;
  background: #2d7be8;
  color: #fff;
  padding: 10px 14px;
  font-weight: 900;
  cursor: pointer;
}

.record-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.record-metrics article {
  display: grid;
  gap: 6px;
  padding: 16px;
}

.record-metrics span {
  color: #637188;
  font-size: 13px;
  font-weight: 800;
}

.record-metrics strong {
  color: #17243a;
  font-size: 28px;
}

.record-list-panel {
  overflow: hidden;
}

.record-item {
  display: grid;
  grid-template-columns: 54px minmax(0, 1fr) 70px 82px;
  gap: 12px;
  align-items: center;
  padding: 14px 18px;
  border-top: 1px solid #e8eef6;
}

.record-kind {
  display: grid;
  place-items: center;
  height: 34px;
  border-radius: 7px;
  background: #eaf3ff;
  color: #1d5fbf;
  font-size: 12px;
  font-weight: 900;
}

.record-kind.ai_practice {
  background: #fff7df;
  color: #9a5a00;
}

.record-item h4,
.record-item p {
  margin: 0;
}

.record-item h4 {
  color: #1b2a44;
  font-size: 15px;
}

.record-item p,
.record-item small {
  color: #637188;
  font-size: 12px;
}

.record-item a {
  color: #1d5fbf;
  font-size: 13px;
  font-weight: 900;
  text-decoration: none;
}

.empty-state {
  padding: 28px;
  color: #64748b;
}

@media (max-width: 760px) {
  .records-hero,
  .record-item {
    grid-template-columns: 1fr;
  }

  .records-hero {
    align-items: flex-start;
    flex-direction: column;
  }

  .record-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
