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
        const saved = localStorage.getItem(STORAGE_KEY)
        const candidate = this.users.find((user) => user.id === saved) || this.users.find((user) => user.role === 'student') || this.users[0]
        if (candidate) {
          this.currentUser = await api.login(candidate.id)
          localStorage.setItem(STORAGE_KEY, this.currentUser.id)
        }
      } finally {
        this.loading = false
      }
    },
    async switchUser(userId: string) {
      this.currentUser = await api.login(userId)
      localStorage.setItem(STORAGE_KEY, userId)
    },
  },
})
