<template>
  <div class="navigate-view">
    <header class="navigate-top-bar">
      <button class="navigate-back-btn" @click="goBack">
        <span class="material-icons">arrow_back</span>
      </button>
      <h1>Navigate</h1>
      <div class="navigate-spacer"></div>
    </header>

    <div class="navigate-main-content">
      <div class="navigate-panel">
        <div class="navigate-input-group">
          <label>From</label>
          <select v-model="fromLocation">
            <option value="">Select starting point</option>
            <option v-for="node in nodes" :key="node.id" :value="node.id">
              {{ node.name }}
            </option>
          </select>
        </div>

        <div class="navigate-input-group">
          <label>To</label>
          <select v-model="toLocation">
            <option value="">Select destination</option>
            <option v-for="node in nodes" :key="node.id" :value="node.id">
              {{ node.name }}
            </option>
          </select>
        </div>

        <button class="navigate-btn-primary" @click="findRoute" :disabled="!fromLocation || !toLocation">
          Find Route
        </button>

        <div v-if="route" class="navigate-route-result">
          <p>Distance: {{ route.distance }} units</p>
          <p>Steps: {{ route.path.length }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import db from '../services/db.js'
import { dijkstra } from '../services/pathfinder.js'

const router = useRouter()
const nodes = ref([])
const edges = ref([])
const fromLocation = ref('')
const toLocation = ref('')
const route = ref(null)

const goBack = () => router.back()

onMounted(async () => {
  nodes.value = await db.navigation_nodes.toArray()
  edges.value = await db.navigation_edges.toArray()
})

function findRoute() {
  if (!fromLocation.value || !toLocation.value) return
  
  const result = dijkstra(
    nodes.value,
    edges.value,
    parseInt(fromLocation.value),
    parseInt(toLocation.value)
  )
  
  route.value = result
}
</script>

<style>
/* Styles moved to external file: src/assets/navigate.css */
@import '../assets/navigate.css';
</style>
