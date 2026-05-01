<template>
  <span role="status" class="bouncing-dots">
    <span v-for="i in dots" :key="i" class="bouncing-dot"
      :style="{ backgroundColor: color, animationDelay: `${(i-1) * 0.2}s` }" />
    <span class="sr-only">Typing…</span>
  </span>
</template>

<script setup>
defineProps({ dots: { type: Number, default: 3 }, color: { type: String, default: '#FF9800' } })
</script>

<style scoped>
.bouncing-dots { display: inline-flex; align-items: center; gap: 5px; }
.bouncing-dot {
  width: 8px; height: 8px; border-radius: 50%;
  animation: bdAnim 1.4s ease-in-out infinite;
}
@keyframes bdAnim {
  0%, 100% { transform: scale(0.8); opacity: 0.5; }
  50%       { transform: scale(1.2); opacity: 1;   }
}
</style>
