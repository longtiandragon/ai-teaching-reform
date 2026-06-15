<template>
  <div class="login-scene">
    <!-- 噪点纹理叠加层 -->
    <div class="grain-overlay" aria-hidden="true"></div>

    <!-- 左侧：品牌区 -->
    <section class="brand-panel">
      <div class="brand-content">
        <div class="brand-badge">
          <span class="badge-dot"></span>
          <span>AI Teaching Platform</span>
        </div>

        <h1 class="brand-headline">
          <span class="line line-1">智能实训</span>
          <span class="line line-2">引导学习</span>
        </h1>

        <p class="brand-sub">
          不是直接给答案，而是引导你思考。<br />
          在 AI 的逐步引导下，真正理解并掌握知识。
        </p>

        <div class="brand-features">
          <div class="feature-item" v-for="(f, i) in features" :key="i">
            <span class="feature-icon">{{ f.icon }}</span>
            <div>
              <strong>{{ f.title }}</strong>
              <p>{{ f.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 装饰性几何元素 -->
      <div class="deco-ring deco-ring-1" aria-hidden="true"></div>
      <div class="deco-ring deco-ring-2" aria-hidden="true"></div>
    </section>

    <!-- 右侧：登录表单 -->
    <section class="form-panel">
      <div class="form-wrapper">
        <!-- Double-Bezel 登录卡片 -->
        <div class="login-card-outer">
          <div class="login-card-inner">
            <div class="card-header">
              <div class="card-logo">
                <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                  <rect x="2" y="2" width="24" height="24" rx="7" stroke="currentColor" stroke-width="1.5" />
                  <path d="M9 14h10M14 9v10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                </svg>
              </div>
              <h2>进入系统</h2>
              <p>选择身份和账号开始学习</p>
            </div>

            <!-- 角色选择 -->
            <div class="role-selector">
              <button
                v-for="role in roles"
                :key="role.value"
                type="button"
                :class="['role-btn', { active: selectedRole === role.value }]"
                @click="selectedRole = role.value as 'student' | 'teacher'"
              >
                <span class="role-icon">{{ role.icon }}</span>
                <span class="role-label">{{ role.label }}</span>
                <span class="role-check" v-if="selectedRole === role.value">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M3 7l3 3 5-6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
              </button>
            </div>

            <!-- 班级选择 -->
            <div class="form-field">
              <label>班级</label>
              <div class="select-wrapper">
                <input v-model.trim="account" class="login-input" autocomplete="username" placeholder="学生填学号，教师填账号/教师号" />
                <select v-if="false" v-model="selectedClassId" :disabled="!filteredClasses.length">
                  <option value="" disabled>选择班级</option>
                  <option v-for="cls in filteredClasses" :key="cls.id" :value="cls.id">
                    {{ cls.name }}
                  </option>
                </select>
                <svg class="select-arrow" width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M3.5 5.5l3.5 3 3.5-3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>
            </div>

            <!-- 用户选择 -->
            <div class="form-field">
              <label>用户</label>
              <div class="select-wrapper">
                <input v-model="password" class="login-input" type="password" autocomplete="current-password" placeholder="默认演示密码 123456" @keydown.enter.prevent="handleLogin" />
                <select v-if="false" v-model="selectedUserId" :disabled="!filteredUsers.length">
                  <option value="" disabled>选择用户</option>
                  <option v-for="user in filteredUsers" :key="user.id" :value="user.id">
                    {{ user.student_no ? `${user.student_no} · ` : '' }}{{ user.name }}
                  </option>
                </select>
                <svg class="select-arrow" width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M3.5 5.5l3.5 3 3.5-3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>
            </div>

            <!-- 提交按钮 -->
            <button
              type="button"
              class="submit-btn"
              :disabled="!account || !password || loading"
              @click="handleLogin"
            >
              <span class="btn-text">{{ loading ? '进入中...' : '进入学习' }}</span>
              <span class="btn-trailing">
                <svg v-if="loading" width="16" height="16" viewBox="0 0 16 16" class="spin">
                  <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5" fill="none" stroke-dasharray="28" stroke-dashoffset="8" stroke-linecap="round" />
                </svg>
                <svg v-else width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </span>
            </button>
          </div>
        </div>

        <p class="form-footer">
          AI 教学改革实训平台 · 面向软件工程课程
        </p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'

const router = useRouter()
const session = useSessionStore()

const selectedRole = ref<'student' | 'teacher'>('student')
const selectedClassId = ref('')
const selectedUserId = ref('')
const account = ref('')
const password = ref('')
const loading = ref(false)

// 切换角色或班级时，重置用户选择
watch([selectedRole, selectedClassId], () => {
  selectedUserId.value = filteredUsers.value[0]?.id || ''
})

const roles = [
  { value: 'student', label: '学生', icon: '📖' },
  { value: 'teacher', label: '教师', icon: '🎓' },
]

const features = [
  { icon: '→', title: '智能引导', desc: 'AI 按步骤引导，不直接给答案' },
  { icon: '◆', title: '知识库增强', desc: '回答基于课程资料和项目文档' },
  { icon: '○', title: '过程评价', desc: '规则+AI 双轨评分，客观准确' },
]

const filteredClasses = computed(() => {
  return session.classes
})

const filteredUsers = computed(() => {
  let users = session.users.filter((u) => u.role === selectedRole.value)
  if (selectedClassId.value) {
    users = users.filter((u) => u.class_id === selectedClassId.value)
  }
  return users
})

onMounted(async () => {
  // 如果 App.vue 还没加载完数据，等一下
  if (!session.users.length) {
    await session.load()
  }
  if (session.classes.length && !selectedClassId.value) {
    selectedClassId.value = session.classes[0].id
  }
  if (filteredUsers.value.length && !selectedUserId.value) {
    selectedUserId.value = filteredUsers.value[0].id
  }
})

async function handleLogin() {
  if (!account.value || !password.value) return
  loading.value = true
  try {
    await session.login(account.value, password.value)
    const target = session.currentUser?.role === 'teacher' ? '/teacher' : '/student'
    router.push(target)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ─── 字体 ─── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ─── 场景 ─── */
.login-scene {
  min-height: 100dvh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: #FDFBF7;
  font-family: 'Plus Jakarta Sans', 'Noto Sans SC', sans-serif;
  position: relative;
  overflow: hidden;
}

/* ─── 噪点纹理 ─── */
.grain-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  pointer-events: none;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 256px 256px;
}

/* ─── 左侧品牌区 ─── */
.brand-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 72px;
  position: relative;
  overflow: hidden;
}

.brand-content {
  position: relative;
  z-index: 2;
  max-width: 480px;
}

.brand-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px 6px 10px;
  border-radius: 100px;
  background: rgba(0, 0, 0, 0.04);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #8B7355;
  margin-bottom: 40px;
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.8s cubic-bezier(0.32, 0.72, 0, 1) 0.2s forwards;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #C4956A;
}

.brand-headline {
  margin: 0 0 28px;
  font-size: clamp(48px, 6vw, 72px);
  font-weight: 800;
  line-height: 1.05;
  color: #1A1612;
  letter-spacing: -0.03em;
}

.brand-headline .line {
  display: block;
  opacity: 0;
  transform: translateY(20px);
}

.brand-headline .line-1 {
  animation: fadeUp 0.9s cubic-bezier(0.32, 0.72, 0, 1) 0.35s forwards;
}

.brand-headline .line-2 {
  color: #C4956A;
  animation: fadeUp 0.9s cubic-bezier(0.32, 0.72, 0, 1) 0.5s forwards;
}

.brand-sub {
  margin: 0 0 48px;
  font-size: 16px;
  line-height: 1.7;
  color: #7A6E62;
  max-width: 400px;
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.8s cubic-bezier(0.32, 0.72, 0, 1) 0.65s forwards;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  opacity: 0;
  transform: translateY(12px);
}

.feature-item:nth-child(1) { animation: fadeUp 0.8s cubic-bezier(0.32, 0.72, 0, 1) 0.8s forwards; }
.feature-item:nth-child(2) { animation: fadeUp 0.8s cubic-bezier(0.32, 0.72, 0, 1) 0.9s forwards; }
.feature-item:nth-child(3) { animation: fadeUp 0.8s cubic-bezier(0.32, 0.72, 0, 1) 1.0s forwards; }

.feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(196, 149, 106, 0.12);
  color: #C4956A;
  font-size: 14px;
  flex-shrink: 0;
}

