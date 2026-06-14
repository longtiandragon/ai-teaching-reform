import { defineStore } from 'pinia'
import { api, type ClassInfo, type UserInfo } from '../api'

const STORAGE_KEY = 'web-training-current-user-id'

export const useSessionStore = defineStore('session', {
  state: () => ({
    users: [] as UserInfo[],
    classes: [] as ClassInfo[],
    currentUser: null as UserInfo | null,
    loading: false,
  }),
  getters: {
    students: (state) => state.users.filter((user) => user.role === 'student'),
    teachers: (state) => state.users.filter((user) => user.role === 'teacher'),
    isStudent: (state) => state.currentUser?.role === 'student',
    isTeacher: (state) => state.currentUser?.role === 'teacher',
  },
  actions: {
    async load() {
      this.loading = true
      try {
        const data = await api.sessionBootstrap()
        this.users = data.users
        this.classes = data.classes
      } finally {
        this.loading = false
      }
    },
    async login(userId: string) {
      this.currentUser = await api.login(userId)
      localStorage.setItem(STORAGE_KEY, userId)
    },
    async restoreSession() {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved && this.users.length) {
        const user = this.users.find((u) => u.id === saved)
        if (user) {
          this.currentUser = await api.login(user.id)
          return true
        }
      }
      return false
    },
    logout() {
      this.currentUser = null
      localStorage.removeItem(STORAGE_KEY)
    },
  },
})
