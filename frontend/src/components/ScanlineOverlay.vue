<template>
  <div class="scanline-overlay" aria-hidden="true"></div>
</template>

<style scoped>
.scanline-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 50;
  background:
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 3px,
      rgba(249, 115, 22, 0.03) 3px,
      rgba(249, 115, 22, 0.03) 4px
    );
  mix-blend-mode: multiply;
  overflow: hidden;
}

.scanline-overlay::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 3px,
    transparent 3px,
    transparent 4px
  );
  mask-image: repeating-linear-gradient(
    0deg,
    black 0px,
    black 3px,
    transparent 3px,
    transparent 4px
  );
  -webkit-mask-image: repeating-linear-gradient(
    0deg,
    black 0px,
    black 3px,
    transparent 3px,
    transparent 4px
  );
  background-image: linear-gradient(
    180deg,
    #FF6B6B10,
    #FF9D7610,
    #FFD16610,
    #7DD3A810,
    #7C8CF810,
    #C4A1FF10,
    #FF6B6B10
  );
  background-size: 100% 400%;
  animation: rainbowFlow 8s linear infinite;
}

@keyframes rainbowFlow {
  0% { background-position: 0% 0%; }
  100% { background-position: 0% 400%; }
}
</style>
