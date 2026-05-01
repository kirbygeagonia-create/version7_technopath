<template>
  <div ref="container" class="tile-wipe-root" :class="{ 'tile-wipe-exit': active }">
    <div class="tile-wipe-tiles">
      <div
        v-for="tile in tiles"
        :key="tile.id"
        class="tile-wipe-col"
        :style="{ width: tile.width + 'px', left: tile.left + 'px', transitionDelay: tile.delay + 'ms' }"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  active:   { type: Boolean, default: false },
  minWidth: { type: Number,  default: 30 },
  color:    { type: String,  default: '#FF9800' },
})

const container = ref(null)
const containerWidth = ref(390)
let ro = null

onMounted(() => {
  if (container.value) containerWidth.value = container.value.offsetWidth
  ro = new ResizeObserver(([e]) => { containerWidth.value = e.contentRect.width })
  if (container.value) ro.observe(container.value)
})
onUnmounted(() => ro?.disconnect())

const tiles = computed(() => {
  const count = Math.max(5, Math.floor(containerWidth.value / props.minWidth))
  const w = containerWidth.value / count + 1
  const mid = Math.floor((count - 1) / 2)
  return Array.from({ length: count }, (_, i) => ({
    id: i, width: w, left: i * w,
    delay: Math.abs(i - mid) * 45,
  }))
})
</script>

<style scoped>
.tile-wipe-root {
  position: fixed; inset: 0;
  pointer-events: none; z-index: 9998; overflow: hidden;
}
.tile-wipe-tiles { position: relative; width: 100%; height: 100%; }
.tile-wipe-col {
  position: absolute; top: 0; height: 100%;
  background: v-bind(color);
  transform: translateY(0);
  transition: transform 0.55s cubic-bezier(0.45, 0, 0.55, 1);
}
.tile-wipe-exit .tile-wipe-col { transform: translateY(100%); }
</style>
