import { createRouter, createWebHistory } from 'vue-router'

const CourseRoadmap = () => import('./views/CourseRoadmap.vue')
const StudentRecords = () => import('./views/StudentRecords.vue')
const StudentWorkspace = () => import('./views/StudentWorkspace.vue')
const TeacherDashboard = () => import('./views/TeacherDashboard.vue')

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/student' },
    { path: '/student', component: CourseRoadmap },
    { path: '/student/records', component: StudentRecords },
    { path: '/student/learn/:lessonId?', name: 'student-learn', component: StudentWorkspace },
    { path: '/teacher', component: TeacherDashboard },
  ],
})
