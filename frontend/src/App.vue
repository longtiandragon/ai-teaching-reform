<template>
  <div class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">Course Training Platform</p>
        <h1>SpringBoot 与农博项目实训平台</h1>
      </div>
      <nav class="role-tabs" aria-label="角色切换">
        <RouterLink to="/student">
          <BookOpen :size="18" />
          学生工作台
        </RouterLink>
        <RouterLink to="/student/records">
          <ClipboardList :size="18" />
          我的记录
        </RouterLink>
        <RouterLink to="/teacher">
          <BarChart3 :size="18" />
          教师看板
        </RouterLink>
      </nav>
      <label class="identity-switcher">
        <span>{{ session.currentUser?.role === 'teacher' ? '教师' : '学生' }}</span>
        <select :value="session.currentUser?.id" @change="switchIdentity">
          <optgroup label="学生">
            <option v-for="user in session.students" :key="user.id" :value="user.id">
              {{ user.student_no }} · {{ user.name }}
            </option>
          </optgroup>
          <optgroup label="教师">
            <option v-for="user in session.teachers" :key="user.id" :value="user.id">
              {{ user.name }}
            </option>
          </optgroup>
        </select>
      </label>
    </header>
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { BarChart3, BookOpen, ClipboardList } from 'lucide-vue-next'
import { useSessionStore } from './stores/session'

const session = useSessionStore()

onMounted(() => {
  session.load()
})

async function switchIdentity(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  if (value) await session.switchUser(value)
}
</script>
