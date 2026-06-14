<template>
  <Teleport to="body">
    <Transition name="guide-fade">
      <div v-if="visible" class="guide-overlay" @click.self="close">
        <div class="guide-modal">
          <!-- 关闭按钮 -->
          <button class="guide-close" @click="close" title="关闭">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </button>

          <!-- 头部 -->
          <div class="guide-header">
            <h2>{{ isTeacher ? '教师端功能指南' : '学生端功能指南' }}</h2>
            <p>{{ isTeacher ? '以下是平台各功能模块的使用说明，帮助您快速上手。' : '以下是平台各功能的使用说明，帮助你更好地学习。' }}</p>
          </div>

          <!-- 功能列表 -->
          <div class="guide-body">
            <div
              v-for="(item, i) in features"
              :key="i"
              class="guide-item"
              :style="{ animationDelay: (0.1 + i * 0.08) + 's' }"
            >
              <div class="item-icon" :style="{ background: item.color }">
                <span>{{ item.icon }}</span>
              </div>
              <div class="item-content">
                <h3>{{ item.title }}</h3>
                <p>{{ item.desc }}</p>
              </div>
            </div>
          </div>

          <!-- 底部 -->
          <div class="guide-footer">
            <label class="guide-checkbox">
              <input type="checkbox" v-model="dontShow" />
              <span>下次不再显示</span>
            </label>
            <button class="guide-btn" @click="close">
              {{ isTeacher ? '开始管理' : '开始学习' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '../stores/session'

const session = useSessionStore()
const isTeacher = computed(() => session.currentUser?.role === 'teacher')
const visible = ref(false)
const dontShow = ref(false)

const STORAGE_KEY = 'feature-guide-dismissed'

const studentFeatures = [
  { icon: '🗺', title: '学习路线', desc: '选择课程轨道，查看每个关卡的学习目标和任务说明。已完成、进行中、未解锁的状态一目了然。', color: 'rgba(217,119,6,0.12)' },
  { icon: '💬', title: 'AI 助教对话', desc: '在任务工作台中，你可以向 AI 助教提问。AI 会基于课程知识库回答，并附带引用来源。支持提示、反思等功能。', color: 'rgba(125,211,168,0.12)' },
  { icon: '✅', title: '提交验收', desc: '完成任务后，点击「提交验收」。系统会用 Rubric 规则（60%）+ AI 评分（40%）进行综合评判，通过后自动解锁下一关。', color: 'rgba(196,161,255,0.12)' },
  { icon: '📝', title: '自检答题', desc: '每关配有选择题、判断题、简答题和编码题。做完后系统自动批改并记录成绩。', color: 'rgba(255,139,139,0.12)' },
  { icon: '📊', title: '学习记录', desc: '查看你的所有学习历史：聊天记录、练习成绩、提交反馈、教师评价。', color: 'rgba(255,209,102,0.12)' },
  { icon: '⚙️', title: 'AI 配置', desc: '配置 DeepSeek API Key 后即可使用 AI 助教的所有功能。支持连接测试和预置模型选择。', color: 'rgba(120,113,108,0.12)' },
]

const teacherFeatures = [
  { icon: '📊', title: '仪表盘', desc: '查看班级概览：学生人数、完成率、平均分。包含章节分布图、薄弱点雷达、提问热点等数据可视化。', color: 'rgba(255,157,118,0.12)' },
  { icon: '📚', title: '知识库管理', desc: '上传课程资料（PDF、Word、Excel、代码文件等）到知识库，AI 会自动解析并索引。支持题库管理，可发布题目到指定关卡。', color: 'rgba(125,211,168,0.12)' },
  { icon: '👥', title: '学生管理', desc: '查看学生学习进度表，点击「AI 分析」可自动分析每个学生的优势、不足和改进建议。支持班级整体分析。', color: 'rgba(196,161,255,0.12)' },
  { icon: '💌', title: '反馈中心', desc: '向学生发送学习反馈。可以手动撰写，也可以将 AI 分析结果直接发送给学生。学生在「学习记录」中查看。', color: 'rgba(255,209,102,0.12)' },
  { icon: '⚙️', title: 'AI 配置', desc: '配置 DeepSeek API Key、查看系统状态（RAG 知识库、数据库连接等）。', color: 'rgba(120,113,108,0.12)' },
  { icon: '🚀', title: '发布习题', desc: '在题库管理中，将题目发布到指定关卡。学生在关卡路线中看到已发布的题目，点击开始答题。', color: 'rgba(255,139,139,0.12)' },
]

const features = computed(() => isTeacher.value ? teacherFeatures : studentFeatures)

onMounted(() => {
  const dismissed = localStorage.getItem(STORAGE_KEY)
  if (!dismissed) {
    setTimeout(() => { visible.value = true }, 600)
  }
})

function close() {
  if (dontShow.value) {
    localStorage.setItem(STORAGE_KEY, 'true')
  }
  visible.value = false
}
</script>

<style scoped>
.guide-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  padding: 24px;
}

.guide-modal {
  position: relative;
  width: 100%;
  max-width: 640px;
  max-height: 85vh;
  background: #FFFDFB;
  border-radius: 20px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.guide-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.04);
  color: #78716C;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 1;
}

.guide-close:hover {
  background: rgba(0, 0, 0, 0.08);
  color: #1A1A1A;
}

.guide-header {
  padding: 32px 32px 20px;
}

.guide-header h2 {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 700;
  color: #1A1A1A;
}

.guide-header p {
  margin: 0;
  font-size: 14px;
  color: #78716C;
  line-height: 1.6;
}

.guide-body {
  padding: 0 32px;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.guide-item {
  display: flex;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.015);
  border: 1px solid rgba(0, 0, 0, 0.04);
  opacity: 0;
  transform: translateY(10px);
  animation: guideSlideUp 0.5s cubic-bezier(0.32, 0.72, 0, 1) forwards;
}

.item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  flex-shrink: 0;
  font-size: 18px;
}

.item-content h3 {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 600;
  color: #1A1A1A;
}

.item-content p {
  margin: 0;
  font-size: 13px;
  color: #78716C;
  line-height: 1.6;
}

.guide-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px 24px;
  margin-top: 12px;
}

.guide-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #78716C;
  cursor: pointer;
}

.guide-checkbox input {
  width: 16px;
  height: 16px;
  accent-color: #D97706;
}

.guide-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 100px;
  background: #D97706;
  color: #FFFBEB;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.guide-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(217, 119, 6, 0.25);
}

/* 动画 */
.guide-fade-enter-active {
  transition: opacity 0.4s cubic-bezier(0.32, 0.72, 0, 1);
}

.guide-fade-leave-active {
  transition: opacity 0.25s ease-in;
}

.guide-fade-enter-from,
.guide-fade-leave-to {
  opacity: 0;
}

.guide-fade-enter-from .guide-modal {
  transform: scale(0.95) translateY(10px);
}

.guide-fade-enter-active .guide-modal {
  transition: transform 0.4s cubic-bezier(0.32, 0.72, 0, 1);
}

@keyframes guideSlideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 640px) {
  .guide-modal {
    max-height: 90vh;
    border-radius: 16px;
  }

  .guide-header,
  .guide-body,
  .guide-footer {
    padding-left: 20px;
    padding-right: 20px;
  }
}
</style>
