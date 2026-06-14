<template>
  <RouterView />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from './stores/session'

const router = useRouter()
const session = useSessionStore()

onMounted(async () => {
  await session.load()
  const restored = await session.restoreSession()
  if (restored && router.currentRoute.value.path === '/login') {
    const target = session.currentUser?.role === 'teacher' ? '/teacher' : '/student'
    router.push(target)
  }
})
</script>
