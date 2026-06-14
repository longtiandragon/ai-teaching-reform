import { createRouter, createWebHistory } from 'vue-router'
import { useSessionStore } from './stores/session'

const LoginPage = () => import('./views/LoginPage.vue')

// 学生端
const StudentLayout = () => import('./views/StudentLayout.vue')
const CourseRoadmap = () => import('./views/CourseRoadmap.vue')
const StudentRecords = () => import('./views/StudentRecords.vue')
const TaskWorkspace = () => import('./views/TaskWorkspace.vue')
const AIConfigPanel = () => import('./views/AIConfigPanel.vue')

// 教师端
const TeacherLayout = () => import('./views/TeacherLayout.vue')
const TeacherDashboard = () => import('./views/TeacherDashboard.vue')
const KnowledgeManager = () => import('./views/KnowledgeManager.vue')
const StudentManagement = () => import('./views/StudentManagement.vue')
const FeedbackCenter = () => import('./views/FeedbackCenter.vue')

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginPage },

    // 学生路由组
    {
      path: '/student',
      component: StudentLayout,
      meta: { role: 'student' },
      children: [
        { path: '', component: CourseRoadmap },
        { path: 'task/:taskId', name: 'task-workspace', component: TaskWorkspace },
        { path: 'records', component: StudentRecords },
        { path: 'ai-config', component: AIConfigPanel },
      ],
    },

    // 教师路由组
    {
      path: '/teacher',
      component: TeacherLayout,
      meta: { role: 'teacher' },
      children: [
        { path: '', component: TeacherDashboard },
        { path: 'knowledge', component: KnowledgeManager },
        { path: 'students', component: StudentManagement },
        { path: 'feedback', component: FeedbackCenter },
        { path: 'ai-config', component: AIConfigPanel },
      ],
    },
  ],
})

// 路由守卫
router.beforeEach((to) => {
  const session = useSessionStore()

  // 登录页不需要守卫
  if (to.path === '/login') return true

  // 未登录 → 跳转登录页
  if (!session.currentUser) return '/login'

  // 角色不匹配 → 跳转到正确的首页
  const requiredRole = to.meta.role as string | undefined
  if (requiredRole && requiredRole !== session.currentUser.role) {
    return session.currentUser.role === 'teacher' ? '/teacher' : '/student'
  }

  return true
})
