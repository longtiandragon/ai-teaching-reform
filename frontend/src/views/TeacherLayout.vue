<template>
  <div class="teacher-layout" data-theme="teacher">
    <FeatureGuide />
    <!-- 浮动工具栏 -->
    <header class="nav-toolbar" :class="{ scrolled: isScrolled }">
      <div class="toolbar-inner">
        <div class="nav-left">
          <div class="logo-mark">
            <Layers :size="16" />
          </div>
          <span class="logo-text">教学管理平台</span>
        </div>

        <nav class="nav-tabs">
          <RouterLink to="/teacher" class="nav-tab">
            <LayoutDashboard :size="14" />
            <span>仪表盘</span>
          </RouterLink>
          <div class="tab-divider"></div>
          <RouterLink to="/teacher/knowledge" class="nav-tab">
            <Database :size="14" />
            <span>知识库</span>
          </RouterLink>
          <div class="tab-divider"></div>
          <RouterLink to="/teacher/students" class="nav-tab">
            <Users :size="14" />
            <span>学生</span>
          </RouterLink>
          <div class="tab-divider"></div>
          <RouterLink to="/teacher/feedback" class="nav-tab">
            <MessageSquare :size="14" />
            <span>反馈</span>
          </RouterLink>
          <div class="tab-divider"></div>
          <RouterLink to="/teacher/ai-config" class="nav-tab">
            <Settings :size="14" />
            <span>配置</span>
          </RouterLink>
        </nav>

        <div class="nav-right">
          <div class="user-info">
            <span class="user-avatar">{{ (session.currentUser?.name || '?')[0] }}</span>
            <span class="user-name">{{ session.currentUser?.name }}</span>
          </div>
          <button type="button" class="logout-btn" @click="handleLogout" title="退出登录">
            <LogOut :size="14" />
          </button>
        </div>
      </div>
    </header>

    <main class="teacher-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Layers, LayoutDashboard, Database, Users, MessageSquare, Settings, LogOut } from 'lucide-vue-next'
import { useSessionStore } from '../stores/session'
import FeatureGuide from './FeatureGuide.vue'

const router = useRouter()
const session = useSessionStore()
const isScrolled = ref(false)

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
.teacher-layout {
  min-height: 100vh;
  background: var(--bg-primary);
  padding-top: 68px;
}

/* ─── 浮动工具栏 ─── */
.nav-toolbar {
  position: fixed;
  top: 12px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  width: calc(100% - 32px);
  max-width: 1200px;
  transition: all 0.5s cubic-bezier(0.32, 0.72, 0, 1);
}

.toolbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 6px 6px 6px 16px;
  border-radius: 16px;
  background: #FFFDFB;
  /* 新拟态：外凸效果 */
  box-shadow:
    5px 5px 12px rgba(0, 0, 0, 0.05),
    -3px -3px 8px rgba(255, 255, 255, 0.8),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  transition: all 0.5s cubic-bezier(0.32, 0.72, 0, 1);
}

.nav-toolbar.scrolled .toolbar-inner {
  box-shadow:
    3px 3px 8px rgba(0, 0, 0, 0.07),
    -2px -2px 6px rgba(255, 255, 255, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  background: rgba(255, 253, 251, 0.9);
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
  width: 30px;
  height: 30px;
  border-radius: 9px;
  background: var(--accent-primary);
  color: #fff;
  /* 新拟态：内凹 */
  box-shadow:
    inset 2px 2px 4px rgba(0, 0, 0, 0.12),
    inset -1px -1px 2px rgba(255, 255, 255, 0.1);
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.logo-mark:hover {
  transform: scale(1.05);
}

.logo-text {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

/* ─── 导航标签 ─── */
.nav-tabs {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px;
  border-radius: 12px;
  /* 新拟态：内凹 */
  box-shadow:
    inset 2px 2px 5px rgba(0, 0, 0, 0.04),
    inset -2px -2px 4px rgba(255, 255, 255, 0.5);
}

.tab-divider {
  width: 1px;
  height: 16px;
  background: rgba(0, 0, 0, 0.06);
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.35s cubic-bezier(0.32, 0.72, 0, 1);
}

.nav-tab:hover {
  color: var(--text-primary);
  /* 新拟态：外凸 hover */
  box-shadow:
    2px 2px 5px rgba(0, 0, 0, 0.04),
    -1px -1px 3px rgba(255, 255, 255, 0.5);
}

.nav-tab.router-link-exact-active {
  color: #fff;
  background: var(--accent-primary);
  font-weight: 600;
  /* 新拟态：激活态外凸 */
  box-shadow:
    3px 3px 7px rgba(255, 157, 118, 0.2),
    -2px -2px 5px rgba(255, 255, 255, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

/* ─── 用户信息 ─── */
.nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 4px 10px 4px 4px;
  border-radius: 10px;
  /* 新拟态：内凹 */
  box-shadow:
    inset 2px 2px 4px rgba(0, 0, 0, 0.03),
    inset -1px -1px 3px rgba(255, 255, 255, 0.5);
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 7px;
  background: var(--accent-secondary);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
}

.user-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 9px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.logout-btn:hover {
  color: var(--accent-danger, #FF8B8B);
  /* 新拟态：内凹 */
  box-shadow:
    inset 2px 2px 4px rgba(0, 0, 0, 0.05),
    inset -1px -1px 3px rgba(255, 255, 255, 0.5);
}

/* ─── 内容区 ─── */
.teacher-content {
  padding: 24px 32px;
  max-width: 1400px;
  margin: 0 auto;
}

/* ─── 响应式 ─── */
@media (max-width: 900px) {
  .nav-toolbar {
    width: calc(100% - 20px);
    top: 8px;
  }

  .toolbar-inner {
    padding: 5px 5px 5px 10px;
    border-radius: 14px;
  }

  .logo-text {
    display: none;
  }

  .nav-tab span {
    display: none;
  }

  .nav-tab {
    padding: 7px 9px;
  }

  .user-name {
    display: none;
  }

  .teacher-layout {
    padding-top: 60px;
  }
}
</style>
