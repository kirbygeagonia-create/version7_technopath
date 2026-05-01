<template>
  <Skeleton
    :loading="loading"
    :name="name"
    :animate="animate"
    :transition="220"
    :stagger="55"
    :color="skColor"
    dark-color="#252525"
    :class="wrapClass"
  >
    <slot />
  </Skeleton>
</template>

<script setup>
import { Skeleton } from 'boneyard-js'
import { computed } from 'vue'

const props = defineProps({
  loading:   { type: Boolean, required: true },
  name:      { type: String,  default: undefined },
  animate:   { type: String,  default: 'shimmer' },
  wrapClass: { type: String,  default: '' },
  dark:      { type: Boolean, default: false },
})

const skColor = computed(() => props.dark ? '#252525' : '#e6e6e6')
</script>