.feature-item strong {
  display: block;
  font-size: 14px;
  font-weight: 700;
  color: #1A1612;
  margin-bottom: 2px;
}

.feature-item p {
  margin: 0;
  font-size: 13px;
  color: #9B8E82;
  line-height: 1.5;
}

/* ─── 装饰环 ─── */
.deco-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(196, 149, 106, 0.12);
}

.deco-ring-1 {
  width: 400px;
  height: 400px;
  right: -120px;
  top: -80px;
  opacity: 0;
  animation: scaleIn 1.2s cubic-bezier(0.32, 0.72, 0, 1) 0.4s forwards;
}

.deco-ring-2 {
  width: 260px;
  height: 260px;
  left: -60px;
  bottom: -40px;
  opacity: 0;
  animation: scaleIn 1.2s cubic-bezier(0.32, 0.72, 0, 1) 0.6s forwards;
}

/* ─── 右侧表单区 ─── */
.form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 64px;
  background: #F8F5F0;
  position: relative;
}

.form-wrapper {
  width: 100%;
  max-width: 400px;
  opacity: 0;
  transform: translateY(16px);
  animation: fadeUp 0.9s cubic-bezier(0.32, 0.72, 0, 1) 0.4s forwards;
}

/* ─── Double-Bezel 登录卡片 ─── */
.login-card-outer {
  padding: 6px;
  border-radius: 24px;
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.login-card-inner {
  background: #FFFCF8;
  border-radius: 19px;
  padding: 40px 36px 36px;
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.8);
}

