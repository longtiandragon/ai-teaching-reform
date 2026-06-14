<template>
  <Teleport to="body">
    <div v-if="active" class="border-light-flow" aria-hidden="true">
      <svg class="flow-svg" viewBox="0 0 1000 1000" preserveAspectRatio="none">
        <defs>
          <!-- 水平渐变 -->
          <linearGradient id="grad-h-cw" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#D97706" stop-opacity="0" />
            <stop offset="20%" stop-color="#F59E0B" stop-opacity="1" />
            <stop offset="50%" stop-color="#FDE68A" stop-opacity="1" />
            <stop offset="80%" stop-color="#F59E0B" stop-opacity="1" />
            <stop offset="100%" stop-color="#D97706" stop-opacity="0" />
          </linearGradient>
          <linearGradient id="grad-h-ccw" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#FCD34D" stop-opacity="0" />
            <stop offset="20%" stop-color="#FDE68A" stop-opacity="1" />
            <stop offset="50%" stop-color="#FEF3C7" stop-opacity="1" />
            <stop offset="80%" stop-color="#FDE68A" stop-opacity="1" />
            <stop offset="100%" stop-color="#FCD34D" stop-opacity="0" />
          </linearGradient>
          <!-- 垂直渐变 -->
          <linearGradient id="grad-v" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#D97706" stop-opacity="0" />
            <stop offset="20%" stop-color="#F59E0B" stop-opacity="1" />
            <stop offset="50%" stop-color="#FDE68A" stop-opacity="1" />
            <stop offset="80%" stop-color="#F59E0B" stop-opacity="1" />
            <stop offset="100%" stop-color="#D97706" stop-opacity="0" />
          </linearGradient>
          <linearGradient id="grad-v2" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#FCD34D" stop-opacity="0" />
            <stop offset="20%" stop-color="#FDE68A" stop-opacity="1" />
            <stop offset="50%" stop-color="#FEF3C7" stop-opacity="1" />
            <stop offset="80%" stop-color="#FDE68A" stop-opacity="1" />
            <stop offset="100%" stop-color="#FCD34D" stop-opacity="0" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <!-- 顺时针：顶部中心→右边→底部→左边→顶部 -->
        <path
          class="stream cw"
          d="M 500 2 L 998 2 L 998 998 L 2 998 L 2 2 L 500 2"
          fill="none"
          stroke="url(#grad-h-cw)"
          stroke-width="5"
          stroke-linecap="round"
          filter="url(#glow)"
        />
        <!-- 逆时针：顶部中心→左边→底部→右边→顶部 -->
        <path
          class="stream ccw"
          d="M 500 2 L 2 2 L 2 998 L 998 998 L 998 2 L 500 2"
          fill="none"
          stroke="url(#grad-h-ccw)"
          stroke-width="5"
          stroke-linecap="round"
          filter="url(#glow)"
        />

        <!-- 左侧光流：从上到下，双线 -->
        <line
          class="stream left-down"
          x1="3" y1="0" x2="3" y2="1000"
          stroke="url(#grad-v)"
          stroke-width="8"
          stroke-linecap="round"
          filter="url(#glow)"
        />
        <line
          class="stream left-down delay"
          x1="3" y1="0" x2="3" y2="1000"
          stroke="#FDE68A"
          stroke-width="4"
          stroke-linecap="round"
          opacity="0.6"
        />
        <!-- 右侧光流：从下到上，双线 -->
        <line
          class="stream right-up"
          x1="997" y1="1000" x2="997" y2="0"
          stroke="url(#grad-v2)"
          stroke-width="8"
          stroke-linecap="round"
          filter="url(#glow)"
        />
        <line
          class="stream right-up delay"
          x1="997" y1="1000" x2="997" y2="0"
          stroke="#FDE68A"
          stroke-width="4"
          stroke-linecap="round"
          opacity="0.6"
        />
      </svg>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const active = ref(false)

function trigger() {
  active.value = true
  setTimeout(() => {
    active.value = false
  }, 1800)
}

defineExpose({ trigger })
</script>

<style scoped>
.border-light-flow {
  position: fixed;
  inset: 0;
  z-index: 9998;
  pointer-events: none;
}

.flow-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.stream {
  stroke-dasharray: 2000;
  stroke-dashoffset: 2000;
}

/* 顺时针绕边框 */
.cw {
  animation: flow-forward 1.5s cubic-bezier(0.25, 0.1, 0.25, 1) forwards;
}

/* 逆时针绕边框 */
.ccw {
  animation: flow-forward 1.5s cubic-bezier(0.25, 0.1, 0.25, 1) 0.1s forwards;
}

/* 左侧从上到下 */
.left-down {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: flow-side 1.2s cubic-bezier(0.25, 0.1, 0.25, 1) 0.2s forwards;
}

.left-down.delay {
  animation: flow-side 1.2s cubic-bezier(0.25, 0.1, 0.25, 1) 0.35s forwards;
}

/* 右侧从下到上 */
.right-up {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: flow-side 1.2s cubic-bezier(0.25, 0.1, 0.25, 1) 0.3s forwards;
}

.right-up.delay {
  animation: flow-side 1.2s cubic-bezier(0.25, 0.1, 0.25, 1) 0.45s forwards;
}

@keyframes flow-forward {
  0% {
    stroke-dashoffset: 2000;
    opacity: 0;
  }
  3% {
    opacity: 1;
  }
  80% {
    opacity: 1;
  }
  100% {
    stroke-dashoffset: 0;
    opacity: 0;
  }
}

@keyframes flow-side {
  0% {
    stroke-dashoffset: 1000;
    opacity: 0;
  }
  5% {
    opacity: 1;
  }
  80% {
    opacity: 1;
  }
  100% {
    stroke-dashoffset: 0;
    opacity: 0;
  }
}
</style>
