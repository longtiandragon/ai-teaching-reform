<template>
  <div class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">AI Teaching Reform Demo</p>
        <h1>SpringBoot 与农博项目 AI 实训</h1>
      </div>
      <nav class="role-tabs" aria-label="角色切换">
        <RouterLink to="/student">
          <BookOpen :size="18" />
          学生工作台
        </RouterLink>
        <RouterLink to="/teacher">
          <BarChart3 :size="18" />
          教师看板
        </RouterLink>
      </nav>
    </header>
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { BarChart3, BookOpen } from 'lucide-vue-next'
</script>
