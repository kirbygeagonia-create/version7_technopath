<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <Transition name="overlay-fade">
      <div
        v-if="modelValue"
        class="bso-backdrop"
        @click="$emit('update:modelValue', false)"
      >
        <Transition name="overlay-slide">
          <div
            v-if="modelValue"
            class="bso-sheet"
            :style="{ maxHeight: maxHeight }"
            @click.stop
          >
            <!-- Drag Handle -->
            <div class="bso-handle-bar" @click="$emit('update:modelValue', false)">
              <div class="bso-handle"></div>
            </div>
            <!-- Dynamic Content Slot -->
            <slot />
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, required: true },
  maxHeight:  { type: String,  default: '85vh' },
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.bso-backdrop {
  position: fixed;
  inset: 0;
  z-index: 500;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: flex-end;
}

.bso-sheet {
  width: 100%;
  background: var(--color-bg, #ffffff);
  border-radius: 28px 28px 0 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 -8px 40px rgba(0, 0, 0, 0.18);
}

.bso-handle-bar {
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  padding: 12px 0 4px;
  cursor: pointer;
}

.bso-handle {
  width: 40px;
  height: 4px;
  background: var(--color-border, #e0e0e0);
  border-radius: 99px;
}

/* Transitions */
.overlay-fade-enter-active,
.overlay-fade-leave-active { transition: opacity 0.25s ease; }
.overlay-fade-enter-from,
.overlay-fade-leave-to    { opacity: 0; }

.overlay-slide-enter-active,
.overlay-slide-leave-active { transition: transform 0.32s cubic-bezier(0.32, 0.72, 0, 1); }
.overlay-slide-enter-from,
.overlay-slide-leave-to    { transform: translateY(100%); }
</style>
