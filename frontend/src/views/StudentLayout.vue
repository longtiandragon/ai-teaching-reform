<template>
  <div class="student-layout" data-theme="student">
    <ScanlineOverlay />
    <BorderLightFlow ref="lightFlow" />
    <FeatureGuide />

    <!-- 浮沫胶囊导航栏 -->
    <header class="nav-capsule" :class="{ scrolled: isScrolled }">
      <div class="capsule-inner">
        <div class="nav-left">
          <div class="logo-mark">
            <Cpu :size="18" />
          </div>
          <span class="logo-text">AI 实训</span>
        </div>

        <nav class="nav-center">
          <RouterLink
            to="/student"
            class="nav-pill"
            @click="triggerFlow"
          >
            <Map :size="14" />
            <span>学习路线</span>
          </RouterLink>
          <RouterLink
            to="/student/records"
            class="nav-pill"
            @click="triggerFlow"
          >
            <ClipboardList :size="14" />
            <span>学习记录</span>
          </RouterLink>
          <RouterLink
            to="/student/error-book"
            class="nav-pill"
            @click="triggerFlow"
          >
            <BookOpen :size="14" />
            <span>错题本</span>
          </RouterLink>
          <RouterLink
            v-if="false"
            to="/student/ai-config"
            class="nav-pill"
            @click="triggerFlow"
          >
            <Settings :size="14" />
            <span>AI 配置</span>
          </RouterLink>
        </nav>

        <div class="nav-right">
          <div class="user-chip">
            <span class="user-avatar">{{ (session.currentUser?.name || '?')[0] }}</span>
            <span class="user-name">{{ session.currentUser?.name }}</span>
          </div>
          <button type="button" class="logout-pill" @click="handleLogout" title="退出登录">
            <LogOut :size="14" />
          </button>
        </div>
      </div>
    </header>

    <main class="student-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Cpu, Map, ClipboardList, BookOpen, Settings, LogOut } from 'lucide-vue-next'
import { useSessionStore } from '../stores/session'
import ScanlineOverlay from '../components/ScanlineOverlay.vue'
import BorderLightFlow from '../components/BorderLightFlow.vue'
import FeatureGuide from './FeatureGuide.vue'

const router = useRouter()
const session = useSessionStore()
const lightFlow = ref<InstanceType<typeof BorderLightFlow> | null>(null)
const isScrolled = ref(false)

function triggerFlow() {
  lightFlow.value?.trigger()
}

function handleLogout() {
  session.logout()
  router.push('/login')
}

function onScroll() {
  isScrolled.value = window.scrollY > 12
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.student-layout {
  min-height: 100vh;
  background: var(--bg-primary);
  position: relative;
  padding-top: 72px;
}

/* ─── 浮沫胶囊导航栏 ─── */
.nav-capsule {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  width: calc(100% - 48px);
  max-width: 1200px;
  transition: all 0.5s cubic-bezier(0.32, 0.72, 0, 1);
}

.capsule-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 8px 8px 18px;
  border-radius: 20px;
  background: #FFFDF8;
  /* 新拟态：外凸效果 */
  box-shadow:
    6px 6px 14px rgba(0, 0, 0, 0.06),
    -4px -4px 10px rgba(255, 255, 255, 0.9),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  transition: all 0.5s cubic-bezier(0.32, 0.72, 0, 1);
}

.nav-capsule.scrolled .capsule-inner {
  box-shadow:
    4px 4px 10px rgba(0, 0, 0, 0.08),
    -3px -3px 8px rgba(255, 255, 255, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
  background: rgba(255, 253, 248, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

/* ─── Logo ─── */
.nav-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.logo-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: #0F172A;
  color: #FFFBEB;
  /* 新拟态：内凹 */
  box-shadow:
    inset 2px 2px 4px rgba(0, 0, 0, 0.15),
    inset -1px -1px 2px rgba(255, 255, 255, 0.1);
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.logo-mark:hover {
  transform: scale(1.05);
}

.logo-text {
  font-family: 'Playfair Display', serif;
  font-size: 15px;
  font-weight: 700;
  color: #0F172A;
  letter-spacing: -0.01em;
}

/* ─── 导航链接 ─── */
.nav-center {
  display: flex;
  gap: 4px;
}

.nav-pill {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 14px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  color: #78716C;
  text-decoration: none;
  transition: all 0.35s cubic-bezier(0.32, 0.72, 0, 1);
  position: relative;
}

.nav-pill:hover {
  color: #0F172A;
  /* 新拟态：内凹 hover */
  box-shadow:
    inset 2px 2px 5px rgba(0, 0, 0, 0.06),
    inset -2px -2px 4px rgba(255, 255, 255, 0.7);
}

.nav-pill.router-link-exact-active {
  color: #FFFBEB;
  background: #D97706;
  /* 新拟态：激活态外凸 */
  box-shadow:
    3px 3px 8px rgba(217, 119, 6, 0.2),
    -2px -2px 6px rgba(255, 255, 255, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

/* ─── 用户信息 ─── */
.nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 5px 12px 5px 5px;
  border-radius: 12px;
  /* 新拟态：内凹 */
  box-shadow:
    inset 2px 2px 5px rgba(0, 0, 0, 0.04),
    inset -2px -2px 4px rgba(255, 255, 255, 0.6);
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: #D97706;
  color: #FFFBEB;
  font-size: 12px;
  font-weight: 700;
}

.user-name {
  font-size: 12px;
  font-weight: 600;
  color: #0F172A;
}

.logout-pill {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #A8A29E;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.logout-pill:hover {
  color: #DC2626;
  /* 新拟态：内凹 */
  box-shadow:
    inset 2px 2px 5px rgba(0, 0, 0, 0.06),
    inset -2px -2px 4px rgba(255, 255, 255, 0.6);
}

/* ─── 内容区 ─── */
.student-content {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* ─── 响应式 ─── */
@media (max-width: 768px) {
  .nav-capsule {
    width: calc(100% - 24px);
    top: 10px;
  }

  .capsule-inner {
    padding: 6px 6px 6px 12px;
    border-radius: 16px;
  }

  .logo-text {
    display: none;
  }

  .nav-pill span {
    display: none;
  }

  .nav-pill {
    padding: 8px 10px;
  }

  .user-name {
    display: none;
  }

  .student-layout {
    padding-top: 64px;
  }
}
</style>
