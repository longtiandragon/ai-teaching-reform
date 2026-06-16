<template>
  <div class="login-scene">
    <!-- 噪点纹理叠加层 -->
    <div class="grain-overlay" aria-hidden="true"></div>

    <!-- 背景装饰光晕 -->
    <div class="bg-glow glow-1" aria-hidden="true"></div>
    <div class="bg-glow glow-2" aria-hidden="true"></div>

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
            <div class="feature-icon-wrap">
              <span class="feature-icon">{{ f.icon }}</span>
            </div>
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
      <div class="deco-dots" aria-hidden="true">
        <span v-for="n in 12" :key="n"></span>
      </div>
    </section>

    <!-- 右侧：登录表单 -->
    <section class="form-panel">
      <div class="form-wrapper">
        <!-- 琉璃新拟态登录卡片 -->
        <div class="login-card">
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

          <!-- 账号输入 -->
          <div class="form-field">
            <label>账号</label>
            <div class="input-glass">
              <input
                v-model.trim="account"
                class="glass-input"
                autocomplete="username"
                placeholder="学生填学号，教师填工号"
              />
            </div>
          </div>

          <!-- 密码输入 -->
          <div class="form-field">
            <label>密码</label>
            <div class="input-glass">
              <input
                v-model="password"
                class="glass-input"
                type="password"
                autocomplete="current-password"
                placeholder="默认演示密码 123456"
                @keydown.enter.prevent="handleLogin"
              />
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

const filteredClasses = computed(() => session.classes)
const filteredUsers = computed(() => {
  let users = session.users.filter((u) => u.role === selectedRole.value)
  if (selectedClassId.value) users = users.filter((u) => u.class_id === selectedClassId.value)
  return users
})

onMounted(async () => {
  if (!session.users.length) await session.load()
  if (session.classes.length && !selectedClassId.value) selectedClassId.value = session.classes[0].id
  if (filteredUsers.value.length && !selectedUserId.value) selectedUserId.value = filteredUsers.value[0].id
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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@400;500;600;700;800&display=swap');

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

/* ─── 噪点 ─── */
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

/* ─── 背景光晕 ─── */
.bg-glow {
  position: fixed;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  z-index: 0;
}

.glow-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  left: 20%;
  background: radial-gradient(circle, rgba(217, 119, 6, 0.08), transparent 70%);
  animation: glowFloat 12s ease-in-out infinite;
}

.glow-2 {
  width: 300px;
  height: 300px;
  bottom: -50px;
  right: 10%;
  background: radial-gradient(circle, rgba(196, 149, 106, 0.06), transparent 70%);
  animation: glowFloat 15s ease-in-out infinite reverse;
}

@keyframes glowFloat {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -15px); }
}

/* ─── 品牌区 ─── */
.brand-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 72px;
  position: relative;
  overflow: hidden;
  z-index: 1;
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
  background: rgba(0, 0, 0, 0.03);
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
  font-family: 'Playfair Display', serif;
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

.feature-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  /* 琉璃新拟态 */
  background: rgba(196, 149, 106, 0.1);
  box-shadow:
    inset 1px 1px 2px rgba(255, 255, 255, 0.6),
    inset -1px -1px 2px rgba(0, 0, 0, 0.03),
    2px 2px 6px rgba(0, 0, 0, 0.04);
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

.deco-dots {
  position: absolute;
  bottom: 60px;
  right: 40px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  opacity: 0;
  animation: fadeUp 0.8s cubic-bezier(0.32, 0.72, 0, 1) 1.2s forwards;
}

.deco-dots span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: rgba(196, 149, 106, 0.2);
}

/* ─── 表单区 ─── */
.form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 64px;
  background: #F8F5F0;
  position: relative;
  z-index: 1;
}

.form-wrapper {
  width: 100%;
  max-width: 400px;
  opacity: 0;
  transform: translateY(16px);
  animation: fadeUp 0.9s cubic-bezier(0.32, 0.72, 0, 1) 0.4s forwards;
}

/* ─── 琉璃新拟态卡片 ─── */
.login-card {
  padding: 36px 32px;
  border-radius: 24px;
  /* 外层光晕 */
  background: rgba(255, 255, 255, 0.6);
  /* 琉璃新拟态：内凹高光 + 外凸阴影 + 边框 */
  box-shadow:
    inset 2px 2px 4px rgba(255, 255, 255, 0.8),
    inset -2px -2px 4px rgba(0, 0, 0, 0.02),
    8px 8px 24px rgba(0, 0, 0, 0.06),
    -4px -4px 12px rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.card-header {
  margin-bottom: 28px;
}

.card-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  /* 琉璃新拟态 logo */
  background: #1A1612;
  color: #FDFBF7;
  box-shadow:
    inset 1px 1px 2px rgba(255, 255, 255, 0.1),
    3px 3px 8px rgba(0, 0, 0, 0.15);
  margin-bottom: 20px;
}

