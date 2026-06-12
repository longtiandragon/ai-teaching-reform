import { createRouter, createWebHistory } from 'vue-router'
import login from '../login.vue'
import Main from '../components/Main.vue'
import Konwladge from '../components/views/Konwladge.vue'
import SystemManagement from '../components/views/SystemManagement.vue'

const routesObj = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'login',
    component: login
  },
  {
    path: '/main',
    name: 'Main',
    component: Main,
    redirect: '/main/konwladge/index',
    children: [
      {
        path: 'konwladge/index',
        name: 'konwladge',
        component: Konwladge
      },
      {
        path: 'system',
        name: 'system',
        component: SystemManagement
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: routesObj
})

router.beforeEach((to, from, next) => {
  if (to.path === '/login') {
    next()
    return
  }

  if (localStorage.getItem('user') !== null) {
    next()
    return
  }

  next('/login')
})

export default router
