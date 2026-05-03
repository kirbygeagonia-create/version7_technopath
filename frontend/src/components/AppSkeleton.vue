<template>
  <div class="skeleton-wrapper" :class="wrapClass">
    <div v-if="loading" class="skeleton-loader" :class="[animate, { dark }]">
      <div class="skeleton-bone" v-for="i in 5" :key="i" :style="{ animationDelay: `${(i-1) * 100}ms` }"></div>
    </div>
    <slot v-else />
  </div>
</template>

<script setup>
defineProps({
  loading:   { type: Boolean, required: true },
  name:      { type: String,  default: undefined },
  animate:   { type: String,  default: 'shimmer' },
  wrapClass: { type: String,  default: '' },
  dark:      { type: Boolean, default: false },
})

defineOptions({
  inheritAttrs: false
})
</script>

<style scoped>
.skeleton-loader {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
}

.skeleton-bone {
  height: 72px;
  background: #e6e6e6;
  border-radius: 12px;
  animation: shimmer 1.5s infinite;
}

.skeleton-loader.dark .skeleton-bone {
  background: #252525;
}

@keyframes shimmer {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.skeleton-loader.pulse .skeleton-bone {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.02); opacity: 1; }
}
</style>
