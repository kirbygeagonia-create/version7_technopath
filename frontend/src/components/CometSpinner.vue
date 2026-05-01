<template>
  <span role="status" aria-label="Loading" class="comet-spinner" :style="{ width: size, height: size }">
    <span class="comet-inner" />
    <span class="sr-only">Loading</span>
  </span>
</template>

<script setup>
defineProps({ size: { type: String, default: '40px' } })
</script>

<style scoped>
.comet-spinner {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  container-type: size;
}
.comet-inner {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  animation: cometShadow 1.7s infinite ease, cometRotate 1.7s infinite ease;
}
@keyframes cometShadow {
  0%, 5%, 95%, 100% {
    box-shadow:
      0 -83cqmin 0 -40cqmin #FF9800,
      0 -83cqmin 0 -41cqmin #FF9800,
      0 -83cqmin 0 -42cqmin rgba(255,152,0,0.6),
      0 -83cqmin 0 -43cqmin rgba(255,152,0,0.3),
      0 -83cqmin 0 -44cqmin rgba(255,152,0,0.1);
  }
  38% {
    box-shadow:
      0 -83cqmin 0 -40cqmin #FF9800,
      calc(83cqmin * -0.454) calc(83cqmin * -0.892) 0 -41cqmin #FF9800,
      calc(83cqmin * -0.777) calc(83cqmin * -0.629) 0 -42cqmin rgba(255,152,0,0.6),
      calc(83cqmin * -0.934) calc(83cqmin * -0.358) 0 -43cqmin rgba(255,152,0,0.3),
      calc(83cqmin * -0.988) calc(83cqmin * -0.108) 0 -44cqmin rgba(255,152,0,0.1);
  }
}
@keyframes cometRotate {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
</style>
