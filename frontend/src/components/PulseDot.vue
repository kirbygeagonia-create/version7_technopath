<template>
  <span role="status" class="pulse-dot"
    :style="{ width: size, height: size, backgroundColor: color }">
    <span class="sr-only">{{ label }}</span>
  </span>
</template>

<script setup>
defineProps({
  size:  { type: String, default: '10px' },
  color: { type: String, default: '#4CAF50' },
  label: { type: String, default: 'Active' },
})
</script>

<style scoped>
.pulse-dot {
  display: inline-block; border-radius: 50%;
  animation: pdAnim 1.2s ease-in-out infinite;
}
@keyframes pdAnim {
  0%, 100% { transform: scale(1);   opacity: 0.8; }
  50%       { transform: scale(1.5); opacity: 1;   }
}
</style>