.card-header {
  margin-bottom: 32px;
}

.card-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: #1A1612;
  color: #FDFBF7;
  margin-bottom: 20px;
}

.card-header h2 {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 800;
  color: #1A1612;
  letter-spacing: -0.02em;
}

.card-header p {
  margin: 0;
  font-size: 14px;
  color: #9B8E82;
}

/* ─── 角色选择 ─── */
.role-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 24px;
}

.role-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 14px;
  background: transparent;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
  position: relative;
}

.role-btn:hover {
  border-color: rgba(196, 149, 106, 0.3);
  transform: translateY(-1px);
}

.role-btn.active {
  border-color: #C4956A;
  background: rgba(196, 149, 106, 0.06);
}

.role-icon {
  font-size: 18px;
}

.role-label {
  font-size: 14px;
  font-weight: 600;
  color: #1A1612;
}

.role-check {
  position: absolute;
  top: 8px;
  right: 8px;
  color: #C4956A;
}

/* ─── 表单字段 ─── */
.form-field {
  margin-bottom: 18px;
}

.form-field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #7A6E62;
  margin-bottom: 8px;
  letter-spacing: 0.02em;
}

.select-wrapper {
  position: relative;
}

.select-wrapper select {
  width: 100%;
  padding: 12px 36px 12px 16px;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  background: #FFFCF8;
  color: #1A1612;
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: border-color 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.select-wrapper select:focus {
  border-color: #C4956A;
}

.login-input {
  width: 100%;
  padding: 12px 16px;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  background: #FFFCF8;
  color: #1A1612;
  outline: none;
  box-sizing: border-box;
}

.login-input:focus {
  border-color: #C4956A;
}

.select-arrow {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #9B8E82;
  pointer-events: none;
}

/* ─── 提交按钮 ─── */
.submit-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 14px 8px 14px 24px;
  margin-top: 8px;
  border: none;
  border-radius: 100px;
  background: #1A1612;
  color: #FDFBF7;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
}

.submit-btn:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(26, 22, 18, 0.2);
}

.submit-btn:not(:disabled):active {
  transform: scale(0.98);
}

.submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-text {
  font-size: 15px;
  font-weight: 600;
  font-family: inherit;
}

.btn-trailing {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(253, 251, 247, 0.15);
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.submit-btn:not(:disabled):hover .btn-trailing {
  transform: translate(2px, -1px) scale(1.05);
}

.form-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 12px;
  color: #B5A99A;
}

/* ─── 动画 ─── */
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(var(--fade-dist, 12px));
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ─── 响应式 ─── */
@media (max-width: 900px) {
  .login-scene {
    grid-template-columns: 1fr;
  }

  .brand-panel {
    padding: 48px 32px 32px;
    min-height: auto;
  }

  .brand-content {
    max-width: 100%;
  }

  .brand-headline {
    font-size: 40px;
  }

  .brand-features {
    display: none;
  }

  .form-panel {
    padding: 32px 24px 48px;
  }

  .deco-ring {
    display: none;
  }
}
</style>
