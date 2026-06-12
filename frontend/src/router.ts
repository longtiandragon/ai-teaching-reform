import { createRouter, createWebHistory } from 'vue-router'

const StudentWorkspace = () => import('./views/StudentWorkspace.vue')
const TeacherDashboard = () => import('./views/TeacherDashboard.vue')

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/student' },
    { path: '/student', component: StudentWorkspace },
    { path: '/teacher', component: TeacherDashboard },
  ],
})
