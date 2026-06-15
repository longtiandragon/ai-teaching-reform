import { defineStore } from 'pinia'
import { api, type ClassInfo, type UserInfo } from '../api'

const STORAGE_KEY = 'web-training-current-user-id'
const TOKEN_KEY = 'web-training-access-token'

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
    async login(account: string, password: string) {
      const result = await api.login(account, password)
      this.currentUser = result.user
      localStorage.setItem(STORAGE_KEY, result.user.id)
      localStorage.setItem(TOKEN_KEY, result.access_token)
    },
    async restoreSession() {
      const saved = localStorage.getItem(STORAGE_KEY)
      const token = localStorage.getItem(TOKEN_KEY)
      if (saved && this.users.length) {
        const user = this.users.find((u) => u.id === saved)
        if (user && token) {
          this.currentUser = user
          return true
        }
      }
      return false
    },
    logout() {
      this.currentUser = null
      localStorage.removeItem(STORAGE_KEY)
      localStorage.removeItem(TOKEN_KEY)
    },
  },
})