.card-header h2 {
  margin: 0 0 6px;
  font-family: 'Playfair Display', serif;
  font-size: 22px;
  font-weight: 700;
  color: #1A1612;
  letter-spacing: -0.01em;
}

.card-header p {
  margin: 0;
  font-size: 14px;
  color: #9B8E82;
}

/* ─── 琉璃新拟态角色选择 ─── */
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
  border: none;
  border-radius: 14px;
  /* 琉璃新拟态：默认状态 */
  background: rgba(255, 255, 255, 0.4);
  box-shadow:
    inset 1px 1px 2px rgba(255, 255, 255, 0.7),
    inset -1px -1px 2px rgba(0, 0, 0, 0.03),
    3px 3px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
  position: relative;
}

.role-btn:hover {
  transform: translateY(-1px);
  box-shadow:
    inset 1px 1px 2px rgba(255, 255, 255, 0.8),
    inset -1px -1px 2px rgba(0, 0, 0, 0.02),
    4px 4px 12px rgba(0, 0, 0, 0.06);
}

/* 按下时内凹 */
.role-btn:active {
  transform: translateY(0);
  box-shadow:
    inset 2px 2px 4px rgba(0, 0, 0, 0.06),
    inset -1px -1px 2px rgba(255, 255, 255, 0.5);
}

.role-btn.active {
  /* 选中态：内凹 + 琥珀金边框 */
  background: rgba(217, 119, 6, 0.04);
  border-color: rgba(217, 119, 6, 0.3);
  box-shadow:
    inset 2px 2px 4px rgba(0, 0, 0, 0.04),
    inset -1px -1px 2px rgba(255, 255, 255, 0.5),
    2px 2px 6px rgba(217, 119, 6, 0.08);
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

/* ─── 琉璃新拟态输入框 ─── */
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

.input-glass {
  border-radius: 14px;
  /* 琉璃新拟态：内凹输入框 */
  background: rgba(255, 255, 255, 0.3);
  box-shadow:
    inset 2px 2px 4px rgba(0, 0, 0, 0.04),
    inset -1px -1px 2px rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.4);
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.input-glass:focus-within {
  border-color: rgba(217, 119, 6, 0.3);
  box-shadow:
    inset 2px 2px 4px rgba(0, 0, 0, 0.03),
    inset -1px -1px 2px rgba(255, 255, 255, 0.5),
    0 0 0 3px rgba(217, 119, 6, 0.06);
}

.glass-input {
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-family: inherit;
  color: #1A1612;
  outline: none;
}

.glass-input::placeholder {
  color: #B5A99A;
}

/* ─── 琉璃新拟态提交按钮 ─── */
.submit-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 14px 8px 14px 24px;
  margin-top: 8px;
  border: none;
  border-radius: 100px;
  /* 琉璃新拟态：外凸深色按钮 */
  background: #1A1612;
  color: #FDFBF7;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
  box-shadow:
    inset 1px 1px 2px rgba(255, 255, 255, 0.08),
    4px 4px 12px rgba(0, 0, 0, 0.15);
}

.submit-btn:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow:
    inset 1px 1px 2px rgba(255, 255, 255, 0.1),
    6px 6px 18px rgba(0, 0, 0, 0.18);
}

.submit-btn:not(:disabled):active {
  transform: scale(0.98);
  box-shadow:
    inset 2px 2px 4px rgba(0, 0, 0, 0.2),
    1px 1px 4px rgba(0, 0, 0, 0.1);
}

.submit-btn:disabled {
  opacity: 0.35;
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
  /* 琉璃新拟态：内嵌圆形图标区 */
  background: rgba(255, 251, 247, 0.1);
  box-shadow:
    inset 1px 1px 2px rgba(255, 255, 255, 0.06),
    inset -1px -1px 2px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.submit-btn:not(:disabled):hover .btn-trailing {
  transform: translate(2px, -1px);
}

.form-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 12px;
  color: #B5A99A;
}

/* ─── 动画 ─── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(var(--fade-dist, 12px)); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
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

  .brand-content { max-width: 100%; }
  .brand-headline { font-size: 40px; }
  .brand-features { display: none; }
  .form-panel { padding: 32px 24px 48px; }
  .deco-ring { display: none; }
  .deco-dots { display: none; }
}
</style>
